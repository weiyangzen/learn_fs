# File Research: sources/block-storage/linux-dm/drivers/md/dm-ps-historical-service-time.c

## Purpose

`dm-ps-historical-service-time.c` implements the `historical-service-time` multipath selector. It estimates future service time from a time-weighted exponential moving average of completed I/O service times plus outstanding request counts, with stale-path probing logic.

## State And Parameters

The selector tracks valid and failed path lists, valid path count, precomputed EMA weights, and a `threshold_multiplier`. Each path stores a spinlock, historical service time in fixed-point units, `stale_after`, `last_finish`, and outstanding request count.

Selector constructor arguments are optional `[<base_weight> [<threshold_multiplier>]]`. `base_weight` is a 10-bit fixed-point EMA base below 1024, defaulting to 0.95. Weights are precomputed for 64 time buckets of roughly 16 ms each. `threshold_multiplier` suppresses latency comparison when paths are considered too close.

## Selection Algorithm

`hst_select_path()` scans valid paths and chooses the best according to `hst_compare()`, then moves the chosen path to the list tail for tie spreading. The comparison first checks whether historical service times exceed the threshold. If not, it compares outstanding counts. It preferentially probes unloaded stale paths, compares estimated service time using `(1 + outstanding) * historical_service_time`, and limits stale winners to equal usage.

## I/O Accounting

`hst_start_io()` increments the path’s outstanding count. `hst_end_io()` computes service time, decrements outstanding, updates the fixed-point EMA with the precomputed weight for the observed duration, and sets `stale_after` to `last_finish + valid_count * historical_service_time`. `path_service_time()` serializes overlapping completions by using `last_finish` when the previous completion was later than this I/O’s start time.

## Failure And Status

Path failure moves the path to `failed_paths` and decrements `valid_count`; reinstatement moves it back and increments `valid_count`. Selector-level status reports the first weight and threshold multiplier. Per-path info reports historical service time, outstanding count, and stale deadline; table output emits a placeholder `0` per path.

## Invariants And Risks

- Per-path stats are protected by the path’s lock; path-list membership and valid count are protected by the selector lock.
- `valid_count` directly affects stale deadlines, so fail/reinstate balance matters.
- Fixed-point math clamps service-time input to avoid overflow, and high outstanding counts shift values before multiplication.
- Clock-domain assumptions matter because selection compares current time with stale deadlines set during completion.
- `repeat_count` is parsed and stored but table status emits `0`, unlike older selectors that preserve the argument.

## Test Focus

Test base weight validation, threshold behavior, stale unloaded path probing, degraded stale path limiting, outstanding count balance on errors/requeues, fail/reinstate valid count, overflow boundaries for huge service times/outstanding counts, status/table output, and clock behavior for stale detection.
