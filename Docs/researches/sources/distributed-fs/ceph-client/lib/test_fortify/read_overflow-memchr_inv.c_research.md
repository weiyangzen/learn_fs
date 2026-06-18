
# sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow-memchr_inv.c

## Purpose

This negative build test checks fortify handling for an oversized `memchr_inv()` read from a known small object.

## Important APIs, Control Flow, And State

`TEST` expands to `memchr_inv(small, 0x7A, sizeof(small) + 1)`. The shared header initializes `small` and compiles the expression inside `do_fortify_tests()`. No runtime execution is expected; the compiler must diagnose the read size.

## Dependencies, Risks, And Test Signals

The test depends on the fortify implementation for `memchr_inv()` and compiler size knowledge for fixed arrays. The expected build artifact is a log confirming `__read_overflow` detection.
