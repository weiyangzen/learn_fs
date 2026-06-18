# Research: subset-b-007049

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/routeendpoint/RouteEndpoint.cc -->
# sources/distributed-fs/eos/mgm/routeendpoint/RouteEndpoint.cc

## Purpose
Implements `eos::mgm::RouteEndpoint`, the MGM-side representation of a route target used by path routing. The file provides parsing/formatting for `<fqdn>:<xrd_port>:<http_port>`, move assignment, and active health/status probing through XRootD.

## Important APIs and Functions
- `RouteEndpoint::operator=(RouteEndpoint&&)`: moves/copies endpoint fields into an existing endpoint. It swaps the hostname and copies ports plus atomic status flags.
- `RouteEndpoint::ParseFromString(const std::string&)`: tokenizes on `:`, expects exactly three tokens, parses XRootD and HTTP ports with `std::stoul`, and validates the hostname/IP through `eos::common::ValidHostnameOrIP`.
- `RouteEndpoint::ToString() const`: serializes the endpoint back to `fqdn:xrd_port:http_port`.
- `RouteEndpoint::UpdateStatus()`: builds a `root://host:port//dummy?xrd.wantprot=sss,unix` URL, pings it, then sends an opaque query `/?mgm.pcmd=is_master` to determine master status.

## Control Flow
Parsing is intentionally narrow: token count must be exactly three, both port fields must parse as unsigned integers, and invalid hostnames reject the endpoint. `UpdateStatus()` has three stages: URL construction/validation, `XrdCl::FileSystem::Ping(1)` online check, then an XRootD opaque query for master detection. Any invalid URL or ping failure clears both `mIsOnline` and `mIsMaster`; a successful ping sets online before master probing.

The master query branch is counterintuitive at first read: if `fs.Query(...).IsOK()` is false, it logs that the host is running as master but sets `mIsMaster = false`; if the query succeeds, it logs NOT master but sets `mIsMaster = true`. This may reflect endpoint-side command semantics, but the log strings and stored booleans appear inverted and should be treated as a risk signal.

## State and Persistence
The file mutates only in-memory state: hostname, two port fields, and atomic online/master flags. There is no direct persistence. The status flags are public in the header and are consumed by routing logic/tests, so external code can also set them without `UpdateStatus()`.

## Dependencies and Integration Points
Depends on `common/StringConversion.hh` for tokenization, `common/ParseUtils.hh` for hostname/IP validation, EOS logging through `LogId`, and XRootD client classes `XrdCl::URL`, `XrdCl::FileSystem`, `XrdCl::Buffer`, and `XrdCl::XRootDStatus`. It integrates with `PathRouting`, `RouteCmd`, and the MGM build target that includes `routeendpoint/RouteEndpoint.cc`.

## Risks
- `std::stoul` is not range-checked against `uint32_t` before assignment, so oversized numeric strings can wrap/truncate after parsing depending on platform width.
- Ports are not constrained to valid TCP port range.
- The apparent master-query log/boolean inversion in `UpdateStatus()` is a behavioral hotspot.
- `UpdateStatus()` allocates `XrdCl::Buffer* response` and manually deletes it; early returns before allocation are safe, but future edits should avoid leaks by using RAII if ownership semantics allow it.
- Move assignment copies atomic values but does not reset the moved-from flags or ports.

## Test Signals
`sources/distributed-fs/eos/unit_tests/mgm/RoutingTests.cc` covers valid/invalid parsing, endpoint equality, and routing use with manually set `mIsOnline`/`mIsMaster` flags. There is no direct unit test signal for live XRootD `UpdateStatus()` behavior or the master-query branch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/routeendpoint/RouteEndpoint.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/routeendpoint/RouteEndpoint.hh -->
# sources/distributed-fs/eos/mgm/routeendpoint/RouteEndpoint.hh

## Purpose
Declares the `eos::mgm::RouteEndpoint` class used to describe MGM path-routing redirect targets. The class stores endpoint identity, XRootD/HTTP ports, and online/master status flags while exposing parsing, serialization, equality, and status-refresh operations.

## Important APIs and Types
- `RouteEndpoint()`: default endpoint with offline/non-master status and zero ports.
- `RouteEndpoint(const std::string&, uint32_t, uint32_t)`: constructs an endpoint from FQDN and ports, initially offline and non-master.
- Move constructor and move assignment: enable insertion into containers and transfer into routing tables.
- `ParseFromString`, `ToString`, `UpdateStatus`: implemented in the `.cc` file.
- `GetHostname()`, `GetXrdPort()`, `GetHttpPort()`: inline accessors.
- `operator==` / `operator!=`: compare only endpoint identity fields, not online/master status.
- Public `std::atomic<bool> mIsOnline` and `mIsMaster`: runtime routing status exposed for direct manipulation by routing code/tests.

## Control Flow and Usage Contract
The header establishes a two-phase endpoint lifecycle: construct or parse identity first, then update or externally set status. `PathRouting` can then use the endpoint to pick redirect destinations. Equality ignores status, so duplicate detection is based on host and ports rather than health.

## State and Persistence
State is entirely in-memory. Persistent route definitions are likely stored/managed by surrounding MGM routing configuration code, while this type carries the parsed endpoint. Atomic booleans allow status updates and reads from multiple threads, but hostname and ports are not atomic and should be considered immutable after publishing unless protected externally.

## Dependencies and Integration Points
Includes `mgm/Namespace.hh` for the MGM namespace, `common/Logging.hh` for `eos::common::LogId`, and C++ string/integer headers. The class is referenced by `mgm/pathrouting/PathRouting.hh`, user route commands, and `unit_tests/mgm/RoutingTests.cc`.

## Risks
- Public mutable atomic flags make status manipulation easy but bypass invariants.
- The type has move support but no explicit copy constructor/assignment, largely because atomics are not copyable; callers need move semantics.
- Accessors return ports as `int` even though storage is `uint32_t`; values above `INT_MAX` would be lossy if admitted by parsing.
- Equality ignoring status is useful for route identity but can surprise callers expecting full object equality.

## Test Signals
`RoutingTests.cc` validates construction/parsing failures, equality/inequality, duplicate prevention in `PathRouting`, and routing decisions when status flags are manually set. Header-only API risks around port range and copy/move constraints are not directly covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/routeendpoint/RouteEndpoint.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/scheduler/Scheduler.cc -->
# sources/distributed-fs/eos/mgm/scheduler/Scheduler.cc

## Purpose
Implements the MGM file placement and access scheduler facade. It tries the newer `mgm/placement/FsScheduler` flat scheduler first and falls back to the legacy `GeoTreeEngine` when a space is configured for geotree placement or when flat access/placement cannot satisfy the request.

## Important APIs and Functions
- Static state:
  - `Scheduler::pMapMutex`: protects `schedulingGroup`.
  - `Scheduler::schedulingGroup`: maps group tags or `uid:gid` strings to the next `FsGroup*` to try for rotating geotree placement.
- `Scheduler::getRequiredReplicas(unsigned long lid)`: returns `LayoutId::GetStripeNumber(lid) + 1` as `uint8_t`.
- `Scheduler::FlatSchedulerFilePlacement(PlacementArguments*)`: builds `placement::PlacementArguments`, honors explicit scheduling strategy override unless it is `kGeoScheduler`, calls `gOFS->mFsScheduler->schedule`, and copies selected fsids.
- `Scheduler::FilePlacement(PlacementArguments*)`: primary placement API; fast path through flat scheduler, fallback through `gOFS->mGeoTreeEngine->placeNewReplicasOneGroup`.
- `toGeoTreeSchedtype(...)`: local helper mapping scheduler type plus read/write mode to `GeoTreeEngine::SchedType`.
- `Scheduler::FlatSchedulerFileAccess(AccessArguments*)`: delegates access choice to `gOFS->mFsScheduler->access` unless the space strategy is geotree.
- `Scheduler::FileAccess(AccessArguments*)`: primary file access API; validates stripe availability and forced fsid, tries flat access, falls back to `GeoTreeEngine::accessHeadReplicaMultipleGroup`, then enforces `exclude_filesystems`.
- `Scheduler::ReshuffleFs(std::vector<unsigned int>&)`: rotates selected fsids by placing either min or max first based on parity of the fsid sum.

## Control Flow
Placement starts by calling `FlatSchedulerFilePlacement`; success returns immediately. If flat scheduling reports failure or a geotree strategy, the legacy path calculates `ncollocatedfs` from placement policy and layout type, derives an index tag from group tag or uid/gid, selects a scheduling group, and loops over groups. Groups already hosting replicas are tried first when geotree can resolve them from `alreadyused_filesystems`. Forced group selection fails immediately if the requested group cannot place all replicas. Non-forced placement rotates through `FsView::gFsView.mSpaceGroupView[spacename]`, updating `schedulingGroup` under `pMapMutex`.

Access starts with required stripe checks: RW needs `GetOnlineStripeNumber(lid)`, RO needs `GetMinOnlineReplica(lid)`. A forced fsid must already be one of the file locations. Flat access is attempted first. If it fails, geotree access marks locations tried via CGI as unavailable, then calls `accessHeadReplicaMultipleGroup`. After a successful scheduling decision, the method checks `exclude_filesystems` and, if needed, picks the first location not excluded and not unavailable; if none exists it returns `ENODATA`.

## State and Persistence
The only durable-in-process scheduler state here is `schedulingGroup`, used for group rotation fairness across placement calls. It is not persisted and is lost on MGM restart. All selected filesystem output is written through caller-provided vectors in `PlacementArguments` and `AccessArguments`.

## Dependencies and Integration Points
Depends heavily on global MGM state:
- `gOFS->mFsScheduler` for flat placement/access.
- `gOFS->mGeoTreeEngine` for geolocation-aware fallback.
- `FsView::gFsView.mSpaceGroupView` and `ViewMutex`; comments require callers to hold a read lock.
- `LayoutId` for stripe/layout decoding.
- `Quota::FilePlacement` delegates to `Scheduler::FilePlacement`.
Callers include file open/create paths in `mgm/ofs/XrdMgmOfsFile.cc`, user `File`/`Fileinfo` commands, and quota placement logic.

## Risks
- `FilePlacement` calls `FlatSchedulerFilePlacement` before validating `args`; callers rely on `PlacementArguments::isValid()`, but this function does not enforce it.
- `FlatSchedulerFilePlacement` assigns `ret.ids.begin() + n_replicas` without checking `ret.ids.size() >= n_replicas`; this depends on `mFsScheduler->schedule` contract.
- In the non-forced geotree path, `schedulingGroup[indextag]` is dereferenced through `find`; stale `FsGroup*` values could be hazardous if group objects are removed concurrently or not present in the current space.
- The required external `FsView::ViewMutex` locking is a sharp API contract; misuse can race with `mSpaceGroupView` and node state.
- `ReshuffleFs` accumulates fsids into an `int`, which can overflow for large vectors/high fsids, though only parity matters.
- `FlatSchedulerFileAccess` constructs `std::string spaceName(args->forcedspace)` without null checks; callers must set `forcedspace` before selecting flat access.

## Test Signals
The lower-level placement subsystem has broad coverage in `unit_tests/mgm/placement/SchedulerTests.cc` and `FsSchedulerTests.cc`, including flat scheduler strategies, excluded fsids, forced groups, weighted strategies, and concurrency. `test/microbenchmarks/mgm/BM_FlatScheduler.cc` benchmarks flat strategies. Direct tests for this facade’s geotree fallback, `FileAccess` post-filtering, and stale `schedulingGroup` rotation are less obvious.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/scheduler/Scheduler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/scheduler/Scheduler.hh -->
# sources/distributed-fs/eos/mgm/scheduler/Scheduler.hh

## Purpose
Declares the MGM scheduler facade used by file creation, replica placement, and file access paths. It defines placement/access argument bundles, placement policies, scheduler modes, and static scheduling entry points.

## Important APIs and Types
- `enum tPlctPolicy { kScattered, kHybrid, kGathered }`: controls locality/collocation of stripes.
- `enum tSchedType { regular, draining }`: distinguishes normal scheduling from draining workflows.
- `PlacementArguments`: input/output carrier for file placement:
  - Inputs include space name, path, group tag, layout id, inode, placement policy, target geotag, truncation flag, forced group index, booking size, scheduler type, optional strategy override, and virtual identity.
  - Outputs/mutable inputs include already-used fsids, selected fsids, excluded fsids, data proxies, and firewall entry points.
  - Builder helpers `setFileParams`, `setFsParams`, and `setPlctParams` reduce call-site argument ordering mistakes.
  - Strong wrapper structs `Path`, `GroupTag`, `Lid`, `BookingSize` plus namespace helpers make typed construction easier.
- `AccessArguments`: input/output carrier for access scheduling:
  - Inputs include forced fsid/space, tried CGI, layout id, inode, RW flag, booking size, scheduler type, virtual identity, file locations, and excluded fsids.
  - Outputs include proxies, firewall entry points, selected layout index, and unavailable fsids.
- Static functions: `FilePlacement`, `FlatSchedulerFilePlacement`, `FileAccess`, `FlatSchedulerFileAccess`, `getRequiredReplicas`, placement policy string conversion, and `ReshuffleFs`.

## Control Flow and Usage Contract
The header documents that `FilePlacement` and `FileAccess` must be called with `FsView::gFsView::ViewMutex` locked. `isValid()` methods provide precondition checks but are not enforced automatically by the implementations. Layout validity for placement includes a replica count guard: `GetStripeNumber(lid) + 1` must fit below `std::numeric_limits<uint8_t>::max()`.

## State and Persistence
The class itself is a static facade. It declares process-local state `pMapMutex` and `schedulingGroup` for rotating geotree group choices. Placement/access results are returned by mutating caller-owned vectors and scalar pointers; nothing in the header is persisted to disk/config.

## Dependencies and Integration Points
Includes EOS logging, filesystem metadata types, layout id helpers, MGM namespace setup, and `mgm/fsview/FsView.hh`. The public argument structs depend on `eos::common::VirtualIdentity`. The scheduler is used by quota and MGM file command/open paths, while flat placement depends on `mgm/placement` implementations in the `.cc` file.

## Risks
- Raw pointers dominate the argument structs. `isValid()` catches many required fields, but optional fields and implementation assumptions such as `forcedspace` for flat access remain caller-sensitive.
- Strong types cover only placement file parameters; access arguments still use direct field mutation.
- `PlctPolicyFromString` returns `int` rather than `std::optional<tPlctPolicy>` or the enum type, requiring callers to handle `-1`.
- `getRequiredReplicas` truncates to `uint8_t`; the placement argument guard exists but can be bypassed if callers invoke the helper directly.

## Test Signals
Indirect coverage comes from file placement and flat scheduler tests under `unit_tests/mgm/placement`, plus integration call sites in quota and file open/create paths. The `PlacementArguments` builder and `AccessArguments::isValid()` are simple enough but do not appear to have dedicated unit coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/scheduler/Scheduler.hh -->

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
