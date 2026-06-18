
# sources/distributed-fs/ceph-client/lib/test_fpu_impl.c

## Purpose

This file implements the actual floating-point arithmetic check used by the FPU selftest glue.

## Important APIs, Types, And Functions

`test_fpu()` uses volatile `double` variables to prevent optimization away of arithmetic. It checks precision/rounding by adding tiny values to `4.0`, tests denormal and large intermediate values with `1e-310`, and returns `0` only if all expected comparisons are true.

## Control Flow And State

The function has no persistent state. It runs a fixed arithmetic sequence and returns `-EINVAL` on unexpected rounding or denormal handling.

## Dependencies And Integration Points

It includes errno and the local header. It must be called only from a context that has enabled kernel FPU usage, which `test_fpu_glue.c` supplies.

## Risks And Test Signals

The test assumes IEEE-like double semantics, nearest rounding, and denormal support. A return of `0` is success; `-EINVAL` indicates FPU state or compiler/runtime behavior did not match the kernel FPU contract.
