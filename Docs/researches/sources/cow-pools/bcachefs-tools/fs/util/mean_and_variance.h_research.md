# File Research: sources/cow-pools/bcachefs-tools/fs/util/mean_and_variance.h

Purpose: Defines a compact streaming estimator for exact mean plus stochastic-gradient median and MAD.

Key APIs and behavior:
- `struct mean_and_variance` stores `n`, `sum`, `median`, and `mad`.
- `sgm_median_mad_step()` updates median and MAD using sign-gradient steps.
- `mean_and_variance_update()` always tracks exact count/sum, and updates robust spread using either all-time or weighted mode.
- Weight `0` selects an approximate `1/n` Robbins-Monro schedule via `ilog2(n)`; nonzero weight selects exponential behavior.

Integration:
- Included by `time_stats.h`, `util.h`, and tests.
- Public getter declarations are implemented in `mean_and_variance.c`.

Risks and invariants:
- `abs(x - *median)` on signed values depends on inputs staying in a sane range.
- The estimator is robust and cheap, but callers must not expect exact variance.
