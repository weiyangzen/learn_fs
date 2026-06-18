
# sources/distributed-fs/ceph-client/lib/test_fpu.h

## Purpose

This header declares the architecture-neutral entry point for the kernel FPU selftest implementation.

## Important APIs, Control Flow, And State

It exports only `int test_fpu(void);` behind an include guard. It has no state and no inline logic.

## Dependencies, Risks, And Test Signals

`test_fpu_glue.c` calls this function inside `kernel_fpu_begin()`/`kernel_fpu_end()`, while `test_fpu_impl.c` defines it. The main risk is declaration/definition mismatch if the implementation changes its ABI.
