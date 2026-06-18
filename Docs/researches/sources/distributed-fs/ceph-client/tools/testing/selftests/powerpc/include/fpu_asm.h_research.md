# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/fpu_asm.h

## Purpose
Assembly helper macros for preserving and loading nonvolatile FPU registers.

## Important APIs, Types, and Functions
Defines `PUSH_FPU`, `POP_FPU`, and declares/implements `load_fpu` macro entry behavior for f14-f31 style register setup.

## Control Flow
Macros save FPU registers to stack-relative slots and restore them around test assembly bodies.

## State and Persistence
State is caller stack storage and FPU register contents.

## Dependencies and Integration Points
Depends on `basic_asm.h` stack layout. Used by `math/fpu_asm.S`.

## Risks and Test Signals
Risk is corrupting nonvolatile FPU registers or stack offsets. FPU syscall/preempt/signal tests catch mismatches.
