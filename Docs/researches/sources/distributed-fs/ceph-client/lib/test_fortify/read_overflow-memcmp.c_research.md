
# sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow-memcmp.c

## Purpose

This file validates that fortify detects a source read past the end of the first argument to `memcmp()`.

## Important APIs, Control Flow, And State

`TEST` is `memcmp(small, large, sizeof(small) + 1)`. `small` has 16 bytes and `large` has 32 bytes in the common harness, so the first operand cannot legally satisfy the requested compare length.

## Dependencies, Risks, And Test Signals

It exercises the `memcmp()` fortify wrapper. The log should show `__read_overflow` detection; missing detection would indicate a regression in bidirectional object-size checking for compare operations.
