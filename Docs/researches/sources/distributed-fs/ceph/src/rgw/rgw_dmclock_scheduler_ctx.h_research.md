# sources/distributed-fs/ceph/src/rgw/rgw_dmclock_scheduler_ctx.h

## Purpose
Declares perf counter ids, counter containers, client config observer, and scheduler context wiring for RGW dmClock.

## Important APIs, types, and functions
`queue_counters` and `throttle_counters` define perf counter ids/builders. `ClientCounters` stores counter refs for each client plus global scheduler stats. `ThrottleCounters` wraps simple throttler counters. `ClientSum`/`ClientSums` aggregate counts and costs. `ClientConfig` observes config and returns `ClientInfo*` by `client_id`. `SchedulerCtx` conditionally owns dmClock config and counters based on `rgw_scheduler_type`.

## Control flow
RGW setup constructs `SchedulerCtx`; dmClock schedulers consume `get_dmc_client_config()` and `get_dmc_client_counters()` to initialize queues and counter callbacks.

## State and persistence
State is process-local counters and config snapshots. No persistent state.

## Dependencies and integration points
Depends on Ceph perf counter collections, config observer APIs, and `rgw_dmclock.h`.

## Risks and test signals
`get_dmc_client_counters()` assumes dmClock mode initialized the optional. Tests should verify no access in non-dmClock modes, config-observer lifetimes, and counter id stability.
