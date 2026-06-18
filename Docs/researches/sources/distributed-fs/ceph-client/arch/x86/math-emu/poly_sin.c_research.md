# sources/distributed-fs/ceph-client/arch/x86/math-emu/poly_sin.c

## Purpose
This file computes sine and cosine polynomial approximations for reduced x87 trigonometric arguments.

## Important APIs, Types, and Functions
Public functions are `poly_sine(FPU_REG *st0_ptr)` and `poly_cos(FPU_REG *st0_ptr)`. Coefficient tables include lower- and upper-range positive/negative polynomial terms. The functions use `Xsig` arithmetic, `mul64_Xsig()`, `mul_Xsig_Xsig()`, `polynomial_Xsig()`, `round_Xsig()`, and fixed `pi/2` correction constants.

## Control Flow
`poly_sine()` splits the domain around approximately `0.883091`, evaluates a direct sine polynomial for smaller arguments, or computes cosine of `pi/2 - x` with correction for larger arguments. `poly_cos()` splits around approximately `0.687705`, computes direct cosine for small arguments, or computes sine of `pi/2 - x` with extra fix-up. Both convert the final `Xsig` accumulator back into ST0 and preserve or set the appropriate sign.

## State and Persistence
The functions mutate ST0 contents and tag. PARANOID builds may raise internal exceptions for out-of-range results.

## Dependencies and Integration Points
They are called by `fpu_trig.c` after argument reduction and special-case handling. They depend on `poly.h`, register constants, and emulator rounding/copy helpers.

## Risks and Test Signals
Risks include domain split boundary errors, pi/2 approximation correction mistakes, result overflow checks, and sign handling. Test signals include `fsin`, `fcos`, and `fsincos` tests near 0, pi/4, pi/2, reduced quadrant boundaries, and comparison with hardware x87.
