# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/time_stats.h

## Summary
Declares bcachefs time-statistics structures, update helpers, printing APIs, and optional quantile support.

## Main Contents
- `struct time_unit`.
- `struct quantiles` with 15 quantile entries.
- `struct time_stat_buffer` with 31 buffered event pairs.
- `struct bch2_time_stats`, storing min/max/total duration, min/max frequency, last event times, lifetime start, mean/variance, weighted mean/variance, lock, buffer pointer, and quantile flag.
- `struct bch2_time_stats_quantiles`.
- Inline helpers `bch2_time_stats_update()` and `track_event_change()`.

## Important Behavior
`track_event_change()` records the duration of true/false state intervals by remembering `last_event_start` and updating stats when the state changes back.

Initialization sets min fields to `U64_MAX` and captures `local_clock()` as the stats epoch. `bch2_time_stats_init_no_pcpu()` disables automatic percpu buffering.

## Risks
The stats object is not passive: callers that inspect or reset it must respect the lock and percpu-buffer lifecycle. `last_event_start` doubles as state storage in `track_event_change()`, so direct manipulation can break interval tracking.
