# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/vmx_asm.h

## Purpose
Assembly macros for saving/restoring and loading VMX/Altivec registers.

## Important APIs, Types, and Functions
Defines `PUSH_VMX`, `POP_VMX`, and `load_vmx` helper patterns for vector registers.

## Control Flow
Macros expand to vector store/load sequences around assembly tests.

## State and Persistence
State is caller stack save area and VMX register contents.

## Dependencies and Integration Points
Depends on `basic_asm.h` and is used by VMX math/preempt/signal tests.

## Risks and Test Signals
Risk is register corruption or requiring Altivec support. VMX tests catch mismatches or skip unsupported hardware.
