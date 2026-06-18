
# sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow-memscan.c

## Purpose

This test checks read-overflow diagnostics for `memscan()` over a fixed small buffer.

## Important APIs, Control Flow, And State

`TEST` expands to `memscan(small, 0x7A, sizeof(small) + 1)`. The shared header provides the initialized `small` buffer and compiles the expression inside `do_fortify_tests()`.

## Dependencies, Risks, And Test Signals

The target integration point is the fortified `memscan()` wrapper. The expected signal is detection of the filename-derived `__read_overflow`; a clean object without that symbol is a test failure.
