# sources/distributed-fs/ceph-client/arch/arm/nwfpe/extended_cpdo.c

## Purpose
Implements extended-precision CPDO arithmetic for NWFPE when `CONFIG_FPE_NWFPE_XP` is enabled.

## Important APIs, Types, And Functions
Exports `ExtendedCPDO`. Defines `dyadic_extended` and `monadic_extended` tables for add, multiply, subtract, reverse subtract, divide, reverse divide, remainder, move, negate, absolute, round, square root, and normalize. Uses `floatx80_*` SoftFloat operations.

## Control Flow
The function resolves `Fm` from a constant or from single/double/extended FPA register values converted to `floatx80`. Dyadic operations similarly resolve `Fn`. It dispatches by arithmetic opcode table and writes the extended result to `rFd->fExtended`, returning 0 for unsupported opcodes or invalid source types.

## State, Dependencies, And Integration
State is the FPA11 register file and type tags. Dependencies include `CONFIG_FPE_NWFPE_XP`, `softfloat.h`, `fpopcode.h`, and constants from `fpopcode.c`. Integrated through `EmulateCPDO`, which chooses extended mode based on operand/destination type and later converts destination size if required.

## Risks And Test Signals
Risks are extended format ABI mismatch, sign-bit handling, unsupported opcode behavior, and conversion/rounding regressions. Test signals include extended precision arithmetic, mixed precision conversions, NaN and exception behavior, and build coverage with XP enabled/disabled.
