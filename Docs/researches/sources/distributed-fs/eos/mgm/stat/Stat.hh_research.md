# sources/distributed-fs/eos/mgm/stat/Stat.hh

## Purpose
`Stat.hh` declares the MGM statistics data model. It provides fixed-size circular rolling counters (`StatAvg`), extended rolling statistics with sample counts, weighted sums, minima, and maxima (`StatExt`), execution timing macros, and the `Stat` class that owns all per-tag statistics maps and reporting entry points.

## Important APIs, Types, And Functions
`StatAvg` exposes `Add()`, `StampZero()`, and `GetAvg3600()/GetAvg300()/GetAvg60()/GetAvg5()`. `StatExt` exposes `Insert()`, `StampZero()`, `GetN*()`, `GetAvg*()`, `GetMin*()`, and `GetMax*()` for the same windows. `EXEC_TIMING_BEGIN()` and `EXEC_TIMING_END()` wrap elapsed-time measurement and call `gOFS->MgmStats.AddExec()`. `Stat` declares maps for UID/GID/app totals, averages, extended stats, execution samples, cumulative times, and public methods implemented in `Stat.cc`.

## Control Flow
The header implements the bucket-update logic inline. `StatAvg::Add()` and `StatExt::Insert()` map `time(0)` into modulo buckets for 3600, 300, 60, and 5 second windows, zero the next bucket, then accumulate the current bucket. `StampZero()` performs the aging step without adding data. Getter methods scan all buckets to produce totals or derived values.

## State And Persistence
The structures are in-memory circular buffers with one bucket per second for each window length. `StatExt` initializes minima to a large signed value and maxima to the minimum `size_t` value. `Stat` persists process-lifetime sparse hash maps and a mutable XRootD mutex; no content is written to disk by this header.

## Dependencies And Integration Points
The header depends on EOS MGM namespace macros, `ThreadAssistant`, XRootD strings/mutexes, Google sparse hash maps, and the global `gOFS` pointer used by the timing macro. It is included by MGM command, stats, and monitoring code needing to record or expose command metrics.

## Risks And Edge Cases
The rolling buckets use wall-clock `time(0)` rather than monotonic time, so clock jumps can smear or clear buckets unexpectedly. Average methods divide by 3599, 299, 59, and 4 rather than by the array size, which is intentional-looking but should be validated. `StatExt::GetAvg*()` divides by the sample count without a zero guard. The macros require unique IDs and a valid `gOFS`; misuse can create shadowing or missing-stat effects.

## Test Signals
Header-level signals include compile coverage of all inline methods and timing macros. Runtime tests should force controlled timestamps if possible, verify bucket rotation, zero stamping, min/max initialization, zero-sample behavior, and that `EXEC_TIMING_END()` records samples only when `gOFS` exists.
