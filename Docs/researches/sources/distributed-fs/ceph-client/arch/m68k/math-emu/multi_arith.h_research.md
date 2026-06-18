# sources/distributed-fs/ceph-client/arch/m68k/math-emu/multi_arith.h

## Purpose
Defines specialized multi-precision integer helpers used to implement extended-precision floating-point mantissa arithmetic.

## APIs, Flow, And State
The header provides inline helpers for denormalizing/overnormalizing `struct fp_ext`, adding/subtracting 64-bit mantissas with low guard byte, propagating carry, 64-bit multiply/divide macros, 64/96-bit add/sub macros, 128-bit mantissa multiply/divide, and writing normalized 128-bit results back to `fp_ext`. The helpers mutate their operand structures directly and set FPSR exception bits through `fp_set_sr()` in overflow/rounding-relevant paths.

## Dependencies And Integration
Depends on `fp_emu.h`, m68k inline assembly instructions such as `bfffo`, `mulu.l`, `divu.l`, `addx`, and `subx`, and `union fp_mant64/fp_mant128` definitions from architecture math-emu headers. Used by `fp_arith.c` for add/sub alignment, multiplication, division, and result packing.

## Risks And Test Signals
The routines are explicitly not general-purpose; they assume normalized ranges and emulator-specific mantissa layout. Inline assembly constraints and carry semantics are architecture-sensitive. Test signals are arithmetic identity tests for FP add/mul/div, mantissa boundary cases, denormal shifts across 8/32/64-bit boundaries, and compiler build tests across supported m68k CPU variants.
