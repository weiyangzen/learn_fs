# Research Report: subset-b-008469

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/MockGlobalState.cpp -->
## sources/storage-engines/foundationdb/fdbserver/datadistributor/MockGlobalState.cpp

Purpose: implements the mock in-memory data plane used by the datadistributor tests. `MockGlobalState` models cluster topology, key-to-team mapping, storage-server lists, key-location queries, storage metrics, and simple data operations without running real transactions. `MockStorageServer` models the parts of storage server behavior needed by DD: shard ownership state, byte samples, disk usage, storage metrics RPCs, fetch-key completion, and read/write cost signals.

Important APIs and functions: `MockGlobalStateImpl::waitStorageMetrics()` and `splitStorageMetrics()` provide NativeAPI-like metric loops over mock `getKeyRangeLocations()`. `MockStorageServerImpl::waitMetricsForReal()` and `waitFetchKeysFinish()` serve metric waits and simulate key fetching. `MockStorageServer::{setShardStatus,coalesceCompletedRange,twoWayShardSplitting,threeWayShardSplitting,removeShard,sumRangeSize}` maintain `serverKeys`. `MockGlobalState::{initializeClusterLayout,initializeAsEmptyDatabaseMGS,addStorageServer,addStoragePerProcess,getKeyLocation,getKeyRangeLocations,runAllMockServers,get,set,clear,getRange,clearRange}` are the public mock cluster surface.

Control flow: initialization builds topology objects, process locality, seed processes, initial `MockStorageServer` objects, and an all-key team assignment in `shardMapping`. Key-location reads query `ShardsAffectedByTeamFailure`, prefer destination teams for in-flight shards, and return `KeyRangeLocationInfo` backed by mock storage interfaces. Metrics waits repeatedly collect locations, call storage metric helpers, retry on wrong-shard/all-alternatives/future-version errors, and delay to avoid spin. Data operations look up source servers from `shardMapping`, apply reads/writes/clears to all replicas or a random replica, and update metric samples and disk counters.

State and persistence: all state is process-local and transient. `allServers` mirrors `serverListKeys`; `shardMapping` mirrors `keyServers`; each mock server's `serverKeys` mirrors server key ranges with `MockShardStatus` plus byte size. `usedDiskSpace`, `totalDiskSpace`, `CommonStorageCounters`, and `IStorageMetricsService::metrics.byteSample` model storage load. There is no durable persistence; correctness depends on symmetric updates between mock key-server state and mock server-key state.

Dependencies and integration: this file integrates with `MockGlobalState.h`, `DataDistribution.h`, `ShardsAffectedByTeamFailure`, `StorageMetrics`, `LocationInfo`, `serveStorageMetricsRequests`, Flow actors, deterministic randomness, and server/client knobs. It is consumed by `DDMockTxnProcessor` and mock DD tests as the backing database and key-location service.

Risks: shard status transitions are asserted and can fail hard if move sequencing diverges from the mock contract. Split helpers divide sizes evenly, so metrics are intentionally approximate. Range operations rely on boundary variables and partial-shard estimates; these are good enough for tests but not a substitute for real storage semantics. `serverIsDestForShard()` requires destination mapping and server status to agree, so asymmetric move/fetch updates can make test failures hard to diagnose. The mock supports only a simplified, mostly single-region model.

Test signals: embedded unit tests cover empty database initialization, two/three-way server-key splitting, status transitions/coalescing, key-location and range-location lookup, storage metric waits, and simple data ops. Useful future signals include tests for failed-server removal, partial-range `getRange/clearRange`, in-flight source versus destination selection, and fetch-key status transitions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/MockGlobalState.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/MovingWindow.h -->
## sources/storage-engines/foundationdb/fdbserver/datadistributor/MovingWindow.h

Purpose: defines a small template utility for uniformly weighted moving-window averages over recent samples. It is intended for DD telemetry such as recent bytes-moved rates, where an exact windowed average is preferable to exponential smoothing.

Important APIs and types: `template<class T> class MovingWindow` exposes `MovingWindow(double timeWindow)`, `addSample(T)`, `getAverage()`, and `getTotal()`. Internal fields are `previous`, `total`, `maxDequeSize`, `Deque<std::pair<double,T>> updates`, `interval`, and `previousPopTime`.

Control flow: `addSample()` increments the lifetime total, appends `(now(), sample)`, and evicts oldest entries if the deque exceeds a knob-derived memory cap. `getAverage()` either divides samples accumulated since initialization or forced eviction by elapsed time, or evicts entries older than `now() - interval` and divides the active sum by the fixed interval. Eviction moves values into `previous`, leaving `total - previous` as active-window mass.

State and persistence: state is in-memory only. `total` is monotonic over object lifetime, while `previous` tracks samples outside the active window or evicted by memory pressure. `previousPopTime` is used to avoid dividing by the full interval before the window has aged in or after forced eviction.

Dependencies and integration: uses Flow `Deque`, `now()`, and `SERVER_KNOBS->MOVING_WINDOW_SAMPLE_SIZE`. It is a header-only utility and can be embedded in DD actors without a separate implementation file.

Risks: `getAverage()` may divide by a very small elapsed time immediately after construction or eviction. `maxDequeSize` depends on `sizeof(std::pair<double,T>)`; very large `T` or an unexpectedly low knob can force frequent eviction and reduce window fidelity. It assumes `T` supports zero construction, addition, subtraction, and division-compatible conversion to `double`.

Test signals: no local unit tests in this header. Useful tests would cover cold-start averaging, expiration, max-deque eviction, zero/near-zero elapsed time behavior, and non-integer sample types.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/MovingWindow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/ShardsAffectedByTeamFailure.cpp -->
## sources/storage-engines/foundationdb/fdbserver/datadistributor/ShardsAffectedByTeamFailure.cpp

Purpose: implements the DD-side index that maps shards to current and previous teams, teams to affected shards, and storage servers to shard counts. Team trackers use it to identify which shards must be relocated when teams degrade, while mock DD uses it as the key-server mapping.

Important APIs and functions: lookup methods include `getShardsFor()`, `hasShards()`, `getNumberOfShards(UID|Team)`, `getTeamsForFirstShard()`, `getTeamsFor()`, `getSourceServerIdsFor()`, `getAllRanges()`, and `intersectingRanges()`. Mutation methods include `defineShard()`, `moveShard()`, `rawMoveShard()`, `finishMove()`, `assignRangeToTeams()`, `removeFailedServerForRange()`, and private `insert()/erase()` helpers.

Control flow: `defineShard()` splits/defines boundaries, collects existing current and previous teams, installs the new range, then re-inserts team-to-shard index rows for affected ranges. `moveShard()` changes ownership without changing boundaries; exact-contained shards are rewritten with destination teams and accumulated previous teams, while intersecting partial shards are unioned so failure reactions do not lose old team information. `finishMove()` clears previous-team vectors after a move completes. `rawMoveShard()` directly writes source/destination state for exact shard ranges. `assignRangeToTeams()` performs define, move, and finish in sequence.

State and persistence: the authoritative in-memory map is `KeyRangeMap<pair<vector<Team>, vector<Team>>> shard_teams`, where first is current source or destination and second is previous sources for in-flight shards. `team_shards` is a secondary set keyed by team and range. `storageServerShards` counts shard membership by server UID. There is no durable storage here; callers rebuild it from system keys or mock state.

Dependencies and integration: depends on `KeyRangeMap`, Flow reference counting, `UID`, `KeyRange`, and sorted `Team` semantics. It feeds `DDTeamCollection` team trackers, `DataDistributionTracker`, `DDTxnProcessor` removal flows, and `MockGlobalState` source/destination checks.

Risks: consistency depends on every mutation keeping `shard_teams`, `team_shards`, and `storageServerShards` synchronized. `getTeamsFor()` indexes by exact key in `KeyRangeMap`, so callers must understand range-map semantics. `removeFailedServerForRange()` mutates vectors in place while updating secondary indexes; missed erase/insert pairing would corrupt shard counts. Expensive `check()` is gated by validation knobs or force mode, so production paths may not catch drift immediately.

Test signals: no tests in this implementation file, but the mock global-state tests exercise `assignRangeToTeams()`, key-location lookups, and source/destination queries. Good focused tests would cover overlapping moves, queued splits/merges, server removal from both current and previous team vectors, and forced `check()` failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/ShardsAffectedByTeamFailure.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/SimulatedCluster.cpp -->
## sources/storage-engines/foundationdb/fdbserver/datadistributor/SimulatedCluster.cpp

Purpose: builds a minimal `BasicSimulationConfig` from `BasicTestConfig` for datadistributor and mock-global-state tests. It translates replication intent and optional role counts into a `DatabaseConfiguration` plus a simple machine/process layout.

Important APIs and functions: `generateBasicSimulationConfig()` is the exported function. Private helpers `getRedundancyMode()` maps minimum replication to `single`, `double`, or `triple`; `applyConfigurationString()` uses FoundationDB management parsing to fill the database config.

Control flow: generation chooses datacenter count from `singleRegion`, `simpleConfig`, and minimum replication, applies the redundancy mode, optionally forces simplified proxy/resolver/TLog counts, applies explicit overrides, sets `storageTeamSize`, applies log anti-quorum when provided, sets usable regions for single-DC configs, and computes a default or overridden machine count large enough for the storage team.

State and persistence: no persistent state. It returns a value object containing topology counts and `DatabaseConfiguration`.

Dependencies and integration: depends on `BasicTestConfig`/`BasicSimulationConfig` from `SimulatedCluster.h`, `DatabaseConfiguration`, and `buildConfiguration()` from the generic management API. `MockGlobalState` uses the result to create process locality and seed storage servers.

Risks: the helper is intentionally simplified and does not model all production simulation knobs. The redundancy string mapping is coarse; unusual replication policies or multi-region layouts need explicit extensions. Assertions assume `buildConfiguration()` recognizes the selected mode.

Test signals: indirectly exercised by `MockGlobalState.cpp` tests that call it before cluster initialization. Focused tests could validate simple versus multi-DC machine counts, override precedence, and ASAN-specific machine-count behavior if that field is later consumed here.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/SimulatedCluster.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/TCInfo.cpp -->
## sources/storage-engines/foundationdb/fdbserver/datadistributor/TCInfo.cpp

Purpose: implements storage-server, machine, machine-team, and server-team metric/state helpers used by `DDTeamCollection`. It turns storage metrics and health stats into team load, space, CPU, lagging-server, storage-queue, and in-flight accounting decisions.

Important APIs and functions: `TCServerInfoImpl::updateServerMetrics()` polls a server endpoint and updates lag/version/storage-queue signals. `serverMetricsPolling()` periodically combines storage metrics and health stats. `TCServerInfo` implements metrics access, store-type updates, desired-DC updates, queue-duration detection, team removal, space/load helpers, and destructor cleanup. `TCMachineInfo`, `TCMachineTeamInfo`, and `TCTeamInfo` implement locality grouping, stringification, membership, in-flight counters, load/read/cpu/space scoring, healthy-space checks, optimality checks, and metric refresh across team members.

Control flow: server metric polling races a metrics RPC with interface-change, removal, and retry-delay futures. Successful replies set `metrics` and notify `updated`; failures delay and retry, respecting the failure monitor to avoid tight loops. After each metrics update, version staleness and lag thresholds add/remove lagging zones in the collection. Optional storage-queue rebalancing tracks queue duration and emits `longStorageQueue` with throttling. Team methods aggregate per-server metrics and apply penalties for in-flight bytes or missing replies.

State and persistence: objects are in-memory DD control-plane state. `TCServerInfo` stores last known interface/class, store type, in-flight counters, metrics replies, health stats, queue timing, team memberships, AsyncVars, and promises. `TCTeamInfo` stores server refs, sorted IDs, health/configuration status, priority, UID, and eligibility counters. No database writes occur here; persistence is handled by callers such as team collection and transaction processors.

Dependencies and integration: integrates with `DDTeamCollection` for lagging-zone accounting and wiggle checks, `IDDTxnProcessor` for health stats, `StorageServerInterface` RPCs, `IFailureMonitor`, server knobs, `IDataDistributionTeam`, and Flow actor primitives.

Risks: many methods assume metrics are present and assert otherwise, so callers must refresh before scoring. Missing health stats count as 100% CPU, intentionally conservative but potentially noisy. `getLoadAverage()` doubles load when some replies are missing, a heuristic that can skew team selection. Lagging-zone cleanup in the destructor depends on `collection` still being valid unless `cancel()` has cleared it.

Test signals: no local unit tests in this file, but team-collection and DD tests should cover server metric polling, queue-triggered relocation, load-based team selection, and lagging-server accounting. Focused tests would help around interface-change races, failure-monitor retry, and queue hysteresis thresholds.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/TCInfo.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DDShardTracker.h -->
## sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DDShardTracker.h

Purpose: declares the shard tracker interface and concrete `DataDistributionTracker` state holder. The tracker watches shard sizes, metrics, hot ranges, physical shards, and bulk-load constraints, then emits `RelocateShard` work to the DD queue.

Important APIs and types: `IDDShardTracker` exposes readiness and request streams for shard metrics, top-K metrics, metrics lists, average shard bytes, storage-queue rebalance triggers, and bulk-load triggers. `DataDistributionTrackerInitParams` packages dependencies. `DataDistributionTracker` stores transaction processor, distributor ID, shard map pointer, actor collection, DB size/max-shard estimates, output stream, `ShardsAffectedByTeamFailure`, `PhysicalShardCollection`, `BulkLoadTaskCollection`, cancellation guard, read-hot stream, and user range config. Static `run()` wires external streams into the actor implementation.

Control flow: this header does not implement tracking, but it declares the lifecycle: construct from init params, run with initial data and request streams, update internal estimates, and answer synchronous `getAverageShardBytes()`. `SafeAccessor` is used by long-lived actors to avoid accessing a tracker after cancellation.

State and persistence: in-memory tracker state points at a longer-lived `KeyRangeMap<ShardTrackedData>`. Persistence is external: initial data comes from `InitialDataDistribution`, moves go through data-movement metadata, and user range config snapshots come from DD configuration.

Dependencies and integration: depends on `DataDistribution.h`, `IDDTxnProcessor`, `ShardsAffectedByTeamFailure`, `PhysicalShardCollection`, `BulkLoadTaskCollection`, Flow streams, and DD queue relocation output. `DDSharedContext` owns a tracker reference.

Risks: `shards` and `trackerCancelled` are raw pointers with lifetime assumptions; misuse can become memory unsafe. `getAverageShardBytes()` assumes `maxShardSize` is present. Actor cancellation ordering is central, hence the explicit safe accessor and destructor.

Test signals: tests should validate cancellation, request stream service, average shard bytes updates, bulk-load gating, storage-queue rebalance triggers, and physical-shard relocation decisions. This header itself provides no unit tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DDShardTracker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DDSharedContext.h -->
## sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DDSharedContext.h

Purpose: declares the shared context object passed among DD components. It centralizes the distributor identity, interface, lock, configuration, enable state, tracker cancellation flag, shard-failure index, tracker, DD queue, and primary/remote team collections.

Important APIs and types: `DDSharedContext` owns `DDEnabledState`, `DataDistributorInterface`, `UID ddId`, `MoveKeysLock`, `DatabaseConfiguration`, `Reference<ShardsAffectedByTeamFailure>`, `Reference<DataDistributionTracker>`, `Reference<DDQueue>`, and `Reference<DDTeamCollection>` for primary and remote. It exposes constructors, `id()`, `markTrackerCancelled()`, `isTrackerCancelled()`, `usableRegions()`, and `isDDEnabled()`.

Control flow: this header only declares lifecycle. Components share a reference to the same context; cancellation is signaled by flipping `trackerCancelled`, and DD enablement delegates to the shared `DDEnabledState`.

State and persistence: the context is in-memory orchestration state. The underlying `DDEnabledState` is intentionally a non-resettable unique pointer because it is shared with the snapshot server. Durable state remains in system keys and data-movement metadata handled elsewhere.

Dependencies and integration: includes `DataDistributorInterface`, `MoveKeys`, `DDShardTracker`, `ShardsAffectedByTeamFailure`, and `DDTeamCollection`. It is the glue object used by real and mock data distributor startup paths.

Risks: because the class is intentionally small but shared broadly, adding members can create hidden coupling. Raw cancellation state must outlive actors that read it through `DataDistributionTracker::SafeAccessor`. Ordering between context destruction and component actors is important.

Test signals: tests should ensure constructors initialize shared state consistently, tracker cancellation is visible to actors, and mock/real DD paths share the same context contracts.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DDSharedContext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DDTeamCollection.h -->
## sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DDTeamCollection.h

Purpose: declares the main team-collection control plane for DD. It tracks storage servers, TSS pairs, server teams, machine teams, locality validity, failures, exclusions, recruitment, wiggle, under-replication, and team selection requests.

Important APIs and types: `TSSPairState` coordinates paired SS/TSS recruitment. `ServerStatus` and `ServerStatusMap` track failed, undesired, wiggling, wrong-configuration, and locality state. `IDDTeamCollection` exposes `getTeam`. `DDTeamCollectionInitParams` packages transaction processor, lock, relocation output, shard mapping, configuration, DC filters, readiness, health flags, request streams, failed-server removal promises, average-shard requests, storage-queue rebalance streams, and bulk-load collection. `DDTeamCollection` declares methods for building teams, adding/removing servers, tracking teams and servers, recruitment, wiggle, health waits, exclusion safety, under-replication repair, machine-team management, and public `run()`.

Control flow: implementation is elsewhere, but declared flow is clear: initialize from `InitialDataDistribution`, build machine teams and server teams that satisfy replication policy, track server list and excluded-server changes, recruit new storage/TSS when needed, mark bad teams, emit `RelocateShard` work, wait for data removal before final server removal, and maintain wiggle progress through system-key metadata. Template `addTeam()` converts UID ranges to server refs before adding concrete teams.

State and persistence: in-memory maps/vectors hold server info, machine info, teams, machine teams, lagging zones, recruiting IDs, invalid localities, team pivots, under-replication, and status maps. Persistent interactions are declared through transaction processor/database context and wiggle metadata key-backed maps; this header itself does not write.

Dependencies and integration: it depends on FDB options/types, storage interfaces, management APIs, replication policy, `MoveKeys`, `TCInfo`, `DataDistribution`, quiet database, server DB info, Flow actors, and bulk-load/task streams. It supplies teams to DD queue and reacts to tracker output, server list updates, exclusions, and wiggle configuration.

Risks: this is a high-coupling class with many invariants: `teams` and `teamsByServerIDs` must stay synchronized; machine-team and server-team counts must match policy; actors may reference raw `this` and rely on `shutdown`; removal paths must wait for data to leave; wiggle and exclusion states overlap. The protected surface is large, so regression tests should exercise lifecycle, not just individual helpers.

Test signals: the friend `DDTeamCollectionUnitTest` indicates direct unit-test access. Critical signals include team building under locality policy, server removal and data-drain, TSS pair success/failure, exclusion safety, perpetual wiggle pause/resume, under-replication fixes, and `getTeam` scoring under disk/read/storage-queue preferences.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DDTeamCollection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DDTxnProcessor.h -->
## sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DDTxnProcessor.h

Purpose: defines the transaction/data-plane abstraction used by DD, plus real and mock implementations. It isolates DD control logic from direct `Database`/NativeAPI calls and makes mock testing possible.

Important APIs and types: `IDDTxnProcessor` declares `context()`, `isMocked()`, source-server lookup, source interface lookup, `waitForAllDataRemoved()`, server-list reads, initial DD load, move-keys lock management, configuration reads, replica-key updates, DD enabled checks, lock polling, failed-server key removal, storage-server removal, `moveKeys()`, storage metric wait/split, read-hot ranges, health metrics, ignore-key reads, team-info print signal, worker listing, and storage stats. `DDTxnProcessor` implements the real database path. `DDMockTxnProcessor` implements mock state backed by `MockGlobalState`.

Control flow: real implementation delegates to NativeAPI and system-key operations, including move-key start/finish helpers. Mock implementation returns immediately where transaction atomicity is assumed, uses in-memory shard/server state, and exposes `setupMockGlobalState()` for tests. The interface lets DD components request behavior without knowing whether they run against a cluster or mock.

State and persistence: `DDTxnProcessor` stores a `Database cx` and performs durable reads/writes externally. `DDMockTxnProcessor` stores a shared `MockGlobalState` and mutates transient in-memory maps/server state. The interface makes persistence semantics explicit by forcing all database-affecting operations through this layer.

Dependencies and integration: includes knobs, move keys, `MockGlobalState`, `InitialDataDistribution`, `DDShardInfo`, storage metrics, health metrics, and data movement structures. It is referenced by shard tracker, team collection, TC metrics polling, physical shard collection, and mock DD.

Risks: default interface methods returning `Void`, `Never`, or empty vectors must be overridden where production behavior is required. Mock `context()` is unreachable, so code paths that leak direct database access break testability. Real and mock move semantics must stay aligned or mock DD tests can pass while production behavior differs.

Test signals: tests should assert DD components use this abstraction instead of direct `Database` calls, compare real/mock source-server semantics, cover failed-server removal, initial-data reconstruction, storage metrics split/wait behavior, and DD-enabled lock polling.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DDTxnProcessor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DataDistribution.h -->
## sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DataDistribution.h

Purpose: central declarations for DD relocation, shard metrics requests, physical shards, initial data distribution, bulk-load coordination, and perpetual storage wiggle. It is the shared type layer used by tracker, team collection, queue, transaction processor, and tests.

Important APIs and types: relocation types include `RelocateReason`, `DataMove`, and `RelocateShard`. Metric request types include `GetMetricsRequest`, `GetTopKMetricsRequest/Reply`, and `GetMetricsListRequest`. Physical-shard support is in `PhysicalShardCollection` and nested `PhysicalShard`. Bulk-load support includes `BulkLoadShardRequest`, `DDBulkLoadTaskBusyMap`, `BulkLoadAck`, `DDBulkLoadEngineTask`, and `BulkLoadTaskCollection`. Startup and team plumbing include `DDShardInfo`, `InitialDataDistribution`, and `TeamCollectionInterface`. Wiggle support is declared by `StorageWiggler`.

Control flow: `RelocateShard` captures requested movement, priority, reason, move reason, parent range, restore/cancel state, and data-move ID. `PhysicalShardCollection` maps key ranges to physical shard IDs, maps teams to physical shard IDs, chooses available physical shards for primary/remote team selection, tracks metrics changes, moves key ranges out of anonymous or oversized physical shards, and cleans/logs collection state. `BulkLoadTaskCollection` gates shard work while jobs/tasks are active, publishes newer tasks while invalidating overlapping old tasks, starts/terminates/erases task metadata, and lets DD attach tasks to data moves. `StorageWiggler` maintains a priority queue of servers and round metrics for perpetual wiggle.

State and persistence: declarations hold mostly in-memory DD state. Persistent inputs/outputs include data-move metadata, bulk-load task states, storage wiggle data/metrics, database configuration snapshots, audit states, and system-key-backed wiggle maps handled by implementations. `InitialDataDistribution` is a reconstructed snapshot at DD startup.

Dependencies and integration: this file includes NativeAPI, data distributor interfaces, move keys, data movement, shard metrics/sizing, DD transaction processor, shard-failure mapping, TC info, storage wiggle metrics, DD config, and Boost heap. It is included by most files in this group and forms a dependency hub.

Risks: because this header is central, changes have broad compile and behavior blast radius. Physical-shard state has multiple maps that must stay consistent. Bulk-load range maps intentionally treat uninitialized state as blocking, which is safe but can stall moves if initialization is missed. `GetTopKMetricsRequest` scores read density by bytes with a minimum denominator of 1, so tiny shards can dominate. Circular include pressure is visible because `DataDistribution.h` includes `DDTxnProcessor.h`, which also references data-distribution structs.

Test signals: important tests include relocation validation, parent range preservation, top-K read-density ordering, physical-shard selection and transition out of anonymous shards, bulk-load task overwrite/outdated behavior, and storage wiggle priority/round transitions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DataDistribution.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DataDistributionTeam.h -->
## sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DataDistributionTeam.h

Purpose: defines the abstract team interface and team-selection request object used by DD to choose source/destination teams for relocation, read balancing, storage-queue balancing, and bulk load.

Important APIs and types: `data_distribution::EligibilityCounter` tracks counts for `LOW_CPU` and `LOW_DISK_UTIL` eligibility bits. `IDataDistributionTeam` declares metrics, membership, health, priority, in-flight, space, read-load, CPU, store-configuration, and identity methods. Boolean params describe team-selection preferences. `TeamSelect` distinguishes normal selection, complete-source preference, and true-best selection. `GetTeamRequest` packages selection flags, source sets, optional key range, penalty, and reply promise.

Control flow: callers fill `GetTeamRequest`, send it to a team collection, and receive an optional team plus a boolean status. `lessCompare()` ranks candidate teams using read-load comparison when read balancing is requested, otherwise disk-load comparison; load direction flips when lower utilization is preferred. `fromGetTeamRequest()` lets eligibility counters derive combined conditions.

State and persistence: no persistence. `GetTeamRequest` is transient actor-message state. Team implementations such as `TCTeamInfo` provide the backing state and reference counting.

Dependencies and integration: depends on `StorageServerInterface`, `UID`, Flow promises, and `GetTeamRequest` consumers in `DDTeamCollection`. `TCTeamInfo` implements `IDataDistributionTeam`.

Risks: `TeamSelect::operator==` is non-const, which can be inconvenient in const contexts. Comparator behavior mixes read and disk signals; incorrect preference flags can select the opposite end of utilization. `GetTeamRequest` has many booleans, so constructor defaults and call-site readability are important.

Test signals: tests should cover comparator direction for disk/read balancing, `findTeamByServers`, complete-source selection, bulk-load selection, storage-queue awareness, eligibility counts, and `getDesc()` diagnostics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DataDistributionTeam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DataDistributor.h -->
## sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DataDistributor.h

Purpose: declares the real data distributor actor entry point.

Important APIs and functions: `Future<Void> dataDistributor(DataDistributorInterface ddi, Reference<AsyncVar<ServerDBInfo> const> db, std::string folder)` starts the DD role using its RPC interface, live server DB info, and data folder.

Control flow: implementation is not in this header. Callers hand the actor a `DataDistributorInterface`; the actor is expected to initialize DD state, participate in leader/role lifecycle, and run until cancellation or error.

State and persistence: no local state. The actor implementation will use `ServerDBInfo`, system keys, move-key locks, and DD components declared elsewhere.

Dependencies and integration: includes `DataDistributorInterface` and Flow. Forward-declares `ServerDBInfo`. This is the public include for fdbserver role startup.

Risks: minimal header risk, but signature changes would affect role startup call sites. The `folder` parameter couples actor startup to local process storage/log paths.

Test signals: compile/link coverage and role startup simulation tests should ensure the actor can be constructed with the current interface.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DataDistributor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/MockDataDistributor.h -->
## sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/MockDataDistributor.h

Purpose: declares the mock data distributor entry point used by DD tests.

Important APIs and functions: `class MockDataDistributor` exposes `Future<Void> run(Reference<DDSharedContext> context, Reference<DDMockTxnProcessor> txnProcessor)`.

Control flow: implementation is elsewhere. The mock runner takes the same shared context shape as the real DD but uses `DDMockTxnProcessor`, allowing DD control-plane actors to operate against `MockGlobalState`.

State and persistence: no state in the header. Runtime state lives in `DDSharedContext` and the mock transaction processor's `MockGlobalState`; all persistence is in-memory.

Dependencies and integration: includes `DataDistribution.h`, `DDSharedContext.h`, and `MockGlobalState.h`. It bridges mock tests into the same component graph as production DD.

Risks: if DD code bypasses `IDDTxnProcessor` and uses real `Database` APIs, this mock entry point will fail or miss coverage. Header coupling to `DataDistribution.h` can increase rebuild cost.

Test signals: mock DD tests should verify `run()` can initialize team collection, tracker, queue, and move flows using `DDMockTxnProcessor`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/MockDataDistributor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/MockGlobalState.h -->
## sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/MockGlobalState.h

Purpose: declares the in-memory mock storage cluster used by DD tests. It models shard status, server-key state, key-location service behavior, topology, process locality, storage metrics service endpoints, and simple read/write/clear operations.

Important APIs and types: `MockShardStatus` and `isStatusTransitionValid()` define shard lifecycle. `MockStorageServer` implements `IStorageMetricsService` with `ShardInfo`, `FetchKeysParams`, disk/cpu constants, server key map, byte samples, storage interface, data operations, metrics RPC handlers, fetch signaling, and protected split/sample helpers. Mock topology is represented by `mock::TopologyObject` and `mock::Process`. `MockGlobalState` implements `IKeyLocationService`, owns `shardMapping`, `allServers`, configuration, topology, workload knobs, cluster initialization, server addition, source/destination checks, metric wait/split, key-location lookup, data ops, and server-running helpers.

Control flow: callers build topology with `initializeClusterLayout()`, initialize seed storage with `initializeAsEmptyDatabaseMGS()`, optionally add storage per process, then run mock servers. DD mock transaction code uses `shardMapping` and `allServers` to answer source-server queries and drive moves. `MockStorageServer` methods mutate `serverKeys`, samples, counters, and disk usage in response to simulated operations and fetch completion.

State and persistence: all state is transient. `MockGlobalState::g_mockState()` offers a process-global shared pointer. The mock deliberately mirrors production system key concepts in memory: `keyServers` as `shardMapping`, `serverListKeys` as `allServers`, and `serverKeys` per mock storage server.

Dependencies and integration: depends on storage metrics, key range maps, storage server interfaces, database configuration, key-location service, shard/team failure mapping, and simulated-cluster config. It is the backing state for `DDMockTxnProcessor` and `MockDataDistributor`.

Risks: default public workload fields such as `emptyProb`, `minByteSize`, and `maxByteSize` are not initialized in the constructor and must be set before use in workloads that depend on them. Mock behavior is intentionally approximate: simplified locality, simplified disk/CPU model, and mostly single-region assumptions. Status and server-removal contracts are documented but enforced by assertions rather than durable invariants.

Test signals: the implementation file contains tests for initialization, shard splitting, status transitions, locations, metrics, and data operations. Additional tests should cover uninitialized workload knobs, failed-server contracts, mock server removal, and source/destination checks during in-flight moves.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/MockGlobalState.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/ShardsAffectedByTeamFailure.h -->
## sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/ShardsAffectedByTeamFailure.h

Purpose: declares the shard/team failure index used by DD to know which shards are affected by a failed or degraded team. It also serves as the mock key-server mapping.

Important APIs and types: `ShardsAffectedByTeamFailure::Team` is a sorted vector of server UIDs plus a primary flag, with comparison, equality, membership, removal, and stringification. Public methods expose shard counts, shards for a team, teams for a key/range, source-server extraction, shard definition, movement, raw movement, move finish, assignment, consistency checking, failed-server removal, range iteration, and `restartShardTracker` signaling.

Control flow: the intended mutation pipeline is `defineShard()` to adjust boundaries, `moveShard()` to set destination teams while preserving previous sources, and `finishMove()` to clear previous sources after completion. `assignRangeToTeams()` wraps that full pipeline for direct assignment.

State and persistence: private state consists of a `KeyRangeMap` from shard ranges to current/previous teams, a secondary set from team to ranges, and per-server shard counts. It is in-memory only and must be rebuilt or updated by DD logic.

Dependencies and integration: depends on Flow refs/random, FDB key/range types, and `KeyRangeMap`. It is used by team collection, tracker, transaction processor, data distribution startup, and mock global state.

Risks: `Team` requires sorted server vectors; unsorted input breaks map ordering and equality expectations. The secondary indexes are manually maintained. `CheckMode::ForceNoCheck` can hide corruption, while `ForceCheck` can be expensive.

Test signals: test coverage should target overlapping move semantics, previous-source retention, server count changes, failed-server removal, team ordering with `primary`, and consistency-check behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/ShardsAffectedByTeamFailure.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/SimulatedCluster.h -->
## sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/SimulatedCluster.h

Purpose: declares a compact simulation configuration interface used by DD tests and mock global-state setup.

Important APIs and types: `simulationSetupAndRun()` is the fdbserver simulation entry point declared here. `SimulationStorageEngine` enumerates storage backends. `BasicTestConfig` contains replication, anti-quorum, simplification, region, role-count, machine-count, coordinator, storage-engine, and ASAN machine-count options. `BasicSimulationConfig` contains datacenter count, replication type, machine count, processes per machine, and `DatabaseConfiguration`. `generateBasicSimulationConfig()` converts test config to simulation config.

Control flow: callers fill `BasicTestConfig`, call `generateBasicSimulationConfig()`, and feed the result to mock or simulation setup. `simulationSetupAndRun()` is declared for `fdbserver -r simulation` usage.

State and persistence: the structs are value-only configuration state. There is no persistence.

Dependencies and integration: includes `DatabaseConfiguration` and Flow `Optional`. `MockGlobalState` consumes `BasicSimulationConfig` to create topology and initial servers.

Risks: this header does not enforce consistency beyond types; validation occurs in the implementation and downstream assertions. Some fields, such as `asanMachineCount`, are declared but not consumed by the current `generateBasicSimulationConfig()` implementation in this subset.

Test signals: compile coverage plus config-generation tests for replication modes, simple configs, single-region behavior, and optional override fields.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/SimulatedCluster.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/TCInfo.h -->
## sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/TCInfo.h

Purpose: declares the in-memory metadata objects used by `DDTeamCollection` to represent storage servers, machines, machine teams, and server teams.

Important APIs and types: `TCServerInfo` stores server identity, desired-DC flag, collection pointer, tracker, added version, last known interface/class, store type, in-flight counters, team membership, metrics, health stats, queue timing, locality entry, promises, and AsyncVars. It exposes metric refresh, store-type refresh, desired-DC updates, team membership mutation, queue detection, space/load helpers, and cancellation. `TCMachineInfo` groups servers by machine locality. `TCMachineTeamInfo` groups machines and server teams. `TCTeamInfo` implements `IDataDistributionTeam`, exposing server interfaces/IDs, health/priority/config flags, metrics aggregation, in-flight accounting, eligibility counters, optimality, and space/load/read/CPU methods.

Control flow: team collection creates `TCServerInfo` for storage servers, groups them into machines and machine teams, builds `TCTeamInfo` server teams, then uses these objects to score candidate teams and react to health changes. Metric polling and storage stats populate server fields; team methods aggregate those values for placement decisions.

State and persistence: all fields are in-memory control-plane state. Persistent server lists, storage metadata, exclusions, and wiggle metadata are read or written by team collection/transaction code, not by these declarations.

Dependencies and integration: depends on system data, replication types, `DDTxnProcessor`, `DataDistributionTeam`, Flow refs, and arenas. `TCInfo.cpp` implements the declared behavior, and `DDTeamCollection.h` owns collections of these objects.

Risks: `TCServerInfo` exposes many mutable promises and AsyncVars, so actor lifecycle ordering matters. Methods such as `getMetrics()` assume metrics are present. `TCTeamInfo::size()` asserts server refs and IDs remain synchronized; adding servers by UID without refs is a special case that needs care.

Test signals: tests should cover server metric availability, in-flight counter updates, machine/team membership removal, team load/space/read/CPU aggregation, eligibility counters, wrong-store-type handling, and destructor cleanup of lagging zones.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/TCInfo.h -->
