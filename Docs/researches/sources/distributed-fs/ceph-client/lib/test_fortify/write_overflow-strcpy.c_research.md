
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-strcpy.c

## Purpose

This test checks `strcpy()` destination overflow when the source is a fixed large array instead of a literal at the call site.

## Important APIs, Control Flow, And State

`TEST` is `strcpy(small, large_src)`. The shared header declares `large_src` with a large literal initializer and `small` as a 16-byte destination.

## Dependencies, Risks, And Test Signals

It depends on fortified string object-size analysis for arrays. The expected result is `__write_overflow`; a clean compile would indicate a regression in non-literal `strcpy()` checking.
