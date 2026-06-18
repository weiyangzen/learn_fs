# sources/distributed-fs/ceph/src/rgw/rgw_dmclock_async_scheduler.h

## Purpose
Declares the asynchronous RGW dmClock scheduler and a simple max-concurrency throttler alternative.

## Important APIs, types, and functions
`AsyncScheduler` inherits `md_config_obs_t` and `Scheduler`, owns a dmClock `PullPriorityQueue`, Asio timer, counters, max/outstanding request atomics, and observer pointer. `async_request()` allocates a completion-backed request, queues it, schedules processing, and updates queue/limit counters. `SimpleThrottler` implements `Scheduler` with only `rgw_max_concurrent_requests` accounting.

## Control flow
Async request submission is nonblocking and completes handlers when dmClock grants a request. Scheduler users receive a `SchedulerCompleter` from the base class and must let it destruct to release capacity.

## State and persistence
All state is transient scheduling state. Perf counters expose queued cost, granted phases, limits, throttle count, and outstanding requests.

## Dependencies and integration points
Uses Boost.Asio, Ceph async completion, dmClock queue types, config observers, and scheduler context counters.

## Risks and test signals
`SimpleThrottler::schedule_request_impl()` increments outstanding before checking the limit, so error paths rely on completer semantics to unwind. Tests should validate capacity release on success and failure, counter deltas, config changes, and handler executor affinity.
