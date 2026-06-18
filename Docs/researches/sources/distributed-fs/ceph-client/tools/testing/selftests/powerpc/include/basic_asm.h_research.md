# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/basic_asm.h

## Purpose
Shared PowerPC assembly macros for stack frames, load/store word size selection, immediates, and basic prologue/epilogue handling.

## Important APIs, Types, and Functions
Defines `PPC_LL`, `PPC_STL`, `PPC_STLU`, `LOAD_REG_IMMEDIATE`, ABI-specific `STACK_FRAME_*` offsets, `STACK_FRAME_PARAM`, `STACK_FRAME_LOCAL`, `PUSH_BASIC_STACK`, and `POP_BASIC_STACK`.

## Control Flow
No standalone flow; macros expand into assembly used by math/register tests.

## State and Persistence
No runtime state except generated stack frame layout in callers.

## Dependencies and Integration Points
Depends on `<ppc-asm.h>` and `<asm/unistd.h>`. Included by FPU/VMX/VSX assembly helpers.

## Risks and Test Signals
Risk is ABI offset mismatch between 32/64-bit or ELFv1/v2 conventions. Assembly tests expose broken save/restore or syscall frame handling.
