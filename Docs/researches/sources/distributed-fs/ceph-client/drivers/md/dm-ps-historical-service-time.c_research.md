# sources/distributed-fs/ceph-client/drivers/md/dm-ps-historical-service-time.c

## Purpose
Implements the `historical-service-time` multipath path selector. It estimates future path latency from an exponentially weighted moving average of completed service time plus outstanding I/O count, and includes staleness probing logic so paths that have not completed I/O recently are not permanently ignored.

## Important APIs, Types, And Functions
The selector registers a `struct path_selector_type` named `historical-service-time` with `DM_PS_USE_HR_TIMER`. `struct selector` tracks valid/failed path lists, valid count, precomputed EMA weights, and a threshold multiplier. `struct path_info` stores a path pointer, repeat count, per-path lock, fixed-point historical service time, stale deadline, last finish time, and outstanding request count.

Important helpers are `fixed_power()`, `fixed_ema()`, `hst_set_weights()`, `hst_compare()`, `hst_select_path()`, `hst_start_io()`, and `hst_end_io()`. Creation accepts optional `base_weight` and `threshold_multiplier`; path addition accepts optional `repeat_count`.

## Control Flow
On selection, the selector locks the valid list, compares every valid path against the current best using current time, historical service time, outstanding count, and stale deadline, then moves the selected path to the tail for tie fairness. `start_io` increments the path outstanding count. `end_io` computes elapsed service time from the supplied high-resolution start timestamp, serializes overlapping completions using `last_finish`, updates the fixed-point EMA using the precomputed weight bucket, decrements outstanding, and refreshes the stale deadline.

Failed and reinstated paths are moved between valid and failed lists under selector lock. Status reports global table args and per-path historical service time/outstanding/stale state.

## State And Persistence
All state is in memory and reset when the table is loaded or the module is reloaded. The selector maintains no on-disk persistence. The EMA uses 10-bit fixed-point arithmetic and time buckets of about 16 ms to avoid expensive exponentiation on every completion.

## Dependencies And Integration Points
It integrates with the DM multipath path-selector API from `dm-path-selector.h`; the multipath core calls `select_path`, `start_io`, and `end_io` around each mapped I/O. It uses `ktime_get_ns()` and the high-resolution timing feature flag so `start_time` passed to `end_io` is meaningful.

## Risks
Arithmetic overflow is mitigated but still a key risk in the outstanding-count and fixed-point service-time calculations. The threshold multiplier can make latency differences disappear if configured too high. Stale-path handling intentionally probes unused paths, which can send I/O to a degraded path. Correctness also depends on balanced `start_io`/`end_io` calls; an underflow in `outstanding` would distort all future choices.

## Test Signals
Test with paths of different latency, intermittent idleness, failures/reinstatements, and high queue depth. Status should show historical service time changing after completions and stale deadlines refreshing. Module load should log version `0.1.1`, and table parsing should reject invalid fixed-point weights or extra arguments.
