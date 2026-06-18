# sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfrem.c

Purpose: implements double-precision floating-point remainder.

Important APIs/types/functions: `dbl_frem(dbl_floating_point *srcptr1, dbl_floating_point *srcptr2, dbl_floating_point *dstptr, unsigned int *status)`.

Control flow: special cases handle NaNs, signaling NaNs, invalid first-operand infinity, divisor infinity, and zero divisor. Finite operands are normalized, preserving the dividend sign as the result sign. If the dividend magnitude is less than the divisor, it either returns the dividend or `dividend - divisor` for the greater-than-half case. Otherwise it repeatedly subtracts the divisor while left-shifting the dividend mantissa, performs a final subtract and tie decision, possibly flips the result sign, normalizes the remainder, and denormalizes on underflow.

State and dependencies: writes destination and status flags, but remainder is exact and does not set inexact. Depends on `float.h` and `dbl_float.h`.

Risks: tie-to-even style sign correction is encoded with `roundup` and exact half comparisons. The iterative subtract loop can be expensive for large exponent differences. Underflow handling assumes exactness and does not use guard/sticky rounding.

Test signals: `fmod`/remainder-style conformance cases, divisor zero, infinities, NaNs, exact half-divisor ties, denormal operands, signed-zero results, and underflow trap behavior.
