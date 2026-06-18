# File Research: sources/cow-pools/bcachefs-tools/fs/util/mean_and_variance.c

Purpose: Exported accessors for the streaming mean, median, and MAD estimator.

Key APIs and behavior:
- `mean_and_variance_get_mean()` returns exact `sum / n`, or zero with no samples.
- `mean_and_variance_get_mad()` returns current median absolute deviation estimate.
- `mean_and_variance_get_stddev()` reports Gaussian-equivalent spread as approximately `1.4826 * MAD`.
- `mean_and_variance_get_median()` returns the current median estimate.

Integration:
- Implements functions declared in `mean_and_variance.h`.
- Exports symbols with `EXPORT_SYMBOL_GPL`.
- Used by time statistics and related latency reporting.

Risks and invariants:
- The file intentionally preserves a "stddev" readout label while using robust MAD semantics.
- The scaled stddev approximation uses `(mad * 1518) >> 10`, so precision is approximate by design.
