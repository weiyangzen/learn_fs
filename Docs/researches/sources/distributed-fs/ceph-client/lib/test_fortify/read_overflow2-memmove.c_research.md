
# sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow2-memmove.c

## Purpose

This is the `memmove()` equivalent of the source-side fortify overflow test.

## Important APIs, Control Flow, And State

`TEST` expands to `memmove(large, instance.buf, sizeof(large))`. The source field is smaller than the copy length, while the destination is large enough, isolating read overflow behavior.

## Dependencies, Risks, And Test Signals

It depends on the `memmove()` fortify wrapper and compile-time struct field sizing. The expected output is an `ok:` log for `__read_overflow2` detection.
