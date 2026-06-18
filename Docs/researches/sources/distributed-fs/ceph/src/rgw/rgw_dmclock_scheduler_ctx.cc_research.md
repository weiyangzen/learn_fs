# sources/distributed-fs/ceph/src/rgw/rgw_dmclock_scheduler_ctx.cc

## Purpose
Implements dmClock client configuration, perf counter construction, and counter accounting helpers for RGW schedulers.

## Important APIs, types, and functions
`ClientConfig` loads reservation, weight, and limit values for admin/auth/data/metadata clients and observes config keys. `ClientCounters` builds per-client queue counters plus global scheduler throttle counters. `inc()`, `on_cancel()`, and `on_process()` aggregate counter updates. `queue_counters::build()` and `throttle_counters::build()` register perf counters when enabled.

## Control flow
Scheduler context constructs config/counters when dmClock is enabled. Config changes call `ClientConfig::handle_conf_change()`. Schedulers call `on_cancel()` for aborted queued work and `on_process()` for granted requests.

## State and persistence
State is in-memory config vectors and perf counter refs. No persistent storage changes.

## Dependencies and integration points
Uses Ceph config proxy, perf counters collection, dmClock `ClientInfo`, and shared RGW dmClock client ids.

## Risks and test signals
Client ordering is guarded by static assertions and must match enum values. Counter functions must avoid null refs when counters are disabled. Tests should cover config reloads, disabled counters, cancellation cost accounting, reservation/priority latency increments, and per-client/global counter registration.
