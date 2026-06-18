<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/or32_ksyms.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/or32_ksyms.c

## Purpose
Exports OpenRISC compiler helper routines and architecture usercopy/string helpers to modules.

## Important APIs, Types, And Functions
Exports libgcc-style helpers `__udivsi3`, `__divsi3`, `__umodsi3`, `__modsi3`, `__muldi3`, `__ashrdi3`, `__ashldi3`, `__lshrdi3`, `__ucmpdi2`, plus `__copy_tofrom_user`, `__clear_user`, and `memset`.

## Control Flow
No runtime control flow beyond export declarations.

## State And Persistence
No state.

## Dependencies And Integration Points
Supports modules compiled with helper calls not inlined by the compiler and modules needing exported usercopy/string routines.

## Risks
Missing exports cause module link/load failures. Exporting low-level helpers expands module ABI surface.

## Test Signals
External module builds using division, 64-bit arithmetic, memset, and usercopy helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/or32_ksyms.c -->
