# sources/distributed-fs/ceph-client/arch/arm/nwfpe/double_cpdo.c

## Purpose
Implements FPA11 CPDO arithmetic for double-precision operations and mixed single/double operands in NWFPE.

## Important APIs, Types, And Functions
Exports `DoubleCPDO(struct roundingData *, unsigned int opcode, FPREG *rFd)`. Defines `dyadic_double` and `monadic_double` dispatch tables plus helpers for reverse subtract/divide, move, negate, and absolute value. Uses SoftFloat functions such as `float64_add`, `float64_mul`, `float64_div`, `float64_rem`, `float64_round_to_int`, and `float64_sqrt`.

## Control Flow
`DoubleCPDO` resolves `Fm` from a constant, single register converted to double, or double register. For dyadic operations it resolves `Fn` similarly. It indexes the opcode dispatch table by `(opcode & MASK_ARITHMETIC_OPCODE) >> 20`; missing table entries cause failure. Successful operations write `rFd->fDouble`.

## State, Dependencies, And Integration
State is the current thread's `FPA11` register file and type tags. Dependencies are `fpa11.h`, `fpopcode.h`, and SoftFloat. Integrated through `EmulateCPDO`, which handles destination-size conversion and exception raising.

## Risks And Test Signals
Risks include endian-specific sign-bit manipulation, unsupported deprecated opcodes, type-tag mismatches, and precision/rounding regressions. Test signals are FPA double arithmetic instruction tests, mixed single/double operands, NaN/exception cases, and endian builds.
