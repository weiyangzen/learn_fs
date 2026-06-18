# sources/distributed-fs/ceph-client/arch/x86/math-emu/polynom_Xsig.S

## Purpose
This assembly file evaluates fixed-point polynomials into a 12-byte `Xsig` accumulator using Horner-like multiplication at extended precision.

## Important APIs, Types, and Functions
The exported function is `polynomial_Xsig(Xsig *accum, const unsigned long long *x, const unsigned long long terms[], int n)`. Local stack slots hold a 96-bit sum, 96-bit product accumulator, and overflow flag.

## Control Flow
The function starts from `terms[n]`, then iterates backward through the coefficient table. Each iteration multiplies the current 96-bit sum by the 64-bit fixed-point `x`, compensates for a prior overflow bit, adds the next 64-bit term, records carry overflow for the next iteration, and finally adds the computed 96-bit sum into the caller's accumulator.

## State and Persistence
There is no global state. The caller-provided `accum` is incremented by the polynomial result.

## Dependencies and Integration Points
It depends on `Xsig` word order and i386 calling conventions. It is used by all polynomial approximation C files.

## Risks and Test Signals
Risks include coefficient indexing mistakes, carry propagation errors, unchecked final accumulator overflow, and inline caller assumptions about fixed-point scaling. Test signals include transcendental accuracy tests and standalone comparison of polynomial evaluation against high-precision reference arithmetic.
