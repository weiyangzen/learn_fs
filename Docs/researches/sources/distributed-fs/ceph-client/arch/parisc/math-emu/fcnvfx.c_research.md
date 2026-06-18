# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvfx.c

Purpose: implements rounded conversions from floating-point values to signed fixed-point integers.

Important APIs/types/functions: `sgl_to_sgl_fcnvfx`, `sgl_to_dbl_fcnvfx`, `dbl_to_sgl_fcnvfx`, and `dbl_to_dbl_fcnvfx`. Destinations are 32-bit signed or two-word `dbl_integer`.

Control flow: each path computes the unbiased exponent, checks overflow while allowing the exact minimum signed integer as a special case, shifts the normalized mantissa into integer form for nonnegative exponents, applies sign by negation or two-word two's complement, and rounds inexact cases according to the current mode. Magnitudes below one start at zero and can round to +/-1. Overflow with traps disabled saturates to max positive or min negative.

State and dependencies: writes destination and status flags. Depends on `cnv_float.h` signed integer macros, `float.h`, `sgl_float.h`, and `dbl_float.h`.

Risks: exact `MININT` is a special exception to normal overflow handling. Rounding after conversion can overflow a 32-bit result and must raise invalid. Signed two-word increment/decrement behavior must preserve carries/borrows. NaNs/infinities are handled by exponent overflow paths.

Test signals: signed min/max boundaries, exact minint, just-out-of-range values, positive and negative fractions around 0.5, NaNs/infinities, all rounding modes, and invalid/inexact trap combinations.
