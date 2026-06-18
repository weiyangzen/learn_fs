# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/mean_and_variance.c

This file implements incremental mean/variance helpers and exponentially weighted variants.

Core arithmetic:
- `u128_div()` divides a 128-bit value by a 64-bit divisor using staged 64/32-bit division.
- Exported for GPL use.

Unweighted stats:
- `mean_and_variance_get_mean()` returns `sum / n`, or zero for no samples.
- `mean_and_variance_get_variance()` computes `E[x^2] - mean^2` using 128-bit arithmetic.
- `mean_and_variance_get_stddev()` returns integer square root of variance.

Weighted stats:
- `mean_and_variance_weighted_update()` updates exponentially weighted mean and variance.
- Mean is stored shifted by `weight` for precision.
- Variance is also stored shifted and unshifted at readout.
- First update is special-cased by caller-supplied `initted`.
- Getters return weighted mean, variance, and stddev.

Important constraints:
- Caller must not change weight after updates.
- Caller must not directly inspect weighted fields as final values.
- Signed division by powers of two uses the helper from the header for round-toward-zero behavior.

Research notes:
- Comments cite an external statistical derivation paper and KUnit tests in this group verify expected behavior.
