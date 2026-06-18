# sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfdiv.c

Purpose: implements double-precision floating-point division using two-word integer operations.

Important APIs/types/functions: `dbl_fdiv(dbl_floating_point *srcptr1, dbl_floating_point *srcptr2, dbl_floating_point *dstptr, unsigned int *status)`.

Control flow: result sign is established from operand signs. The function handles NaNs, infinities, invalid `inf/inf` and `0/0`, divisor infinity, and divide-by-zero. Finite operands are normalized, with denormal exponents adjusted. The mantissa division uses a non-restoring algorithm: subtract divisor from dividend, iterate through quotient bits with left shifts and add/subtract correction, derive guard/sticky state, round, then handle overflow/underflow and status flags.

State and dependencies: writes destination and status flags only. Depends on `float.h`, `dbl_float.h`, rounding-mode macros, and two-word add/subtract helpers.

Risks: non-restoring division is sensitive to sign-bit interpretation of the partial remainder. Underflow handling repeats tiny-result logic and must remain consistent with multiply. Division-by-zero and invalid-zero cases have different trap/flag behavior. Quotient normalization around hidden-bit absence is a common boundary risk.

Test signals: division by zero, zero by zero, infinity combinations, denormal divisors/dividends, quotient just below/above one, all rounding modes, overflow/underflow traps, and high-precision reference comparisons.
