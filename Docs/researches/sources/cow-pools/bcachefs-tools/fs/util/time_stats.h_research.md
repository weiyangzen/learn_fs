# File Research: sources/cow-pools/bcachefs-tools/fs/util/time_stats.h

Purpose: Public data model and helpers for bcachefs time statistics.

Key APIs and behavior:
- Defines `time_unit`, quantile constants/structures, per-CPU event buffer, and `struct bch2_time_stats`.
- Tracks min/max/total duration, min/max frequency, last event times, lifetime start, and weighted/unweighted estimators.
- `bch2_time_stats_update()` records an event ending at `local_clock()`.
- `track_event_change()` tracks boolean state intervals.
- Declares text/JSON output, init/reset/exit, and quantile wrapper init/exit.

Integration:
- Implemented by `time_stats.c`.
- Depends on `mean_and_variance.h`.

Risks and invariants:
- Time values are nanoseconds.
- `TIME_STATS_MV_WEIGHT` gives weighted estimator half-life around 256 samples.
- Quantiles are explicitly discouraged for new code unless manually enabled.
