# sources/distributed-fs/ceph-client/tools/include/linux/args.h

## Purpose

This header provides small variadic macro utilities for counting arguments and concatenating tokens in tools builds.

## APIs, State, and Dependencies

`COUNT_ARGS` counts up to 15 variadic arguments, returning the 16th slot for larger lists. `__CONCAT` and `CONCATENATE` paste tokens while allowing macro expansion. There is no state or runtime behavior.

## Risks and Test Signals

Argument counting is macro-sensitive and bounded. Empty argument behavior depends on the `, ##X` extension. Tests should compile macro users with zero, one, many, and over-limit arguments under GCC and Clang.
