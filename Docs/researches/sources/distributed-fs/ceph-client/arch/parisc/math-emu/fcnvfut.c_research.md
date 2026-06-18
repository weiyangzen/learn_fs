# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvfut.c

Purpose: implements truncating conversions from floating-point values to unsigned fixed-point integers.

Important APIs/types/functions: `sgl_to_sgl_fcnvfut`, `sgl_to_dbl_fcnvfut`, `dbl_to_sgl_fcnvfut`, and `dbl_to_dbl_fcnvfut`.

Control flow: the functions mirror `fcnvfu.c` but omit rounding increments. They check exponent overflow, reject negative values as invalid, convert nonnegative values by shifting mantissas into 32-bit or 64-bit unsigned destinations, and return zero for magnitudes below one. Inexact is still reported when fractional bits are discarded or a nonzero magnitude truncates to zero.

State and dependencies: writes destination and flags. Depends on the same conversion macros and status helpers as `fcnvfu.c`.

Risks: because truncation does not round, inexact status is the only indication of discarded data. Negative source values are treated as invalid even when truncation would otherwise move toward zero. NaN/infinity handling is implicit through exponent overflow checks and saturation/zero behavior.

Test signals: fractional positive values that truncate to zero, positive integer boundaries, negative values of all magnitudes, NaNs/infinities, unsigned max boundaries, inexact trap enabled/disabled, and invalid trap enabled/disabled.
