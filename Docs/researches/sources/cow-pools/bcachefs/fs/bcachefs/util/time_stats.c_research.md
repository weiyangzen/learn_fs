# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/time_stats.c

## Summary
Implements bcachefs event-duration and inter-arrival statistics collection with optional quantile tracking, optional percpu buffering, and text/JSON reporting.

## Main Responsibilities
- Chooses readable time units from nanosecond values.
- Updates duration and frequency mean/variance, weighted mean/variance, min/max, and totals.
- Maintains approximate quantile entries when enabled.
- Switches high-frequency stats to percpu buffers unless disabled.
- Flushes percpu buffers before reporting or reset.
- Emits aligned human-readable text through `seq_buf`.
- Emits structured JSON summaries.

## Key APIs
- `bch2_pick_time_units()`.
- `__bch2_time_stats_update()`, `__bch2_time_stats_clear_buffer()`.
- `bch2_time_stats_reset()`.
- `bch2_time_stats_to_seq_buf()`, `bch2_time_stats_to_json()`.
- `bch2_time_stats_init()`, `bch2_time_stats_init_no_pcpu()`, `bch2_time_stats_exit()`.

## Important Behavior
Stats are updated directly under a spinlock until the source is frequent enough, then `alloc_percpu_gfp()` is attempted and each CPU buffers up to 31 start/end pairs. Reporting drains all CPU buffers under the main spinlock.

Quantiles use an Eytzinger-order array and adaptive step values. Text output can be suppressed for zero-count stats with `TIME_STATS_PRINT_NO_ZEROES`.

## Risks
Readers/reporters mutate state by draining percpu buffers, so reporting is not a purely const operation. The percpu pointer uses sentinel values, making checks against `TIME_STATS_NONPCPU` important. Quantiles are approximate and marked “do not use” for new code in the header.
