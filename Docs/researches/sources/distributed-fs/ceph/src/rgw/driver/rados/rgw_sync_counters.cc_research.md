# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_counters.cc

## Purpose
This file builds and registers performance counters used by RGW sync and sync delta reporting.

## Important APIs, Types, and Functions
- `sync_counters::build()` creates a `PerfCountersBuilder`, marks counters useful for ceph-mgr, adds fetch, poll, and lock counters, registers them, and returns a `PerfCountersRef`.
- `sync_deltas::add_rgw_sync_delta_counters()` adds the `sync_delta` time counter.
- `sync_deltas::SyncDeltaCountersManager` creates, registers, updates, and unregisters sync delta counters.

## Control Flow
Callers request a counter set by name. The builder defines counter ids and labels, creates `PerfCounters`, and registers them with `CephContext`'s perf counter collection. The delta manager validates the perf counter key name, constructs a counter set, and exposes `tset()` for updates.

## State and Persistence Behavior
Counters are process-local telemetry registered in memory with Ceph's perf counter collection. They are not persisted as RADOS objects, but ceph-mgr can scrape/report them. The delta manager removes its counter set on destruction.

## Dependencies and Integration Points
The file depends on `CephContext`, `PerfCountersBuilder`, `PerfCountersCollection`, perf counter key helpers, and ids from `rgw_sync_counters.h`. It integrates with ceph-mgr through useful-priority perf counters.

## Risks
- Counter id ranges must remain unique and consistent with the header.
- `SyncDeltaCountersManager` asserts that the provided name has the expected key.
- Counter lifetime must end before the owning context/collection disappears.

## Test Signals
Signals include tests that instantiate the counter builders, verify counter names/types, update `sync_delta`, and confirm registration/removal during shutdown.
