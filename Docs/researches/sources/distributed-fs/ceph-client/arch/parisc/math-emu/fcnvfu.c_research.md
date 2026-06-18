# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvfu.c

Purpose: implements rounded conversions from floating-point values to unsigned fixed-point integers.

Important APIs/types/functions: `sgl_to_sgl_fcnvfu`, `sgl_to_dbl_fcnvfu`, `dbl_to_sgl_fcnvfu`, and `dbl_to_dbl_fcnvfu`. Destination types are 32-bit unsigned or `dbl_unsigned`.

Control flow: each function computes unbiased source exponent, checks overflow against the destination integer width, rejects negative values as invalid, builds an integer mantissa when exponent is nonnegative, and otherwise starts from zero for magnitudes below one. Inexact cases round according to current mode: plus increments positive results, minus rejects negative fractional values, and nearest handles half-ulp ties. Disabled invalid traps write saturated all-ones for positive overflow and zero for negative invalid inputs.

State and dependencies: writes output and status flags. Depends on `cnv_float.h` integer construction/rounding macros plus `float.h`, `sgl_float.h`, and `dbl_float.h`.

Risks: unsigned conversion of negative values is a major edge surface and sometimes clears `inexact` when invalid is raised. Rounding can overflow a 32-bit unsigned destination after an initially in-range double-to-single conversion. NaNs and infinities flow through exponent overflow paths rather than a separate class decoder.

Test signals: negative finite values, negative fractions by rounding mode, NaNs/infinities, positive overflow saturation, `UINT_MAX` boundaries, `2^32` and `2^64` edges, half-way fractions, and invalid/inexact trap combinations.
