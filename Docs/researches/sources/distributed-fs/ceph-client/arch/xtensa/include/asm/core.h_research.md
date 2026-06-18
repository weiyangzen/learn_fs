<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/core.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/core.h

## Purpose
Normalizes Xtensa variant core feature macros and derives ABI/support constants used throughout architecture code.

## Important APIs, Types, And Functions
Defines defaults for `XCHAL_HAVE_DIV32`, `XCHAL_HAVE_EXCLUSIVE`, `XCHAL_HAVE_EXTERN_REGS`, `XCHAL_HAVE_MPU`, `XCHAL_HAVE_VECBASE`, `XCHAL_SPANNING_WAY`, `XCHAL_HAVE_TRAX`, and `XCHAL_NUM_PERF_COUNTERS`; derives `USER_SUPPORT_WINDOWED`, `SUPPORT_WINDOWED`, `XTENSA_STACK_ALIGNMENT`, and `XCHAL_HW_MIN_VERSION`.

## Control Flow
No executable control; preprocessor logic converts variant capabilities and Kconfig ABI choices into common macros.

## State And Persistence
No runtime state. Constants persist in compiled code.

## Dependencies And Integration Points
Depends on `<variant/core.h>` and is included by most Xtensa low-level headers.

## Risks And Edge Cases
Incorrect defaults can silently compile unsupported code paths. ABI support macros must match Kconfig and compiler ABI. Stack alignment must satisfy Xtensa ABI and data width.

## Test Signals
Compile many variant headers, especially custom variants lacking newer `XCHAL_*` definitions, and boot both windowed and call0 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/core.h -->
