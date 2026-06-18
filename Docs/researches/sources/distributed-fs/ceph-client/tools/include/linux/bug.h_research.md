# sources/distributed-fs/ceph-client/tools/include/linux/bug.h

## Purpose

This minimal header provides a `BUILD_BUG_ON_ZERO` expression helper for tools/perf-style code.

## APIs, State, and Dependencies

`BUILD_BUG_ON_ZERO(e)` uses a negative-width bitfield in `sizeof` to force a compilation error when `e` is true while evaluating to zero otherwise. It has no state or dependencies.

## Risks and Test Signals

The macro is compile-time only and may conflict semantically with the richer `linux/build_bug.h` variant. Tests should compile users that place it in constant-expression contexts and verify true conditions fail compilation.
