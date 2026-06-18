# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvfxt.c

Purpose: implements truncating conversions from floating-point values to signed fixed-point integers.

Important APIs/types/functions: `sgl_to_sgl_fcnvfxt`, `sgl_to_dbl_fcnvfxt`, `dbl_to_sgl_fcnvfxt`, and `dbl_to_dbl_fcnvfxt`.

Control flow: the functions follow the signed conversion structure of `fcnvfx.c` but omit all rounding-mode increments/decrements. Overflow checks saturate or return exact minimum signed integer where allowed. Nonnegative exponents convert shifted mantissas and apply sign; negative exponents write zero. Discarded fractional data sets inexact or returns an inexact exception if enabled.

State and dependencies: writes destination and flags. Depends on `float.h`, `sgl_float.h`, `dbl_float.h`, and `cnv_float.h`.

Risks: truncation toward zero differs from rounding-mode conversion, so callers must dispatch the correct opcode. Inexact still matters even when the numeric result is zero. Exact minimum integer and disabled invalid traps remain architecture-sensitive. NaN/infinity behavior is implicit via exponent overflow handling.

Test signals: truncation of positive/negative fractions, signed min/max boundaries, exact minimum integer, NaNs/infinities, inexact trap tests, invalid trap tests, and comparison with rounded `fcnvfx` for all rounding modes.
