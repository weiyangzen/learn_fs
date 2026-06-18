# sources/distributed-fs/ceph-client/arch/x86/math-emu/poly_2xm1.c

## Purpose
This file computes the polynomial approximation for `2^x - 1`, used by the x87 `f2xm1` instruction.

## Important APIs, Types, and Functions
The public function is `poly_2xm1(u_char sign, FPU_REG *arg, FPU_REG *result)`. It uses coefficient table `lterms`, leading `hiterm`, and shift constants for quarter-domain identities. It calls `polynomial_Xsig()`, `mul_Xsig_Xsig()`, `shr_Xsig()`, `add_two_Xsig()`, `div_Xsig()`, `round_Xsig()`, and `FPU_round()`.

## Control Flow
The function requires `|arg| < 1`. It converts the argument significand into `Xsig`, reduces larger arguments by subtracting 0.25/0.5/0.75 slices, evaluates the polynomial plus leading term, applies the identity for shifted positive arguments, and for negative arguments computes `-f(x)/(1+f(x))`. It rounds the `Xsig` back into ST0 and sets the tag.

## State and Persistence
It mutates ST0/result register contents and tag, and may report internal exceptions in PARANOID builds. No file-local state persists.

## Dependencies and Integration Points
It is called by `fpu_trig.c`'s `f2xm1()` handler and depends on register constants, `FPU_round()`, and fixed-point helpers.

## Risks and Test Signals
Risks include domain violations, reduction identity mistakes, negative-argument division precision, and rounding flag mismatches. Test signals include `f2xm1` over negative/positive small values, near-domain-boundary inputs, and comparison to hardware/reference results.
