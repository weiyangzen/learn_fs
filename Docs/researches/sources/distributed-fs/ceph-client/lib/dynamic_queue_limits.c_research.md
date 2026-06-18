# sources/distributed-fs/ceph-client/lib/dynamic_queue_limits.c

## Purpose
Implements Dynamic Queue Limits (DQL), a byte/object queue-limit controller used by networking and similar producer/completion paths to keep queues deep enough to avoid starvation but not so deep that latency grows unnecessarily. It also includes optional stall detection for queues that receive work but stop completing.

## Important APIs, Types, and Functions
The file operates on `struct dql` from `include/linux/dynamic_queue_limits.h`. Exported functions are `dql_completed()`, `dql_reset()`, and `dql_init()`. `dql_check_stall()` is the internal stall detector. Macros `POSDIFF()` and `AFTER_EQ()` implement wrap-tolerant positive-difference and ordering logic for unsigned counters.

## Control Flow
`dql_init()` sets default bounds (`DQL_MAX_LIMIT`, `min_limit = 0`), records the caller's slack hold time, disables stall detection, and calls `dql_reset()`. `dql_reset()` resets counters, limit, slack tracking, last reap timestamp, and history ring state.

`dql_completed()` reads the producer-updated queued count and stall threshold, validates that completions do not exceed queued work, computes current in-progress work, and adjusts the limit. If the queue was over-limit and drained, or the previous over-limit interval may have starved, it increases the limit by completed work and previous over-limit. If the queue stayed busy, it tracks lowest slack and periodically decreases the limit after `slack_hold_time`. The new limit is clamped to `[min_limit, max_limit]`, derived fields are updated, and `dql_check_stall()` inspects the history bitmap for stale queued work without completions.

## State and Persistence
All state lives in the caller-owned `struct dql`: queued/completed counters, current and adjusted limits, previous interval counters, slack state, history ring, stall counters, and jiffy timestamps. There is no allocation or external persistence. Concurrency relies on `READ_ONCE()`, barriers paired with enqueue-side writes, and caller discipline defined by the DQL API.

## Dependencies and Integration Points
Uses jiffies/time helpers, bitmap operations, `trace_dql_stall_detected()`, and exported symbols for drivers or core networking code. It expects enqueue-side code to call the corresponding DQL queue APIs/macros that update `num_queued`, `last_obj_cnt`, `history`, and `history_head`.

## Risks
Counter arithmetic assumes the DQL invariants are respected; `BUG_ON(count > num_queued - num_completed)` turns misuse into a hard failure. Limit adaptation is sensitive to wraparound assumptions and jiffies-based timing. Stall detection depends on correct memory ordering between queue recording and history reads. Incorrect `min_limit`, `max_limit`, or `stall_thrs` settings can hide real stalls or cause unstable queue depth.

## Test Signals
Exercise DQL through network transmit paths and targeted unit-style tests that model bursty, steady, over-limit, and starved queues. Tracepoint output from `dql_stall_detected`, limit convergence, clamp behavior, and reset behavior are key signals. Tests should include wrap-adjacent counter values and stall thresholds.
