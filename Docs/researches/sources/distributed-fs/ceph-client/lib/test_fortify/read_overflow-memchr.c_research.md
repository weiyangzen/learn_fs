
# sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow-memchr.c

## Purpose

This compile-time fortify test verifies detection of a read overflow in `memchr()`.

## Important APIs, Control Flow, And State

The file defines `TEST` as `memchr(small, 0x7A, sizeof(small) + 1)` and includes `test_fortify.h`, whose `do_fortify_tests()` initializes shared buffers and expands `TEST`. The state is the common `small` array; the one-byte oversized length is intended to trigger the `__read_overflow` fortify path.

## Dependencies, Risks, And Test Signals

It depends on compiler object-size analysis and the shared harness. The expected signal is a build failure warning or unresolved symbol matching the filename-derived `__read_overflow`; successful compilation without that symbol is a failed test.
