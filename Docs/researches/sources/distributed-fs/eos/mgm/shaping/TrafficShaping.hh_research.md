<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/shaping/TrafficShaping.hh -->
# sources/distributed-fs/eos/mgm/shaping/TrafficShaping.hh

## Purpose
Declares MGM traffic shaping types, policy/state containers, manager APIs, and the threaded engine wrapper. The header defines the data model used for FST IO report aggregation, policy control, plugin ABI exchange, FST delay publication, and admin-facing inspection.

## Important APIs and Types
- C plugin ABI:
  - `DelayState` and `DelayAlgoFunc`: single-entity delay calculation inputs and output.
  - `AppState` and `ControllerAlgoFunc`: flat app array used by custom reservation/controller plugins.
- Runtime metric types:
  - `StreamState`: last cumulative counters and generation id per node stream.
  - `RateMetrics`: read/write Bps and IOPS.
  - `MultiWindowRate`: atomic accumulators, EMA/SMA snapshots, sliding windows, stream activity data.
  - `RateSnapshot`: read-only exported snapshot shape with cumulative totals and estimator arrays.
  - `ProjectionCumulativeStats`: app/uid/gid/node cumulative totals.
- Key types:
  - `StreamKey` aliases `IoStatsKey` for app/uid/gid/fsid.
  - `DiskKey` and `DetailedKey` provide hashable/orderable node/fs and node/stream dimensions.
- Policy/diagnostic types:
  - `TrafficShapingPolicy`: persistent user limits/reservations/enabled flag plus ephemeral controller limits/timestamps.
  - `AppIoPressureSnapshot`, `AppNodeIoPressureSnapshot`, `MapCardinalityStats`.
- `TrafficShapingManager`: core API for report processing, estimator updates, policy updates, controller updates, delay publication, stats snapshots, policy serialization, garbage collection, and runtime clearing.
- `TrafficShapingEngine`: lifecycle/config/thread API around a shared manager, report queueing, FST sync, automatic detail-level switching, and persistent config setters.

## Control Flow and Usage Contract
The header separates pure management from threading. `TrafficShapingManager` is usable directly in tests and receives parsed reports plus explicit update ticks. `TrafficShapingEngine` owns `AssistedThread` instances for estimator updates, FST IO policy updates, and enabled/config sync. Public setters on the engine typically apply to atomics/manager and persist to `FsView` global config; private `Apply*Config` variants replay config without necessarily storing it again.

The detail-level model supports aggregate mode, where fsid is collapsed to zero, and filesystem detail mode, where per-fsid stats are retained. Automatic detail thresholds are declared so the engine can switch between modes based on map cardinality.

## State and Persistence
Declared manager state includes runtime node streams, rate maps, cumulative maps, policy maps, per-node FST delay configs, published-config cache, sliding-window loop metrics, plugin handles/function pointers, and atomic toggles. Declared engine state includes thread handles, running flag, configurable periods, detail flags, automatic detail thresholds, limit/reservation/controller thresholds, garbage-collection idle seconds, and a mutex-protected report queue.

Persistent fields are not stored directly by the header, but setter declarations map to global config writes in the implementation. `TrafficShapingPolicy` explicitly distinguishes persistent user configuration from ephemeral controller configuration in its member layout.

## Dependencies and Integration Points
Includes `common/AssistedThread.hh`, common traffic shaping key/window helpers, and generated protobuf definitions. Exposes types used by MGM admin commands, `XrdMgmOfs`, FsView report ingestion, and unit tests. `IN_TEST_HARNESS` can widen access to otherwise private manager/engine methods, making internal algorithms directly testable.

## Risks
- The C plugin ABI uses fixed-size `char app_name[128]` and primitive fields for ABI stability; app names can be truncated.
- Public manager APIs return copies of potentially large maps; admin/reporting callers should avoid high-frequency expensive snapshots.
- The header exposes many configuration controls whose interactions are subtle: limits enabled, reservations enabled, explicit user limits, controller limits, active-node threshold, IO pressure threshold, and automatic detail switching.
- Multiple maps share related keys but are updated in different paths; changes to report ingestion or detail-level switching need careful cleanup to avoid stale entries.
- `TrafficShapingPolicy::operator==` deliberately ignores controller fields, which is correct for persistence but easy to misuse for full equality.

## Test Signals
`unit_tests/mgm/TrafficShapingTests.cc` accesses many internals through `IN_TEST_HARNESS`, including config application helpers, delay calculations, controller behavior, stats aggregation, map cardinality, and policy expiry. The header’s public snapshot and setter API is also exercised indirectly by admin command code under `mgm/proc/admin/IoShapingCmd.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/shaping/TrafficShaping.hh -->
