# subset-b-008464 research

Grouped research for the requested FoundationDB data distributor files. Each source section is wrapped for reconciliation into the matching source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/AuditUtilsTests.cpp -->
# `sources/storage-engines/foundationdb/fdbserver/datadistributor/AuditUtilsTests.cpp`

## Purpose

This file is a Flow unit-test translation unit for audit helper routines declared in `fdbclient/AuditUtils.h`. It verifies range-list normalization and bidirectional consistency checks between the KeyServers view and ServerKeys view of shard ownership. `forceLinkAuditUtilsTests()` exists only to keep the tests linked into the datadistributor test target.

## Important APIs and Test Cases

- `coalesceRangeList()` is tested for empty input, a single unchanged range, sorting of non-overlapping ranges, overlap merging, adjacency merging, and containment absorption.
- `rangesSame()` is tested for empty equivalence, empty-vs-non-empty mismatch, exact equality, equivalent coverage with different split points, mismatched begin/end boundaries, and gaps.
- `checkLocationMetadataConsistency()` is tested with per-server maps keyed by `UID`, exercising consistent ownership, missing ServerKeys entries, missing KeyServers entries, per-server range mismatches, multiple simultaneous errors, and both maps empty.
- `buildLocationMetadataMaps()` is tested as the production preparation path before calling `checkLocationMetadataConsistency()`, including missing ownership, phantom server ownership, shifted boundaries, and partial ownership.

## Control Flow

The file uses independent `TEST_CASE` blocks. Each block constructs `UID`s and `KeyRange`s, builds small `std::unordered_map<UID, std::vector<KeyRange>>` fixtures, calls one audit helper, and asserts either an empty result or specific error content. The production-path tests call `buildLocationMetadataMaps()` first, then pass `builtMaps.fromKeyServers` and `builtMaps.fromServerKeys` into the consistency checker.

## State and Persistence Behavior

The tests are pure in-memory checks. They do not create transactions, use actors, or write system keys. The only state is local vectors/maps and returned `LocationMetadataError` objects. Their persistence relevance is indirect: they validate logic used to compare durable KeyServers and ServerKeys metadata views elsewhere in the system.

## Dependencies and Integration Points

The file depends on `fdbclient/AuditUtils.h`, `fdbclient/FDBTypes.h`, and `flow/UnitTest.h`. It is compiled into the datadistributor unit-test target by the local CMake file. The tested helpers are also referenced by production data-distribution audit logic and storage-server ownership validation paths, so these tests guard common range-comparison semantics rather than datadistributor-only code.

## Risks and Edge Cases

The assertions check message substrings, which confirms error category but not the full diagnostic payload. The fixtures use simple printable keys and do not cover system key boundaries, empty ranges inside non-empty maps, duplicated server entries beyond vector coalescing, or very fragmented range lists. Because the tests rely on exact error counts in multi-error scenarios, future helper changes that aggregate or de-duplicate errors could require test updates even if audit behavior remains acceptable.

## Test Signals

This file is itself test coverage. Strong signals include split-point-insensitive equality, adjacency merging, and simultaneous detection of missing and mismatched server ownership. Missing signals include randomized/fuzzed range-list inputs and coverage for `buildOwnRangesFromServerKeysResult()` or raw KeyServers parsing, which are adjacent helpers in `AuditUtils.h` but outside this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/AuditUtilsTests.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/CMakeLists.txt -->
# `sources/storage-engines/foundationdb/fdbserver/datadistributor/CMakeLists.txt`

## Purpose

This CMake file defines the datadistributor sublibrary and its local tests. It collects all sources in the directory, builds them as a static Flow target named `fdbserver_datadistributor`, wires link and unit tests, and exposes the datadistributor include path to downstream targets.

## Important Build APIs

- `fdb_find_sources(FDBSERVER_DATADISTRIBUTOR_SRCS)` discovers source files under this directory according to FoundationDB's build helpers.
- `add_flow_target(STATIC_LIBRARY NAME fdbserver_datadistributor SRCS ...)` creates the static library target.
- `add_fdbserver_link_test(fdbserver_datadistributorlinktest fdbserver_datadistributor fdbserver_core)` ensures the datadistributor library links with core server code.
- `add_fdbserver_unit_test(fdbserver_datadistributor_test datadistributor fdbserver_datadistributor fdbserver_core)` creates the unit-test executable/category that picks up `TEST_CASE` registrations such as `AuditUtilsTests.cpp`, `DDRelocationQueue.actor.cpp`, and `DDShardTracker.cpp`.
- `configure_fdbserver_common_includes()`, `target_include_directories()`, and `target_link_libraries()` apply include and dependency wiring.

## Control Flow

The file is declarative. Source discovery runs first, then target creation, test target creation, include configuration, and final private linkage to `fdbserver_core`. The include directories are split between a public `${CMAKE_CURRENT_SOURCE_DIR}/include` path for exported datadistributor headers and a private current-source path for implementation-local headers such as `DDRelocationQueue.h`.

## State and Persistence Behavior

There is no runtime state. The build state it influences is target graph metadata: source membership, include search paths, static-library artifacts, and test executables. Since `fdb_find_sources()` is directory driven, adding or removing source files in this folder changes the library/test composition without needing explicit per-file edits here.

## Dependencies and Integration Points

The target links privately against `fdbserver_core`, while tests link both `fdbserver_datadistributor` and `fdbserver_core`. The public include directory lets other server code include headers under `fdbserver/datadistributor/...`. The private current-source include path supports local implementation includes like `"DDRelocationQueue.h"` without exporting that path as API.

## Risks and Edge Cases

Directory-wide source discovery is convenient but can accidentally compile experimental or generated files if they are placed under the source folder and match the helper's filters. Any missing dependency in `target_link_libraries()` may show up only in link tests or downstream targets. Public/private include separation is important: moving a header from `include/` to the implementation folder, or vice versa, changes what external targets can include.

## Test Signals

The file creates both a link test and unit-test target. The link test catches unresolved symbols and target dependency mistakes. The unit target provides the execution surface for Flow `TEST_CASE`s in this directory; failures in audit, queue, or tracker unit cases should be attributable through the `datadistributor` test category.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/DDRelocationQueue.actor.cpp -->
# `sources/storage-engines/foundationdb/fdbserver/datadistributor/DDRelocationQueue.actor.cpp`

## Purpose

This actor implementation is the core scheduler and executor for FoundationDB data-distribution relocations. It receives `RelocateShard` requests, coalesces/overwrites queued intent by key range, fetches source servers, throttles launches by source and destination server busyness, selects destination teams, invokes `moveKeys()`, updates shard-location metadata, handles data-move cancellation/cleanup, and runs background disk/read rebalance loops.

## Important APIs, Types, and Functions

- `RelocateData` wraps `RelocateShard` with queue/runtime metadata: key range, priority, reason, data-move reason/id, source and destination IDs, work factor, cancellability, parent split range, trace interval, optional restored `DataMove`, and optional bulk-load task.
- `ParallelTCInfo` adapts multiple `IDataDistributionTeam` instances into a single aggregate team-like object for metrics/in-flight accounting across regions.
- `Busyness` maintains fixed-point work ledgers by priority bucket; `canLaunch()`, `addWork()`, and `removeWork()` gate source and destination concurrency.
- `getSourceServersForRange()` reads source server membership through `IDDTxnProcessor::getSourceServersForRange()`.
- `DDQueue::queueRelocation()` merges incoming relocation intent into `queueMap`, truncates or cancels overlapping queued work, and starts source-fetch actors.
- `DDQueue::launchQueuedWork()` chooses launchable queued work, cancels contained in-flight actors, assigns data-move IDs, updates in-flight maps, applies busyness, and starts `dataDistributionRelocator()`.
- `cancelDataMove()` and `enqueueCancelledDataMove()` serialize cleanup of existing data-move metadata via `cleanUpDataMove()`.
- `dataDistributionRelocator()` is the main move actor. It cleans conflicting data moves, validates bulk-load state, retrieves metrics, repeatedly selects healthy destination teams, updates `ShardsAffectedByTeamFailure`, builds `MoveKeysParams`, runs `txnProcessor->moveKeys()`, tracks data-transfer completion, and finalizes physical-shard/bulk-load state.
- `rebalanceReadLoad()`, `rebalanceTeams()`, `BgDDLoadRebalance()`, and `getSrcDestTeams()` implement background mountain-chopper/valley-filler movement for disk and read load.
- `pipelineGateActor()` limits non-urgent relocation intake by `DD_MAX_PIPELINE_MOVES` while allowing cancellations and high-priority health moves to pass.
- `DDQueueImpl::run()` is the top-level actor loop for queue events, source fetch completions, data-transfer completions, relocation completions, metrics logging, background rebalancers, pipeline gate errors, and unhealthy relocation count requests.

## Control Flow

Incoming `RelocateShard`s pass through `pipelineGateActor()` unless they are cancellations or high-priority health moves. The run loop dispatches restore moves directly, cancellation messages to cleanup, and normal moves to `queueRelocation()`. `queueRelocation()` overlays the requested range in `queueMap`, cancels affected source-fetch actors, preserves higher health/boundary priorities when replacing queued work, and schedules new source-server fetches. Once sources are fetched, `completeSourceFetch()` indexes the relocation by each source server and triggers `launchQueuedWork()`.

Launch checks combine candidate relocations from affected sources or ranges. The queue refuses to launch if an overlapping in-flight move with adequate priority should continue, or if source busyness cannot accommodate the move after considering cancellable contained work. Launching removes queued entries, cancels contained in-flight actors, optionally cleans previous data moves, writes a new in-flight `RelocateData`, charges source busyness, increments active counts, and starts a relocator actor.

The relocator first makes the in-flight entry non-cancellable when location metadata is encoded, waits for prior cleanup, possibly revalidates bulk-load task metadata, and assigns or finalizes a data-move ID. It fetches shard metrics and optional parent metrics for split diagnostics. Destination team selection loops over team collections, using restore-specified teams or `GetTeamRequest` policies driven by priority, read rebalance, bulk load, physical-shard requirements, and "true best" preferences. If teams are unavailable or destinations are too busy, it delays and retries; restore/bulk-load cases can eventually fail with `data_move_dest_team_not_found`.

After destination selection, the actor updates `ShardsAffectedByTeamFailure::moveShard()` for new moves, charges data/read in-flight to destination teams, charges destination busyness, emits relocation decision traces, and calls `moveKeys()`. The move may complete in two phases when cross-DC optimization initially moves to one remote server and later expands to all extra IDs. Data-transfer completion and relocation completion are signaled separately, allowing busyness to be released before the whole actor finishes. On success it clears completed data-move tracking, records bytes/rate, calls `finishMove()`, updates `PhysicalShardCollection` when enabled, terminates bulk-load task state, and returns. Retryable move-key errors release destination accounting and loop; non-cancel errors propagate through the queue error promise.

## State and Persistence Behavior

Most queue state is in memory: `queueMap`, per-source `queue`, `fetchingSourcesQueue`, `fetchKeysComplete`, `inFlight`, `inFlightActors`, `dataMoves`, source/destination busyness maps, priority counters, pipeline counters, and moving-window byte-rate stats. Durable/persistent effects are mediated through `IDDTxnProcessor` and core move-key helpers: source lookup, data-move cleanup, `moveKeys()`, DD ignore switch reads, health metrics, and bulk-load task reads/updates. When `SHARD_ENCODE_LOCATION_METADATA` is enabled, data-move IDs are stored in metadata flows and `dataMoves` protects against overlapping cleanup/write races. Physical-shard updates remain in the in-memory `PhysicalShardCollection` but are keyed by data-move IDs derived from physical shard IDs.

## Dependencies and Integration Points

This file integrates with `DataDistributionTeam` for team selection and load metrics, `DDTxnProcessor` for database/system-key operations, `MoveKeys` for actual metadata changes, `ShardsAffectedByTeamFailure` for shard/team ownership maps, `PhysicalShardCollection` for physical shard reuse/transition, `BulkLoadTaskCollection` for bulk-load scheduling, server knobs for priorities/throttles, Flow actor primitives, trace/event-cache infrastructure, and simulation knobs/buggify paths. It also serves metrics requests from `DDShardTracker` through `getShardMetrics` and `getTopKMetrics` streams during relocation and rebalance decisions.

## Risks and Edge Cases

Correctness is sensitive to non-atomic updates between in-flight actor maps, `dataMoves`, and physical-shard maps; the file contains TODO comments around split-brain risk and future assertions. Queue replacement must preserve health/boundary priority or urgent recovery can be delayed. Source lists can become stale between fetch and launch. Busyness accounting must be released exactly once across transfer-complete, retry, cancellation, and error paths. Cross-region best-team readiness has a no-wait requirement before `moveShard()` to avoid missing failure notifications. Bulk-load tasks can become outdated after source launch but before cleanup completes, causing fallback or task failure. Physical shard selection can choose full or unhealthy remote teams and must force re-selection. Pipeline control deliberately bypasses urgent moves, so health storms can still produce high activity.

## Test Signals

The file includes `/DataDistribution/DDQueue/ServerCounterTrace`, which exercises periodic server-counter tracing with randomized teams/reasons/count types. Broader behavioral coverage likely comes from simulation workloads and datadistributor integration tests rather than local unit tests. Trace signals are extensive: queue size changes, pipeline full/clear, relocation begin/end, best-team stuck, destination busy, data-move conflicts, move rates, rebalance decisions, bulk-load state, and physical-shard retry counters.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/DDRelocationQueue.actor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/DDRelocationQueue.h -->
# `sources/storage-engines/foundationdb/fdbserver/datadistributor/DDRelocationQueue.h`

## Purpose

This header declares the relocation queue interface, queue data model, throttling helpers, constructor parameter bundle, and `DDQueue` class used by the data distributor to schedule and execute shard relocations. It is the local contract consumed by the actor implementation and by other datadistributor components that need queue status or construction.

## Important APIs and Types

- `IDDRelocationQueue` is the narrow external interface with `getUnhealthyRelocationCount()`.
- `RelocateData` is the queue's normalized relocation intent. It stores the key range, priority decomposition (`priority`, `boundaryPriority`, `healthPriority`), relocation/data-movement reasons, source/destination servers, data-move identity, work factor, trace interval, optional parent split range, optional restored `DataMove`, and optional `DDBulkLoadEngineTask`.
- `RelocateData::isHealthPriority()` and `isBoundaryPriority()` classify server-knob priorities into health and boundary buckets.
- `RelocateDecision` is a trace/reporting view over a relocation, destinations, extra IDs, metrics, and optional parent metrics.
- `Busyness` declares per-priority fixed-point capacity accounting for launch throttling.
- `DDQueueInitParams` groups constructor dependencies: distributor ID, move-keys lock, transaction processor, team collections, failure tracker, physical shard collection, bulk-load collection, average-shard-size stream, team sizes, relocation input/output streams, and metric request streams.
- `DDQueue::DDDataMove` stores a data-move ID plus an optional cleanup future.
- `DDQueue::ServerCounter` tracks proposed/queued/launched source and destination counts per server and `RelocateReason`, with bounded tracing support.
- `DDQueue` exposes state fields and internal methods used by the actor implementation: queueing, launching, validation, source fetch completion, cancellation, counter refresh, rebalance helpers, and static `run()`.

## Control Flow Contract

The header shows the queue's staged model. Relocations enter through `input`, are produced downstream through `output`, and flow through source-fetch queues, per-source queues, in-flight maps, and completion streams. `queueRelocation()` accepts raw `RelocateShard`s and may populate `serversToLaunchFrom`. `completeSourceFetch()` moves source-fetched work into launchable per-server queues. `launchQueuedWork()` overloads support launching by key range, affected source set, or single relocation. `dataTransferComplete` and `relocationComplete` are separate streams because capacity release and full cleanup happen at different times.

## State and Persistence Behavior

The class stores in-memory scheduling state: pipeline counters, active/queued relocation counts, source and destination busyness maps, `queueMap`, `fetchingSourcesQueue`, per-source `queue`, `lastAsSource`, `inFlight`, `inFlightActors`, `dataMoves`, priority counters, unhealthy counts, and moving-window byte rate. Persistent actions are not declared directly here, but the state references the `IDDTxnProcessor`, `MoveKeysLock`, and `DDDataMove` cleanup futures that the implementation uses to mutate location metadata and clean durable data-move state.

## Dependencies and Integration Points

The header depends on `fdbserver/datadistributor/DataDistribution.h` for core DD types (`RelocateShard`, `DataMove`, `TeamCollectionInterface`, `PhysicalShardCollection`, bulk-load types, metric requests) and `MovingWindow.h` for move-rate accounting. `DDQueue` integrates with Flow primitives (`PromiseStream`, `FutureStream`, `AsyncVar`, `FlowLock`, actor maps), team collections for destination selection, failure tracking for shard/team mapping, physical shard collection for physical moves, and bulk-load task collection for range-specific load operations.

## Risks and Edge Cases

Several invariants are visible in the data layout. `noErrorActors` must be destroyed last because other actors may use it. `queueMap`, per-source `queue`, and `fetchingSourcesQueue` must agree on whether a relocation has source servers. `inFlight`, `inFlightActors`, and `dataMoves` must stay range-aligned during cancellation and replacement. `priority_relocations` and `unhealthyRelocations` drive external health signals, so incorrect increments/decrements can block team removal or misreport DD health. `RelocateData` comparison determines set uniqueness through priority/start/random/range ordering; equality is not the set uniqueness predicate.

## Test Signals

The header itself has no tests, but it exposes `ServerCounter::randomCountType()` for the queue unit test in the actor file. Runtime validation is supported by `DDQueue::validate()` under expensive validation, and operational traces are backed by `ServerCounter::traceAll()`, `MovingData`, and physical-shard counter fields.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/DDRelocationQueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/DDShardTracker.cpp -->
# `sources/storage-engines/foundationdb/fdbserver/datadistributor/DDShardTracker.cpp`

## Purpose

This file implements shard metric tracking, shard splitting/merging, read-hot detection, metric query serving, storage-queue rebalance triggering, bulk-load shard boundary setup, and physical-shard collection maintenance for the data distributor. It decides when shard boundaries should change and sends `RelocateShard` requests to the relocation queue.

## Important APIs, Types, and Functions

- `getBandwidthStatus()` and `getReadBandwidthStatus()` classify write/read pressure from `StorageMetrics`.
- `updateMaxShardSize()` updates an `AsyncVar<Optional<int64_t>>` as estimated database size changes.
- `calculateShardSizeBounds()` computes dynamic shard bounds and flags read-hot shards.
- `trackShardMetrics()` waits on `IDDTxnProcessor::waitStorageMetrics()`, updates per-shard metrics, database/system size estimates, physical-shard metrics, and can emit move-out relocations for oversized/anonymous physical shards.
- `shardUsableRegions()` audits usable-region coverage from `ShardsAffectedByTeamFailure` and emits populate-region relocation if a shard has too few usable regions.
- `shardSplitter()`, `executeShardSplit()`, `shardMerger()`, and `shardEvaluator()` implement split/merge decisions and boundary changes.
- `restartShardTrackers()` replaces tracker actors for affected key ranges and starts metric, split/merge, and optional usable-region actors.
- `trackInitialShards()` initializes trackers from `InitialDataDistribution`, respecting user range boundaries, then sends `readyToStart`.
- `fetchShardMetrics()`, `fetchTopKShardMetrics()`, and `fetchShardMetricsList()` serve queue/rebalance metric requests with timeout behavior.
- `triggerStorageQueueRebalance()` selects a high-write shard from affected teams and emits `REBALANCE_STORAGE_QUEUE`.
- `DataDistributionTrackerImpl::run()` wires long-running services for logging, read-hot detection, metric streams, storage-queue requests, bulk-load shard requests, restart requests, and child actor errors.
- `trackKeyRangeInPhysicalShardMetrics()` and `PhysicalShardCollection::*` maintain physical-shard-to-team, key-range-to-physical-shard, metric, cleanup, and logging structures.

## Control Flow

Startup calls `DataDistributionTracker::run()`, stores stream handles and configuration snapshots, and delegates to `DataDistributionTrackerImpl::run()`. Initialization creates shard trackers for all initial shard intervals, splitting at user range boundaries. `readyToStart` is sent after tracker installation and initial size accounting begins; the max-shard-size updater starts after initial metrics are collected.

Each tracked shard has a metrics actor and a shard evaluator actor. The metrics actor waits until observed metrics leave the current bounds, updates estimates and `ShardMetrics`, and triggers read-hot or physical-shard move-out signals when needed. The evaluator waits for stats and max-shard-size availability, then repeatedly calculates whether the shard should split, merge, or wait for metric changes. Splits call `splitStorageMetrics()`, restart trackers in a nibbling order compatible with the relocation queue, define new shards in `ShardsAffectedByTeamFailure`, and emit split relocations for all but the kept subrange. Merges collect adjacent low-bandwidth shards forward and backward while respecting system boundaries, user range boundaries, bulk-load ranges, shard-count limits, max shard size, and low-bandwidth coalescing delay; successful merges restart one tracker and emit a merge relocation.

Metric request handlers aggregate metrics over intersecting tracked ranges, waiting for missing stats when possible and returning fallback/timed-out replies when necessary. Background service actors multiplex these request handlers with logging, read-hot range logging, storage-queue rebalance triggers, bulk-load shard boundary creation, and restart requests from failure tracking.

Physical-shard maintenance is updated from both metric tracking and relocation completion. The collection can initialize/restored physical shard mappings, select reusable physical shards for a primary team, find paired remote teams, generate new IDs, update metrics on key-range moves, detect anonymous-shard transition work, detect oversized physical shards, remove empty physical shards, and log physical-shard/team/server distributions.

## State and Persistence Behavior

The tracker owns in-memory range state through `KeyRangeMap<ShardTrackedData>* shards`, per-shard `AsyncVar<Optional<ShardMetrics>>`, `dbSizeEstimate`, `systemSizeEstimate`, `maxShardSize`, and child actors. Durable reads come through `IDDTxnProcessor` metric APIs and bulk-load metadata reads. Boundary changes are represented in memory immediately by restarting trackers and defining shards, then made durable indirectly by emitted `RelocateShard`s that the queue turns into `moveKeys()` operations. `PhysicalShardCollection` is in-memory bookkeeping keyed by data-move/physical-shard IDs; it is reconstructed or updated from data distribution metadata and relocation completion paths rather than writing directly here.

## Dependencies and Integration Points

This file integrates with `DDShardTracker.h`, `DDSharedContext.h`, `DataDistribution.h`, `ShardSizing`, `ShardsAffectedByTeamFailure`, `PhysicalShardCollection`, `BulkLoadTaskCollection`, and `IDDTxnProcessor`. It emits relocation requests consumed by `DDRelocationQueue`, serves metric streams used by queue destination selection and background rebalancing, uses `anyZeroHealthyTeams` to suppress merges when no healthy teams exist, and uses Flow actor/task priorities and trace events for scheduling and observability.

## Risks and Edge Cases

Shard-boundary correctness is sensitive to ordering. `executeShardSplit()` deliberately avoids asking the queue to split one shard into three pieces at once. Merges must not cross `systemKeys` boundaries, user range config boundaries, or active bulk-load ranges. Metric unavailability can stall decisions; timeout fallbacks can return intentionally large metrics to avoid unsafe movement. Physical-shard metrics are approximate in some multi-shard/move-out paths, including even division across multiple outgoing physical shards. `SafeAccessor` protects actors from accessing a destroyed tracker, but any missed guard could be a use-after-free risk. Bulk-load ranges temporarily disable normal boundary changes to avoid disrupting load tasks.

## Test Signals

Local tests include `/DataDistributor/Tracker/FetchTopK`, currently a minimal empty-range timeout/result test, and `/DataDistributor/Tracker/CrossesCriticalSystemBoundary`, which covers the system-key boundary predicate used by merge feasibility. Many important behaviors rely on simulation/integration coverage and trace probes: split/merge trace events, `DDTrackerStats`, read-hot logs, storage-queue rebalance traces, physical-shard consistency assertions in simulation, and code probes for shard split/merge paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/DDShardTracker.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/DDSharedContext.cpp -->
# `sources/storage-engines/foundationdb/fdbserver/datadistributor/DDSharedContext.cpp`

## Purpose

This file provides the constructor/destructor definitions for `DDSharedContext`, the reference-counted object that carries common data-distributor state shared by tracker, relocation queue, team collections, and related DD components.

## Important APIs and Types

- `DDSharedContext::DDSharedContext()` leaves members at their header defaults.
- `DDSharedContext::DDSharedContext(const DataDistributorInterface& iface)` delegates to the UID constructor using `iface.id()` and then stores the full interface.
- `DDSharedContext::DDSharedContext(UID id)` allocates a shared `DDEnabledState`, stores the distributor ID, and creates a `ShardsAffectedByTeamFailure` instance.
- `DDSharedContext::~DDSharedContext()` is defaulted in the implementation file, allowing smart/reference-counted members to clean themselves up.

The associated header exposes `ddEnabledState`, `interface`, `ddId`, `MoveKeysLock`, `trackerCancelled`, `configuration`, `shardsAffectedByTeamFailure`, tracker/queue/team-collection references, and convenience methods such as `id()`, `markTrackerCancelled()`, `usableRegions()`, and `isDDEnabled()`.

## Control Flow

Construction is intentionally simple. The interface constructor is the production path when a `DataDistributorInterface` already exists; it ensures `ddId` and the stored interface are consistent. The UID constructor is the lower-level initializer for tests or setup paths that only have an ID. No actor is started here; consumers attach `DataDistributionTracker`, `DDQueue`, and team collection references after constructing the shared context.

## State and Persistence Behavior

The context is in-memory shared state. It does not read or write database keys. The `DDEnabledState` is heap-owned by a `unique_ptr` and intentionally stable because other components, including snapshot-related code, can share the underlying object. `trackerCancelled` is a lifecycle flag used to protect tracker actors. The context owns a fresh `ShardsAffectedByTeamFailure` reference in the UID constructor, which becomes the shared shard/team map used by tracker and queue components.

## Dependencies and Integration Points

The implementation includes `DDSharedContext.h` and `DDRelocationQueue.h`, tying the shared context to the queue type declared in the private header. The header depends on `DataDistributorInterface`, `MoveKeys`, `DDShardTracker`, `ShardsAffectedByTeamFailure`, and `DDTeamCollection`. The context is an integration hub rather than a behavior-heavy component.

## Risks and Edge Cases

The default constructor does not initialize `ddEnabledState`, `ddId`, or `shardsAffectedByTeamFailure` beyond header defaults, so consumers must know whether a default context is only a placeholder. The UID/interface constructors allocate the critical shared objects; code paths that use the default constructor and then call methods like `isDDEnabled()` before initialization would be unsafe. Because `trackerCancelled` is read by actor-safe accessors, its lifetime must outlive actors that reference it.

## Test Signals

There are no local tests in this file. Useful validation is indirect: DD startup tests should confirm context construction wires a shared `ShardsAffectedByTeamFailure`, queue, tracker, and team collections; tracker cancellation tests or simulation failures should exercise `trackerCancelled` lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/DDSharedContext.cpp -->
