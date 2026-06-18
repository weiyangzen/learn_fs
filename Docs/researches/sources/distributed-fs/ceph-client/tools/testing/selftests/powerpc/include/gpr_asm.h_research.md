# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/gpr_asm.h

## Purpose
Assembly helper macros for saving/restoring nonvolatile general purpose registers.

## Important APIs, Types, and Functions
Defines `__PUSH_NVREGS`, `__POP_NVREGS`, public push/pop variants, and `load_gpr` declaration/body macro support.

## Control Flow
Macros emit stores/loads for r14-r31 at stack offsets, including variants below FPU save areas.

## State and Persistence
State is stack save area and GPR contents.

## Dependencies and Integration Points
Depends on `basic_asm.h`. Used by register preservation and transactional-memory style tests.

## Risks and Test Signals
Risk is ABI register preservation breakage; tests using load/store GPR helpers expose corruption.
