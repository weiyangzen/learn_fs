# sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_u_mul.S

## Purpose
Implements unsigned finite multiplication for normalized `FPU_REG` significands at approximately 128-bit internal precision.

## Important APIs, Types, And Functions
Exports `FPU_u_mul(FPU_REG *a, FPU_REG *b, FPU_REG *c, unsigned int cw, char sign, int exponent_sum)`, though the exact parameters are consumed by assembly offset macros and the common rounding tail.

## Control Flow
The routine multiplies all 32-bit limbs of the two 64-bit significands, accumulates a 128-bit product, computes the biased destination exponent from the summed exponents, clamps extreme underflow, normalizes by shifting left when the top product bit is clear, converts lower product bits into rounding extension information, and jumps to `fpu_reg_round`.

## State And Persistence
Writes the destination register through `reg_round.S`; local accumulators are stack-resident or static under `NON_REENTRANT_FPU`.

## Dependencies And Integration Points
Called by `reg_mul.c` after tag/special-case handling. It depends on `reg_round.S`, `fpu_emu.h` offsets, and control-word definitions.

## Risks
Product accumulation and carry propagation must preserve enough low-order information for rounding. It does not independently validate exponent overflow/underflow beyond preparing values for the common rounder.

## Test Signals
Products near 1.0 and 4.0, normalization shift/no-shift, carry propagation across limbs, low discarded bits affecting rounding, underflow/overflow through the rounder, denormal-preconverted operands from the C wrapper, and precision controls.
