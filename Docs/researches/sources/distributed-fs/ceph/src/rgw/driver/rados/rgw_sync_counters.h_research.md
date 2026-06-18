# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_counters.h

## Purpose
This header declares perf counter id ranges and the sync delta counter manager for RGW sync telemetry.

## Important APIs, Types, and Functions
- `sync_counters` reserves ids beginning at `805000` for fetch bytes, not-modified counts, fetch errors, poll latency/errors, and lock latency.
- `sync_counters::build()` returns a registered `PerfCountersRef`.
- `rgw_sync_delta_counters_key` names the delta counter set as `rgw_sync_delta`.
- `sync_deltas` reserves ids beginning at `806000` for datalog sync delta.
- `SyncDeltaCountersManager` owns a `PerfCounters` object and exposes `tset()`.

## Control Flow
Sync components include this header to publish counters. Construction is delegated to the `.cc` implementation, and callers use enum ids when updating metrics.

## State and Persistence Behavior
State is in-memory perf counter state. The manager owns the counter object and removes it from the collection in its destructor.

## Dependencies and Integration Points
It depends on Ceph perf counter collection types and `CephContext` declarations. It integrates with ceph-mgr-visible daemon telemetry.

## Risks
- Changing enum values can break metric continuity or collide with other counter ranges.
- Callers must use ids from the correct namespace with the correct counter object.

## Test Signals
Build coverage for enum use, perf dump checks for expected counter names, and lifecycle checks for manager construction/destruction are useful.
