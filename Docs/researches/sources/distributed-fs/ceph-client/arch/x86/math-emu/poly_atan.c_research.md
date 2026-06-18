# sources/distributed-fs/ceph-client/arch/x86/math-emu/poly_atan.c

## Purpose
This file computes arctangent approximations for `fpatan`, converting ST1/ST0 ratios into an angle with quadrant and sign adjustments.

## Important APIs, Types, and Functions
The public function is `poly_atan(FPU_REG *st0_ptr, u_char st0_tag, FPU_REG *st1_ptr, u_char st1_tag)`. It uses odd polynomial coefficient tables, `denomterm`, `fixedpterm`, and `pi_signif`. It calls `div_Xsig()`, `mul_Xsig_Xsig()`, `mul64_Xsig()`, `polynomial_Xsig()`, `add_Xsig_Xsig()`, `add_two_Xsig()`, `round_Xsig()`, and `FPU_round()`.

## Control Flow
The function compares operand magnitudes to decide whether to invert the ratio, divides significands to form the reduced argument, applies an atan identity when the argument is larger than `sqrt(2)-1`, evaluates rational polynomial terms, then adjusts by `pi/4`, `pi/2`, or `pi` depending on transformation, inversion, and original sign. The final angle is rounded into ST1 and the precision flag is set.

## State and Persistence
It mutates ST1 register contents and tag, and status precision bits. ST0 is later popped by the caller in `fpatan()`.

## Dependencies and Integration Points
It is called by `fpu_trig.c` after special-case handling for zeros, infinities, NaNs, and denormals. It depends on fixed-point `Xsig` helpers and x87 rounding semantics.

## Risks and Test Signals
Risks include quadrant errors, transformed/inverted boundary mistakes, sign preservation bugs, and polynomial precision loss. Test signals include `fpatan` quadrants, zero/infinity combinations, denormal-valid combinations, and comparisons with hardware x87.
