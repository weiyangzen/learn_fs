# sources/distributed-fs/ceph/src/rgw/rgw_dmclock_async_scheduler.cc

## Purpose
Implements Boost.Asio-based asynchronous dmClock scheduling for RGW requests, including cancellation, config updates, throttle accounting, and ready-request processing.

## Important APIs, types, and functions
`AsyncScheduler::~AsyncScheduler()` cancels queued work and unregisters config observation. `handle_conf_change()` updates delegated client info and max concurrent requests, refreshes dmClock client infos, and schedules processing. `schedule_request_impl()` bridges blocking coroutine/yield callers to `async_request()`. `request_complete()` returns a throttle unit. `cancel()` and `cancel(client)` abort queued requests and update counters. `schedule()` arms the timer. `process()` pulls ready requests while under `max_requests`, posts completions, tracks reservation/priority latency, and schedules future work.

## Control flow
Requests enter the pull priority queue from the header template. Processing runs in the Asio executor via timer callbacks. Each ready completion grants capacity until the caller's returned completer calls `request_complete()`.

## State and persistence
State is in-memory queue contents, timer, outstanding count, max request limit, client config, and perf counters.

## Dependencies and integration points
Uses crimson dmClock pull queue, Ceph async completion, Boost.Asio timers/executors, Ceph config observation, and RGW scheduler interface.

## Risks and test signals
Risks include timer callbacks after destruction, outstanding underflow, cancellation races, executor-thread assertions, and config changes while requests are queued. Tests should cover reservation vs priority phases, future timers, max concurrency, cancellation, config reload, and error translation to `-EAGAIN`.
