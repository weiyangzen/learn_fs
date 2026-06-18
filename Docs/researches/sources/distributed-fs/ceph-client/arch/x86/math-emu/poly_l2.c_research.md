# sources/distributed-fs/ceph-client/arch/x86/math-emu/poly_l2.c

## Purpose
This file computes base-2 logarithm polynomial approximations for `fyl2x` and `fyl2xp1`.

## Important APIs, Types, and Functions
Public functions are `poly_l2(FPU_REG *st0_ptr, FPU_REG *st1_ptr, u_char st1_sign)` and `poly_l2p1(u_char s0, u_char s1, FPU_REG *r0, FPU_REG *r1, FPU_REG *d)`. Static `log2_kernel()` evaluates `log2(1+x)`. Coefficients are held in `logterms` and `leadterm`.

## Control Flow
`poly_l2()` reduces ST0 into a range around 1 using `sqrt(2)` thresholds, evaluates a log kernel, adds the integer exponent component, multiplies by ST1, rounds into ST1, and sets precision. `poly_l2p1()` handles `log2(1+x)` for small `x`, multiplies by ST1, rounds into the destination, and handles too-large or negative-domain inputs through invalid-operation behavior. `log2_kernel()` uses a transformed numerator/denominator, `div_Xsig()`, polynomial evaluation, and leading-term correction.

## State and Persistence
It mutates ST1/destination register contents, tags, and exception/precision status. It can signal underflow for very small results.

## Dependencies and Integration Points
It is called by `fpu_trig.c` handlers `fyl2x()` and `fyl2xp1()`. It depends on fixed-point helpers, register constants, control-word exception handling, and `FPU_round()`.

## Risks and Test Signals
Risks include domain handling for negative inputs, exponent recombination errors, underflow handling, and precision loss in the reduced kernel. Test signals include `fyl2x` and `fyl2xp1` across values near 1, near -1 for `log1p`, denormals, zeros, infinities, and comparison to hardware/reference results.
