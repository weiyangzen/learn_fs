# sources/distributed-fs/ceph-client/arch/arm/nwfpe/single_cpdo.c

## Purpose
Implements FPA11 CPDO arithmetic for single-precision operands and results in NWFPE.

## Important APIs, Types, And Functions
Exports `SingleCPDO`. Defines `dyadic_single` and `monadic_single` tables for add, multiply, subtract, reverse subtract, divide, reverse divide, remainder, move, negate, absolute, round, square root, and normalize. Uses `float32_*` SoftFloat functions and single-precision constants.

## Control Flow
`SingleCPDO` resolves `Fm` from a constant or a single-precision register. For dyadic instructions it requires `Fn` to also be single precision. It indexes the opcode dispatch table and writes `rFd->fSingle` on success; unsupported opcodes or incompatible source types return 0.

## State, Dependencies, And Integration
State is FPA11 single registers and type tags. Dependencies are `fpa11.h`, `softfloat.h`, and `fpopcode.h`. Integrated through `EmulateCPDO`, which selects precision, converts destinations when necessary, and raises exceptions.

## Risks And Test Signals
Risks include rejecting valid promoted operands too early, unsupported deprecated functions, incorrect sign manipulation for negate/abs, and exception/rounding regressions. Test signals are single-precision FPA arithmetic, constant operands, invalid type handling, NaN/exception cases, and destination conversion via `EmulateCPDO`.
