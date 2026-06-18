# sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpa11.h

## Purpose
Defines the FPA11 emulator state model, register representation, type tags, rounding data, and public emulator entry points.

## Important APIs, Types, And Functions
Defines `GET_FPA11()`, `GET_USERREG()`, `struct roundingData`, type tags `typeNone`, `typeSingle`, `typeDouble`, `typeExtended`, union `FPREG`, and packed struct `FPA11`. Declares initialization, dispatch, CPDT/CPDO/CPRT, precision-specific CPDO, and transfer helpers.

## Control Flow
No runtime control flow. The macros compute current-thread FPA state and saved user register access; functions declared here are implemented across the NWFPE sources.

## State, Dependencies, And Integration
`FPA11` is exported to user space through the ARM user FP state ABI and must match `struct user_fp`. Its layout contains eight 12-byte FP registers, FPSR, FPCR, eight type tags, and `initflag`. Dependencies include `linux/thread_info.h`, `fpsr.h`, `milieu.h`, and `softfloat.h`.

## Risks And Test Signals
Risks are ABI-breaking layout changes, wrong packing/alignment, incorrect `GET_USERREG()` stack assumptions, and type-tag misuse. Test signals include size checks in `fpmodule.c`, ptrace/core-dump FP state compatibility, first-use initialization, and all NWFPE arithmetic/transfer tests.
