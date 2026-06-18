
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-strncpy.c

## Purpose

This file tests `strncpy()` overflow into a struct field destination.

## Important APIs, Control Flow, And State

`TEST` is `strncpy(instance.buf, large_src, sizeof(instance.buf) + 1)`. The explicit copy count exceeds the size of `instance.buf`.

## Dependencies, Risks, And Test Signals

The test relies on fortify distinguishing the field destination from the surrounding struct. The expected output confirms `__write_overflow` detection.
