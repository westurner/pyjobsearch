#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function
"""
jobterms
"""
import BeautifulSoup
import itertools
import nltk
import nltk.util
from collections import OrderedDict

def mine_strings(fileobj):
    """extract relevant portions of Python Job Board listings"""
    d = BeautifulSoup.BeautifulSoup(fileobj)
    content = d.find('div',attrs={'id':'content'})
    paragraphs = (
        (p.text)
            for p in content.findAll('p')
                if getattr(getattr(p,'next',None),'name',None)
                    not in ('strong','em'))

    lists = (
        (s.parent.parent.parent.findNext('ul').findAll('li'))
            for s in content.findAll('strong',text='Requirements'))
    lists = (li.text for ul in lists for li in ul)

    text = itertools.chain(paragraphs, lists)
    for line in text:
        yield line


STOPWORDS = dict((w,None) for w in nltk.corpus.stopwords.words('english'))
STOPWORDS.update((p,None) for p in ',-!.()[]:/;%\'&')
STOPWORDS["'s"] = None
STOPWORDS["'re"] = None

class DistSet(object):
    FREQDISTS = OrderedDict((
        ('1-word', (nltk.FreqDist,
            lambda dist,words: dist.update((w,) for w in words))),
        ('2-word', (nltk.FreqDist,
            lambda dist,words: dist.update(nltk.util.ingrams(words, 2)))
            ),
        ('3-word', (nltk.FreqDist,
            lambda dist,words: dist.update(nltk.util.ingrams(words, 3)))
            ),
        ('4-word', (nltk.FreqDist,
            lambda dist,words: dist.update(nltk.util.ingrams(words, 4)))
            ),
        ('5-word', (nltk.FreqDist,
            lambda dist,words: dist.update(nltk.util.ingrams(words, 5)))
            ),
    ))
    def __init__(self, distset=('1-word',)):
        self.distset = distset
        self.freqdists = {}
        for dist in distset:
            (cls,func) = DistSet.FREQDISTS[dist]
            self.freqdists[dist] = cls()

    def process(self, words):
        for distname in self.distset:
            cls, func = DistSet.FREQDISTS[distname]
            dist = self.freqdists[distname]
            func(dist, words)

    def print_dists(self, frequency_threshold=0):
        for name, fd in self.freqdists.iteritems():
            print('#'*79)
            print(name)
            print('#'*79)
            for (k,v) in sorted(fd.iteritems(), key=lambda x: x[1]):
                if v > frequency_threshold:
                    print("%4d %s" % (v,u' '.join(k)))


def super_tokenize(sent, stemmer):
    words = (stemmer.stem(w.lower()) for w in nltk.word_tokenize(sent))
    for w in words:
        if w not in STOPWORDS:
            yield w


def jobterms():
    dists = DistSet()
    stemmer = nltk.stem.PorterStemmer()
    with open('./Python Job Board.html') as fileobj:
        for block in mine_strings(fileobj):
            for sent in nltk.sent_tokenize(block):
                words = list(super_tokenize(sent, stemmer))
                dists.process(words)
    dists.print_dists()


import unittest
class Test_jobterms(unittest.TestCase):
    def test_jobterms(self):
        jobterms()


def main():
    import optparse
    import logging

    prs = optparse.OptionParser(usage="./%prog : args")

    prs.add_option('-v', '--verbose',
                    dest='verbose',
                    action='store_true',)
    prs.add_option('-q', '--quiet',
                    dest='quiet',
                    action='store_true',)
    prs.add_option('-t', '--test',
                    dest='run_tests',
                    action='store_true',)

    (opts, args) = prs.parse_args()

    if not opts.quiet:
        logging.basicConfig()

        if opts.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

    if opts.run_tests:
        import sys
        sys.argv = [sys.argv[0]] + args
        import unittest
        exit(unittest.main())

    jobterms()

if __name__ == "__main__":
    main()


