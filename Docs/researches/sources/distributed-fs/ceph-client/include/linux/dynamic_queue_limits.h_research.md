# sources/distributed-fs/ceph-client/include/linux/dynamic_queue_limits.h

## Purpose
This header defines Dynamic Queue Limits, a feedback mechanism for producer/consumer queues such as network hardware rings. It adjusts a queue limit to keep enough queued work to avoid starvation while minimizing latency and queued data.

## Important APIs, types, and functions
`struct dql` stores enqueue-path counters (`num_queued`, `adj_limit`, `last_obj_cnt`), stall tracking state, completion-path counters and previous state, slack tracking, configured min/max/hold time, and reported stall metrics. Constants include `DQL_HIST_LEN`, `DQL_MAX_OBJECT`, and `DQL_MAX_LIMIT`. Inline helpers are `dql_queue_stall()`, `dql_queued()`, and `dql_avail()`. Implemented elsewhere are `dql_completed()`, `dql_reset()`, and `dql_init()`.

## Control flow, state, and persistence
Enqueue callers check `dql_avail()`, then call `dql_queued()` with the number of objects queued. Completion callers call `dql_completed()` to retire objects and recalculate the limit. Stall tracking records jiffies bits in a ring history if `stall_thrs` is set. State is in-memory only and must be protected by caller-provided locking; enqueue and completion paths may use different locks according to the header comments.

## Dependencies and integration points
It depends on bitops, bug/WARN support, jiffies, barriers, and cacheline alignment. It is used by networking and other queueing subsystems to tune hardware/software queue depth.

## Risks and test signals
Risks include missing serialization, counter overflow, invalid count values, barrier mistakes in stall history, and stale limits after reset. `dql_queued()` warns and returns if `count > DQL_MAX_OBJECT`. Tests should cover enqueue/completion race patterns with caller locks, limit growth/shrink behavior, stall detection, reset/init defaults, and overflow boundary values.
