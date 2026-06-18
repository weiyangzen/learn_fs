<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/shaping/TrafficShaping.cc -->
# sources/distributed-fs/eos/mgm/shaping/TrafficShaping.cc

## Purpose
Implements MGM traffic shaping. It ingests FST IO reports, computes per-app/uid/gid/node/disk rates, stores user and controller policies, computes delay configurations, publishes those configs to online FST nodes, and runs background loops for estimator updates and policy publication.

## Important APIs and Functions
- `TrafficShapingPolicy::{GetEffectiveWriteLimit, GetEffectiveReadLimit, IsEmpty, IsActive, ToString}`: policy helpers combining persistent user limits/reservations and ephemeral controller limits.
- `TrafficShapingManager::ProcessReport`: normalizes node ids, calculates deltas from cumulative FST counters, suppresses spikes on first contact/restart/delayed reports, and updates runtime/cumulative maps.
- `TrafficShapingManager::UpdateEstimators`: consumes atomic accumulators into EMA windows (`1s`, `5s`) and SMA windows (`1s`, `5s`, `15s`, `60s`, `300s`).
- `TrafficShapingManager::CalculateDelayUs`: built-in feedback controller that adjusts per-entity microsecond delays using current rate, limit, pressure, sparse/idle handling, deadbands, and a max delay cap.
- `TrafficShapingManager::ApplyDefaultReservationController`: built-in app reservation controller. When reserved apps have meaningful deficits on pressured nodes, it applies controller limits to competing non-reserved apps, honoring minimum limits and active-rate thresholds.
- `TrafficShapingManager::UpdateTrafficShapingController`: gathers app rates and pressure, optionally invokes hot-reloaded `update_controller`, otherwise applies the default controller, then calls `ApplyControllerPolicyUpdates`.
- `TrafficShapingManager::UpdateLimits`: computes per-node `TrafficShapingFstIoDelayConfig` maps for app/uid/gid read/write, using either plugin `calculate_delay` or built-in delay logic, encodes configs with `SymKey::Base64`, and publishes them to FST node config.
- Policy CRUD (`SetUidPolicy`, `SetGidPolicy`, `SetAppPolicy`, remove/get methods): update maps, scale existing delays on effective limit changes, and persist user policy JSON.
- `SerializePoliciesUnlocked` / `LoadPoliciesFromString`: convert policy maps to/from protobuf JSON while deliberately excluding controller-only fields from persistent serialization and retaining controller-only runtime entries during reload.
- `TrafficShapingManager::LoadPluginIfModified`: hot-reloads `/etc/eos/traffic_shaping_plugin.so` and resolves C symbols `calculate_delay` and `update_controller`.
- `TrafficShapingEngine::ApplyConfig`, `Start`, `StopRuntime`, `EstimatorsUpdate`, `FstIoPolicyUpdate`, `FstTrafficShapingEnabledUpdate`: own config replay, runtime threads, queue draining, periodic updates, and FST enable/config sync.

## Control Flow
FSTs send serialized `FstIoReport` payloads to `TrafficShapingEngine::ProcessSerializedFstIoReportNonBlocking`; the engine drops reports if not running, parses protobuf, then appends to a bounded queue of 500 reports. The estimator thread periodically swaps the queue, calls `ProcessReport` for each report, updates processed-report metrics, computes EMA/SMA estimators from accumulators, applies automatic detail-level switching, and garbage-collects idle maps every 20 seconds.

The policy-update thread periodically collects online node IO pressure from `FsView`, runs the reservation controller every 500 ms, and calls `UpdateLimits`. `UpdateLimits` prunes offline nodes, determines active policies, constructs node-local and global rate maps, decides whether each app/uid/gid read/write policy should emit a delay, carries prior node delay forward, applies delay algorithms, encodes protobuf configs, and publishes changed or stale configs every 5 seconds through `SetConfigMember(FST_TRAFFIC_SHAPING_IO_LIMITS, encoded, true)`.

Config replay reads global FsView config keys for enable state, policy JSON, thread periods, detail level, automatic detail thresholds, limits/reservations toggles, controller minimum limit, active node threshold, IO pressure threshold, and garbage collection idle time. Start/stop intentionally avoid immediate FST sync while config replay may hold `ViewMutex`; a separate sync thread pushes enabled/config state every 5 seconds.

## State and Persistence
The manager owns runtime maps for node stream baselines, global/node/disk/detailed rates, cumulative stats, projected app/uid/gid/node totals, policies, per-node pending delay configs, last published configs, plugin handles, and loop timing stats. `mMutex` protects most maps; atomics hold toggles and thresholds. `mPluginMutex` protects plugin function pointers while hot-reloading.

Persistent state flows through `FsView::gFsView.SetGlobalConfig`:
- `TRAFFIC_SHAPING_POLICIES_CONFIG`: user policy JSON for app/uid/gid limits/reservations/enabled flags.
- `TRAFFIC_SHAPING_ENABLE_CONFIG`, detail-level keys, limits/reservations toggles, controller min limit, active node threshold, IO pressure threshold, garbage collection idle, and base64-encoded `TRAFFIC_SHAPING_THREAD_PERIODS`.
Ephemeral controller limits and update timestamps are runtime-only and intentionally omitted from JSON serialization. FST node-local effective delays are also runtime outputs, published to node config rather than stored as global policy.

## Dependencies and Integration Points
Depends on `proto/TrafficShaping.pb.h`, protobuf JSON utilities, EOS `FsView`, `XrdMgmOfs`, `common/SymKeys`, `common/AssistedThread`, `SlidingWindowStats`, and `IoStatsKey`. FST report ingestion is wired from `mgm/fsview/FsView.cc`; `XrdMgmOfs` owns `mTrafficShapingEngine`; admin commands in `mgm/proc/admin/IoShapingCmd.cc` and `NsCmd.cc` inspect and modify this engine/manager. FSTs consume `FST_TRAFFIC_SHAPING_ENABLE_TOGGLE`, `FST_TRAFFIC_SHAPING_STATS_THREAD_PERIOD`, `FST_TRAFFIC_SHAPING_DETAIL_LEVEL`, and `FST_TRAFFIC_SHAPING_IO_LIMITS`.

## Risks
- Large shared maps are protected by a single `shared_mutex`; high-frequency reports plus admin queries/policy updates may contend.
- `SyncTrafficShapingEnabledWithFst` and `SyncTrafficShapingConfigWithFst` reacquire `ViewMutex` once per node after first reading online names; node state can change between the two steps, though lookup is checked.
- Plugin callbacks are trusted C ABI code loaded from `/etc/eos/traffic_shaping_plugin.so`; bad plugins can block, crash, or return pathological delay/limit values.
- The report queue drops oldest entries at 500; under sustained overload, rate estimates may underrepresent traffic.
- Missing node IO pressure is treated as `kUnknownIoPressure = 1.0` in several paths, which biases toward conservative throttling when pressure data is absent.
- Policy serialization persists user changes but not controller-only state; this is intentional, but operators may need clear diagnostics when runtime limits disappear on restart/expiry.
- `strncpy` into `AppState::app_name[128]` truncates long app names for plugin/controller exchange, risking policy collisions in plugin outputs.

## Test Signals
`unit_tests/mgm/TrafficShapingTests.cc` covers config replay constraints, toggle propagation, garbage-collection clamping, active node thresholds, controller-only ephemeral policy behavior, loop metric separation, detail toggles, aggregation modes, map cardinality, cumulative-stat pruning, controller limit expiry, reserved app IO pressure, delay seeding/release/deadbands, default reservation controller behavior, and delay emission predicates. Runtime integration with real FST node config publication and plugin hot reload is harder to test and should be validated in integration/system tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/shaping/TrafficShaping.cc -->
