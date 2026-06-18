# sources/distributed-fs/ceph-client/arch/x86/math-emu/poly_tan.c

## Purpose
This file computes tangent approximations for reduced x87 trigonometric arguments.

## Important APIs, Types, and Functions
The public function is `poly_tan(FPU_REG *st0_ptr)`. It uses odd/even numerator and denominator coefficient tables, `twothirds`, `Xsig` accumulators, and helpers `polynomial_Xsig()`, `mul_Xsig_Xsig()`, `mul64_Xsig()`, `div_Xsig()`, `add_two_Xsig()`, and `round_Xsig()`.

## Control Flow
The function splits the domain around `pi/4`. For larger arguments it computes `pi/2 - x`, evaluates tangent for the complement, applies a pi/2 approximation fix-up, and inverts the result. For smaller arguments it directly evaluates a rational polynomial and adds the correction to the original argument. The result is written back as a positive valid ST0 value; the caller applies final sign/quadrant handling.

## State and Persistence
It mutates ST0 significand, exponent, and tag. There is no file-local persistent state.

## Dependencies and Integration Points
It is called by `fpu_trig.c`'s `fptan()` after argument reduction and before sign adjustment. It depends on the fixed-point helper assembly and `FPU_settag0()`.

## Risks and Test Signals
Risks include near-`pi/2` inversion blow-up, special rounded complement case handling, correction-term precision, and exponent adjustment mistakes. Test signals include `fptan` near 0, pi/4, close to pi/2 after reduction, and comparisons to hardware/reference results.
