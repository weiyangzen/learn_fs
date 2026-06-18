
# sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow2-memcmp.c

## Purpose

This companion `memcmp()` test validates overflow detection on the second source argument.

## Important APIs, Control Flow, And State

`TEST` is `memcmp(large, small, sizeof(small) + 1)`. The large first operand is valid for the length, while the second operand is too short, ensuring the fortify check covers both input pointers.

## Dependencies, Risks, And Test Signals

It depends on compiler-visible sizes for both arrays and the fortify `memcmp()` implementation. The expected build signal is `__read_overflow2`, matching the filename prefix.
