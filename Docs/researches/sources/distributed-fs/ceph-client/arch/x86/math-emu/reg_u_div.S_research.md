# sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_u_div.S

## Purpose
Implements unsigned finite division of two normalized `FPU_REG` significands.

## Important APIs, Types, And Functions
Exports `FPU_u_div(FPU_REG *a, FPU_REG *b, FPU_REG *dest, unsigned int control_word, char sign)`. It computes/adjusts the destination exponent and tail-jumps to `fpu_reg_round`.

## Control Flow
The routine computes exponent difference plus bias, clamps extreme underflow, and fast-paths divisors with zero low word using 32-bit division. Full division builds a multiword accumulator, estimates quotient limbs using the divisor high word plus one, corrects overestimates, computes remainder relation to the denominator for rounding information, handles quotient overflow by shifting right and incrementing exponent, then sets up `%eax:%ebx:%edx` for rounding.

## State And Persistence
The destination register is written during rounding. Local accumulator/result storage is stack-resident unless non-reentrant mode uses statics.

## Dependencies And Integration Points
Called by `reg_divide.c` for finite operands. Integrates with `reg_round.S` for precision, sign, and exception handling.

## Risks
The long division correction logic has many carry/borrow invariants. Remainder classification drives exact/half/more-than-half rounding and is a correctness hotspot. Divisor normalization is required; paranoid builds detect broken preconditions.

## Test Signals
Fast divisor path, full divisor path, dividend less/equal/greater than divisor, quotient overflow, exact division, exact half remainder, just-below/above-half remainders, exponent underflow, and all precision/rounding modes.
