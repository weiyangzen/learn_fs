# sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_norm.S

## Purpose
Provides i386 assembly normalization helpers for `FPU_REG` significands.

## Important APIs, Types, And Functions
Exports `FPU_normalize(FPU_REG *n)` and `FPU_normalize_nuo(FPU_REG *n)`. The first normalizes and reports underflow/overflow; the second normalizes without underflow/overflow exception handling.

## Control Flow
Both functions inspect the high and low significand words, shift left until the high bit is set, and adjust the exponent by the shift distance. `FPU_normalize()` then checks `EXP_OVER` and `EXP_UNDER`, calling `arith_overflow()` or `arith_underflow()` as needed before returning a tag. `FPU_normalize_nuo()` returns `TAG_Valid` or `TAG_Zero` without exception calls.

## State And Persistence
The input register is modified in place. Exception paths update global FPU exception state. No persistent storage is allocated.

## Dependencies And Integration Points
Called by conversion, load, and arithmetic code. It relies on `FPU_REG` offset macros and arithmetic exception helpers declared through `fpu_emu.h` and `exception.h`.

## Risks
The assembly assumes exact structure offsets and 32-bit calling conventions. Exponent conversion between internal and 80x87 biased form must happen in the correct order. Underflow during shift adjustment is expected and must flow into arithmetic exception handling.

## Test Signals
Normalize already-normal values, low-word-only values, zero, exponent underflow, exponent overflow, and denormal conversion callers that require no-underflow behavior.
