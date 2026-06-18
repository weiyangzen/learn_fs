# Research: subset-b-008480

This grouped report covers the FoundationDB network test harness plus the ratekeeper, resolver, sequencer, and selected storage-server support files assigned to `subset-b-008480`. Each section preserves the exact source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/networktest.cpp -->
# sources/storage-engines/foundationdb/fdbserver/networktest.cpp

Purpose: implements Flow/FDB network benchmark and diagnostic tests. It provides RPC-style ping/reply tests, streaming reply tests, a nanosleep latency probe, and peer-to-peer socket throughput/session tests exposed as unit-test style commands.

Important APIs and functions: `NetworkTestInterface` binds a well-known endpoint token. `NetworkTestServer` and `NetworkTestStreamingServer` serve request/reply and reply-stream traffic. `networkTestClient`, `testClient`, `testClientStream`, and `logger` drive concurrent clients and latency statistics. `RandomIntRange` parses fixed or min:max command parameters. `P2PNetworkTest` owns listeners, remote addresses, session counters, message framing, `readMsg`, `writeMsg`, `doSession`, `incoming`, `outgoing`, and `run`/`run_oneshot`. Test cases are `:/network/p2ptest` and `:/network/p2poneshottest`.

Control flow, state, and persistence: all state is process-local counters, latency accumulators, sockets, and actor collections. No durable state is written. P2P sessions use an int length header followed by payload bytes, explicitly run Flow handshakes, and update byte/session/error counters before periodic status logging.

Dependencies and integration: depends on Flow networking (`IConnection`, `INetworkConnections`, endpoints, actors), `NetworkTest.h` request types, `FLOW_KNOBS`, and unit-test registration. It integrates with external `fdbserver` network-test invocations rather than production transaction paths.

Risks and test signals: risks are measurement skew from shared non-atomic counters, unbounded loops in nanosleep and server modes, malformed length headers, and random remote selection with empty remote lists. Test signals are successful P2P handshakes, expected streaming indexes ending with `end_of_stream`, stable throughput output, and TraceEvents for connect, accept, or session errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/networktest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/ratekeeper/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbserver/ratekeeper/CMakeLists.txt

Purpose: defines the `fdbserver_ratekeeper` static library target and its build/test integration.

Important APIs and functions: `fdb_find_sources(FDBSERVER_RATEKEEPER_SRCS)` gathers local sources. `add_flow_target(STATIC_LIBRARY NAME fdbserver_ratekeeper ...)` builds the library. `add_fdbserver_link_test` and `add_fdbserver_unit_test` wire link and unit-test validation against `fdbserver_core`. `configure_fdbserver_common_includes`, `target_include_directories`, and `target_link_libraries` publish the `include` tree and add private local includes.

Control flow, state, and persistence: this is declarative CMake with no runtime state. Its main effect is target graph construction, include visibility, and test target registration.

Dependencies and integration: integrates ratekeeper code with the larger fdbserver build. Public headers under `ratekeeper/include` become visible to consumers, while implementation headers in the directory stay private.

Risks and test signals: risks are missing new sources if the source discovery macro changes, missing public include paths, and link-test gaps after dependencies are added. Build signals are successful `fdbserver_ratekeeper`, `fdbserver_ratekeeperlinktest`, and `fdbserver_ratekeeper_test` targets.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/ratekeeper/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/ratekeeper/Ratekeeper.cpp -->
# sources/storage-engines/foundationdb/fdbserver/ratekeeper/Ratekeeper.cpp

Purpose: implements the ratekeeper role that computes transaction-per-second limits for default and batch priorities from storage-server queues, tlog queues, disk space, version lag, durability lag, recovery state, and tag throttling.

Important APIs and functions: `Ratekeeper::run` composes actors for configuration, storage/tlog metric tracking, tag throttle monitoring, hot-shard throttling, commit-cost collection, DBInfo changes, and rate updates. `handleGetRateInfoReqs` returns per-proxy TPS leases and pushed tag throttle maps. `updateRate` is the core limiter algorithm. `StorageQueueInfo::update`, `refreshCommitCost`, and `TLogQueueInfo::update` maintain smoothed metrics. `getSSVersionLag` separates primary and remote DC versions. The free `ratekeeper` actor starts the role.

Control flow, state, and persistence: state is in-memory maps keyed by server UID, `Smoother` counters, proxy leases, health metrics, and recovery windows. Persistent reads/watches use system keys for configuration and tag throttles through `Database`; no local files are written. The role periodically polls metric endpoints and recomputes limits every metric interval.

Dependencies and integration: consumes `ServerDBInfo`, `StorageServerInterface`, `TLogInterface`, `RatekeeperInterface`, failure monitoring, system configuration keys, `TagThrottler`, and health metrics sent to proxies. It also talks to commit proxies for hot-shard throttling.

Risks and test signals: risks include over-throttling when server-list fetches stall, smoothing reset on instance changes, division by small input rates, remote-DC filtering mistakes, and incorrect ignored-zone logic. Signals are `RkUpdate*` traces, health metrics, tag throttle counts, storage/tlog queue limits, and tests or simulation assertions around server-list consistency and recovery transitions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/ratekeeper/Ratekeeper.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/ratekeeper/Ratekeeper.h -->
# sources/storage-engines/foundationdb/fdbserver/ratekeeper/Ratekeeper.h

Purpose: declares internal ratekeeper data structures and the `Ratekeeper` class used by the implementation target.

Important APIs and types: `StorageQueueInfo` stores smoothed durable bytes, input bytes, versions, disk space, locality, accepting state, busiest read/write tags, and commit-cost estimations. `TLogQueueInfo` tracks smoothed tlog durability, input, and disk metrics. `RatekeeperLimits` holds per-priority target/spring bytes, max version difference, durability lag controls, TPS metric handles, priority, and TraceEvent cache. `Ratekeeper` owns the database, server/tlog maps, smoothing history, proxy info, health metrics, and a polymorphic `ITagThrottler`.

Control flow, state, and persistence: this header defines in-memory state only. Persistence and watches are handled in `Ratekeeper.cpp` through FDB transactions and tag throttle APIs.

Dependencies and integration: includes database context, storage-server and tlog interfaces, tag throttling, `Smoother`, ratekeeper interface, and limit reason enums. It is private to the ratekeeper library except for local implementation consumers.

Risks and test signals: risks are stale values in `lastReply`, smoothing semantics when server instances restart, integer/double conversion in queue and durability calculations, and constructor knob drift. Tests should exercise `StorageQueueInfo` update/reset behavior, `getTagThrottlingRatio`, limit metric initialization, and tlog/storage queue accessors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/ratekeeper/Ratekeeper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/ratekeeper/RatekeeperLimits.cpp -->
# sources/storage-engines/foundationdb/fdbserver/ratekeeper/RatekeeperLimits.cpp

Purpose: implements the `RatekeeperLimits` constructor and binds per-priority ratekeeper limit state to metric names and TraceEvent cache keys.

Important APIs and functions: `RatekeeperLimits::RatekeeperLimits` initializes `tpsLimit`, metric handles for TPS and limit reason, storage and log target/spring bytes, max version difference, durability lag target/state, priority, context string, and `EventCacheHolder` for update traces. Context differentiates default and batch limit metric names.

Control flow, state, and persistence: no runtime loop or persistent state exists in this file. It only initializes an in-memory configuration object from constructor arguments and global metric registration.

Dependencies and integration: depends on `Ratekeeper.h`, metric handles, transaction priority naming, and ratekeeper update logging in `Ratekeeper::updateRate`. `Ratekeeper.cpp` creates default and batch instances with different knobs.

Risks and test signals: risks are mismatched metric names, wrong default `durabilityLagLimit` initialization, or swapped default/batch knob values. Test signals are metrics appearing under expected names and correct limit/reason updates in ratekeeper traces.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/ratekeeper/RatekeeperLimits.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/ratekeeper/RkTagThrottleCollection.cpp -->
# sources/storage-engines/foundationdb/fdbserver/ratekeeper/RkTagThrottleCollection.cpp

Purpose: implements the in-memory collection that merges manual and automatic transaction tag throttles and computes smoothed client-facing tag rates.

Important APIs and functions: `RkTagThrottleData::getTargetRate` and `updateAndGetClientRate` translate limits plus observed request rate into smoothed client rates. `computeTargetTpsRate` calculates target TPS from current and desired tag busyness. `autoThrottleTag` creates or updates automatic throttles with aggregation/update windows. `manualThrottleTag` installs priority-specific manual throttles. `getClientRates` expires old entries, merges manual and auto throttles per priority, applies auto ramp-up, and returns `PrioritizedTransactionTagMap`. `addRequests` feeds request-rate smoothing.

Control flow, state, and persistence: state is process-local maps of auto throttles, manual priority maps, request-rate smoothers, and busy-read/write counters. Persistence is external: `TagThrottler` reads/writes system tag throttle keys and rebuilds this collection.

Dependencies and integration: depends on tag throttle client types, `CLIENT_KNOBS`, `SERVER_KNOBS`, transaction priorities, and TraceEvent/CODE_PROBE. Used only behind `TagThrottler`.

Risks and test signals: risks include erasing while iterating manual throttle maps, infinite-rate sentinel handling, divide-by-zero if busyness/request-rate invariants are violated, and priority override mistakes. Tests should cover expiration, ramp-up, manual-vs-auto precedence, max auto throttle count, and request-rate smoothing.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/ratekeeper/RkTagThrottleCollection.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/ratekeeper/RkTagThrottleCollection.h -->
# sources/storage-engines/foundationdb/fdbserver/ratekeeper/RkTagThrottleCollection.h

Purpose: declares the non-copyable ratekeeper tag throttle collection and its private data records.

Important APIs and types: `RkTagData` stores per-tag request-rate smoothing. `RkTagThrottleData` stores a `ClientTagThrottleLimits`, smoothed client rate, creation/update/reduction timestamps, and rate initialization state. Public methods are `autoThrottleTag`, `manualThrottleTag`, `getManualTagThrottleLimits`, `getClientRates`, `addRequests`, throttle counters, and `incrementBusyTagCount`.

Control flow, state, and persistence: this header defines in-memory throttle state only. Move construction/assignment transfers all maps. It has no durable ownership and no direct transaction API.

Dependencies and integration: uses `TransactionTagMap`, prioritized throttle maps, `Smoother`, transaction priorities, and `TagThrottledReason`. `TagThrottler` is the only production wrapper that connects it to database watches and throttle API calls.

Risks and test signals: risks are hidden invariants around positive busyness, valid future expirations, and smoothing windows from client knobs. Tests should validate move semantics, count methods, manual limit lookup, and behavior when `autoThrottlingEnabled` is false.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/ratekeeper/RkTagThrottleCollection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/ratekeeper/TagThrottler.cpp -->
# sources/storage-engines/foundationdb/fdbserver/ratekeeper/TagThrottler.cpp

Purpose: bridges durable tag throttle system keys, automatic throttle creation, expired throttle cleanup, and the in-memory `RkTagThrottleCollection` consumed by ratekeeper.

Important APIs and functions: `TagThrottlerImpl::monitorThrottlingChanges` reads `tagThrottleKeys`, `tagThrottleAutoEnabledKey`, writes the manual-throttle limit key on first successful pass, converts duration-style expirations to absolute timestamps, rebuilds throttle collection state, watches `tagThrottleSignalKey`, and bumps a change id. `tryUpdateAutoThrottling` creates automatic throttles through `ThrottleApi::throttleTags`. `cleanupExpiredTagThrottles` runs periodically through `recurring`. The public `TagThrottler` forwards `addRequests`, `getClientRates`, counters, and `tryUpdateAutoThrottling(StorageQueueInfo)`.

Control flow, state, and persistence: local state is `RkTagThrottleCollection`, change id, auto-enabled flag, and cleanup future. Durable state lives in FDB system keys managed with lock-aware, system-immediate transactions and `ThrottleApi`.

Dependencies and integration: depends on `Database`, tag throttle key codecs, `StorageQueueInfo` busiest tags, ratekeeper knobs, and the ratekeeper proxy reply path. It also uses storage queue/durability lag thresholds to decide when read/write busy tags deserve auto-throttle attempts.

Risks and test signals: risks include stale throttle state between watch signals, invalid auto-enabled values, too many system keys for `TOO_MANY`, and racey duration-to-expiration conversion. Signals are `RatekeeperReadThrottledTags`, `RatekeeperThrottleSignaled`, auto/manual throttle traces, and client proxies receiving updated tag maps when change id advances.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/ratekeeper/TagThrottler.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/ratekeeper/TagThrottler.h -->
# sources/storage-engines/foundationdb/fdbserver/ratekeeper/TagThrottler.h

Purpose: declares the tag throttling abstraction used by `Ratekeeper`, allowing implementation hiding through `PImpl` and test substitution through `ITagThrottler`.

Important APIs and types: `ITagThrottler` exposes monitoring, request accounting, change id, client rate export, auto/manual/busy counters, auto-throttling enabled state, storage-server auto-throttle updates, and `updateThrottling`. `TagThrottler` implements the interface via `PImpl<TagThrottlerImpl>`.

Control flow, state, and persistence: no direct state is visible except the opaque implementation pointer. Persistence is implementation-defined in `TagThrottler.cpp`, where FDB system keys are watched and updated.

Dependencies and integration: includes `Ratekeeper.h` for `StorageQueueInfo`, tag throttle maps, and Flow futures. Ratekeeper holds `std::unique_ptr<ITagThrottler>` so algorithm code can call the abstraction.

Risks and test signals: risks are interface drift between ratekeeper and implementation, the no-op default `updateThrottling`, and lifetime errors through the PImpl. Tests can substitute `ITagThrottler` to verify ratekeeper behavior without database watches and should assert forwarding of counters and client rates.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/ratekeeper/TagThrottler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/ratekeeper/include/fdbserver/ratekeeper/Ratekeeper.h -->
# sources/storage-engines/foundationdb/fdbserver/ratekeeper/include/fdbserver/ratekeeper/Ratekeeper.h

Purpose: exposes the public entry point for starting a ratekeeper actor from other fdbserver modules.

Important APIs and functions: declares `Future<Void> ratekeeper(RatekeeperInterface rkInterf, Reference<AsyncVar<ServerDBInfo> const> dbInfo)`. It forward-declares `ServerDBInfo` and includes `RatekeeperInterface` plus Flow primitives.

Control flow, state, and persistence: none in the header. The returned actor is implemented by `Ratekeeper::run` and owns all runtime monitoring, system-key watches, and rate computation.

Dependencies and integration: this is the public include path exported by the ratekeeper CMake target. Recruitment or role-startup code can include it without depending on internal `Ratekeeper.h` implementation details.

Risks and test signals: risks are ABI/API mismatch if the internal signature changes without this wrapper. Build/link tests should ensure consumers can include this header and link against `fdbserver_ratekeeper`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/ratekeeper/include/fdbserver/ratekeeper/Ratekeeper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/resolver/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbserver/resolver/CMakeLists.txt

Purpose: declares the `fdbserver_resolver` static library and its validation targets.

Important APIs and functions: `fdb_find_sources(FDBSERVER_RESOLVER_SRCS)` collects sources, `add_flow_target` builds the library, link and unit tests include `fdbserver_logsystem` and `fdbserver_core`, common includes are configured, the public `include` directory is exported, and local source directory is private.

Control flow, state, and persistence: declarative build metadata only. It defines no runtime behavior or persistent state.

Dependencies and integration: resolver depends on core server interfaces and the logsystem because resolver private mutations can use a log-system-backed key-value store. This target is consumed by fdbserver role recruitment and tests.

Risks and test signals: risks are missing logsystem linkage, hidden include path mistakes, and source discovery omissions. Build signals are successful resolver library, link test, and resolver unit-test target.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/resolver/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/resolver/ConflictSet.cpp -->
# sources/storage-engines/foundationdb/fdbserver/resolver/ConflictSet.cpp

Purpose: implements the resolver conflict detection engine used to decide which transactions in a commit batch can commit. It records write conflict history by key range/version and checks incoming read ranges against that history plus intra-batch writes.

Important APIs and functions: `newConflictSet`, `clearConflictSet`, and `destroyConflictSet` manage opaque state. `ConflictBatch::addTransaction` converts commit transactions into sorted read/write boundary points and read conflict descriptors. `detectConflicts` sorts points, checks historical read conflicts, checks intra-batch conflicts with `MiniConflictSet`, combines non-conflicting write ranges, merges them into the skip list, and removes old history. The internal `SkipList` stores boundary keys with max versions per level; `ReadConflictRange`, `KeyInfo`, and `sortPoints` optimize batch processing.

Control flow, state, and persistence: state is in-memory `ConflictSet` with a version-history skip list, oldest version, and removal cursor key. No durable persistence exists; recovery rebuilds resolver state elsewhere. Bug injection can ignore too-old/read/write sets in simulation.

Dependencies and integration: consumes `CommitTransactionRef`, Flow arenas, `ConflictBatchStatus`, `ResolverBug`, key ranges, and unit-test macros. `Resolver.cpp` creates a `ConflictBatch` per resolve request.

Risks and test signals: risks are boundary ordering semantics, skip-list max-version maintenance, memory allocator correctness, conflicting-key reporting, and old-version pruning. Tests include `skipListTest` and `miniConflictSetCompatibility`; additional signals are accepted/conflicted/too-old resolver counters and deterministic simulation failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/resolver/ConflictSet.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/resolver/ConflictSet.h -->
# sources/storage-engines/foundationdb/fdbserver/resolver/ConflictSet.h

Purpose: declares the opaque conflict-set API and the `ConflictBatch` wrapper used by resolver code.

Important APIs and types: `ConflictSet` is forward-declared with creation, clear, and destroy functions. `ConflictBatch` extends `ConflictBatchStatus`, accepts transactions, detects conflicts for a commit version/new oldest version, and can return too-old transaction indexes. Private members store transaction info, boundary points, combined write/read ranges, conflict status array, optional conflicting-key range map, reply arena, and simulation bug injector.

Control flow, state, and persistence: the header exposes an in-memory batch lifecycle: build from transactions, detect, then discard. Persistent resolver state is not represented here.

Dependencies and integration: depends on commit transaction encoding, core conflict status values, Flow vectors/arenas, and `ResolverBug`. It is a private include for the resolver library.

Risks and test signals: risks are ownership/lifetime of `StringRef` and `VectorRef` data, optional conflicting-key map nullability, and ensuring `detectConflicts` is called once per populated batch. Tests should exercise too-old reporting, conflicting-key reporting, empty batches, and bug injection probabilities.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/resolver/ConflictSet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/resolver/Resolver.cpp -->
# sources/storage-engines/foundationdb/fdbserver/resolver/Resolver.cpp

Purpose: implements the resolver actor that serializes commit-batch conflict resolution, tracks recent metadata state transactions, serves resolution split/metric requests, and optionally applies resolver-private metadata mutations.

Important APIs and functions: `Resolver` owns conflict state, recent state transaction cache, proxy request history, sampling metrics, optional log-system-backed `txnStateStore`, key-server cache, and counters. `resolveBatch` enforces per-proxy ordering with `versionReady`, detects conflicts through `ConflictBatch`, records committed/too-old/conflicted statuses, stores state transactions, emits private mutations, updates TLog previous-commit-version maps, and responds idempotently to duplicate requests. `resolveMetricsRequests`, `resolveSplitRequests`, `pollMetrics`, and transaction-state request processing support resolution balancing and recovery. `resolverCore` initializes logsystem consumers and actor streams.

Control flow, state, and persistence: resolver state is mostly memory-resident. When private resolver mutations are enabled, a `LogSystemDiskQueueAdapter` and `IKeyValueStore` hold transaction-state metadata recovered from `TxnStateRequest` parts. Recent state transactions are retained until all commit proxies have advanced.

Dependencies and integration: integrates with commit proxies through `ResolverInterface`, master through initialization, logsystem, metadata mutation application, storage info caches, version-vector unicast, histograms, and failure monitoring.

Risks and test signals: risks include proxy ordering deadlocks under memory pressure, duplicate reply retention, state transaction cache growth, private mutation divergence from commit proxy logic, and recovery request sequencing. Signals are resolver counters/histograms, conflict outcomes, state byte limits, resolution metrics, and worker removal termination traces.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/resolver/Resolver.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/resolver/ResolverBug.cpp -->
# sources/storage-engines/foundationdb/fdbserver/resolver/ResolverBug.cpp

Purpose: registers the resolver simulation bug payload with the generic `SimBugInjector`.

Important APIs and functions: `ResolverBugID::create` returns `std::make_shared<ResolverBug>()`.

Control flow, state, and persistence: no runtime loop or persistence. It constructs fresh in-memory bug state when the simulation bug injector requests this identifier.

Dependencies and integration: depends on the public `ResolverBug.h` definition and Flow simulation bug injection. `ConflictBatch` fetches this bug object to probabilistically ignore too-old checks, read sets, or write sets.

Risks and test signals: risk is small but important: if the identifier creates the wrong derived type, conflict-set simulation tests lose intended fault injection. Simulation tests should verify the bug object is discoverable and that `bugs->hit()` paths are reachable when probabilities are nonzero.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/resolver/ResolverBug.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/resolver/include/fdbserver/resolver/Resolver.h -->
# sources/storage-engines/foundationdb/fdbserver/resolver/include/fdbserver/resolver/Resolver.h

Purpose: exposes the public resolver role entry point to the rest of fdbserver.

Important APIs and functions: declares `Future<Void> resolver(ResolverInterface resolver, InitializeResolverRequest initReq, Reference<AsyncVar<ServerDBInfo> const> db)`. It forward-declares initialization and DB info types and includes the resolver interface plus Flow primitives.

Control flow, state, and persistence: none in the header. Runtime behavior lives in `resolverCore` and the wrapper `resolver` in `Resolver.cpp`, including optional logsystem-backed state store setup.

Dependencies and integration: exported through the resolver library's public include directory. Role recruitment code can call this actor without seeing conflict-set internals.

Risks and test signals: risks are public signature drift and missing includes for consumers. Link tests and role startup tests should compile this header and instantiate the resolver actor through the built target.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/resolver/include/fdbserver/resolver/Resolver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/resolver/include/fdbserver/resolver/ResolverBug.h -->
# sources/storage-engines/foundationdb/fdbserver/resolver/include/fdbserver/resolver/ResolverBug.h

Purpose: defines simulation-only resolver bug state and its bug-injector identifier.

Important APIs and types: `ResolverBug` derives from `ISimBug` and stores probabilities for ignoring too-old checks, write sets, and read sets. It also carries `bugFound`, `currentPhase`, and `cycleState` fields for coordinating simulation clients. `ResolverBugID` derives from `IBugIdentifier` and overrides `create`.

Control flow, state, and persistence: state is in-memory per bug object. It is not serialized or used in production durability paths.

Dependencies and integration: included by `ConflictSet.h`; `ConflictBatch` retrieves `SimBugInjector().get<ResolverBug>(ResolverBugID())` and uses the probabilities in conflict logic.

Risks and test signals: risks are accidental production influence if probabilities are nonzero outside simulation, and stale coordination fields. Tests should assert default probabilities are zero and targeted simulation workloads can force conflict anomalies when configured.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/resolver/include/fdbserver/resolver/ResolverBug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/sequencer/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbserver/sequencer/CMakeLists.txt

Purpose: defines the `fdbserver_sequencer` static library and its build validation.

Important APIs and functions: source discovery uses `fdb_find_sources`. `add_flow_target` creates the library. Link and unit tests validate against `fdbserver_core`. Common include setup exports the `include` directory publicly and the local directory privately. `target_link_libraries` records the core dependency.

Control flow, state, and persistence: CMake metadata only; no runtime state.

Dependencies and integration: integrates sequencer/master code into the fdbserver build. The public include path exposes `MasterServer.h` while local files such as `MasterData.h` remain implementation details.

Risks and test signals: risks are missing new source files, absent core linkage, or public include path breakage. Build and unit-test target success are the primary signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/sequencer/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/sequencer/MasterData.h -->
# sources/storage-engines/foundationdb/fdbserver/sequencer/MasterData.h

Purpose: declares internal state for the master/sequencer actor that assigns commit versions and publishes live committed versions.

Important APIs and types: `CounterValue` wraps shared `Counter` ownership and exposes increment/add/clear. `MasterData` stores DB id, epoch/recovery versions, live committed version, lock/metadata state, min known committed version, coordinators, current assigned version, reference version, per-proxy duplicate-suppression maps, master interface, `ResolutionBalancer`, forced recovery flag, storage-server version vector, primary locality, counters, latency samples, actor stream, logger, and balancer actor.

Control flow, state, and persistence: all members are in-memory for a master lifetime. Durable epoch and recovery state are supplied through `UpdateRecoveryDataRequest` and `ServerDBInfo`; this struct does not write storage directly.

Dependencies and integration: depends on master, coordination, server DB info, version-vector, Trace/counter, and resolution balancing types. `masterserver.cpp` constructs and mutates it.

Risks and test signals: risks are lifetime-sensitive references, duplicate reply retention, invalid version initialization, and version-vector locality handling. Tests should cover constructor initialization, counters, forced recovery locality validation, and version vector sample creation when enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/sequencer/MasterData.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/sequencer/ResolutionBalancer.cpp -->
# sources/storage-engines/foundationdb/fdbserver/sequencer/ResolutionBalancer.cpp

Purpose: implements resolver key-range load balancing by sampling resolver metrics and sending move instructions to commit proxies through commit-version replies.

Important APIs and functions: `setResolvers` records resolver interfaces and triggers balancing when more than one resolver exists. `setChangesInReply` attaches pending `ResolverMoveRef` changes to the next reply for each commit proxy. `findRange` selects a source resolver range to move, preferring existing borders with the destination, then new borders, then any source range. `resolutionBalancing_impl` periodically gathers `ResolutionMetricsReply`, compares max/min load, asks the source resolver to split a range, updates the local `CoalescedKeyRangeMap`, and publishes changes for proxies.

Control flow, state, and persistence: state is in-memory resolver assignment, pending changes, target proxy set, and change version. There is no durable state; proxies learn moves via sequencer replies and future recovery can rebuild assignment.

Dependencies and integration: uses `ResolverInterface` metrics/split RPCs, `CommitProxyInterface`, `GetCommitVersionReply`, `KeyRangeMap`, `IndexedSet`, and sequencer version pointer from `MasterData`.

Risks and test signals: risks are moving already-pending ranges, bad split estimates, starvation while pending changes are not consumed, and assignment drift after resolver changes. Signals are `MovingResolutionRange` traces, `resolverChangesVersion`, balanced resolver metrics, and proxy receipt of resolver changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/sequencer/ResolutionBalancer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/sequencer/ResolutionBalancer.h -->
# sources/storage-engines/foundationdb/fdbserver/sequencer/ResolutionBalancer.h

Purpose: declares the sequencer-side helper that tracks resolver assignments and pending balancing changes.

Important APIs and types: `ResolutionBalancer` contains `resolverChanges`, `resolverChangesVersion`, `resolverNeedingChanges`, a pointer to `MasterData::version`, commit proxy and resolver interface vectors, and a trigger. Public methods are `resolutionBalancing`, static implementation entry, `setResolvers`, `setCommitProxies`, and `setChangesInReply`.

Control flow, state, and persistence: state is memory-only and scoped to the master actor. Pending resolver changes remain in an `AsyncVar` until every tracked commit proxy receives them.

Dependencies and integration: depends on commit proxy interfaces, resolver interfaces, master reply types, Flow arenas/triggers, and generic actor support. It is included by `MasterData.h` and `masterserver.cpp`.

Risks and test signals: risks are dangling `pVersion`, pending change loss if commit proxy set changes mid-flight, and missing trigger when resolver count crosses one. Tests should cover single resolver no-op, multi-resolver trigger, reply fanout clearing, and version assigned as current master version plus one.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/sequencer/ResolutionBalancer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/sequencer/include/fdbserver/sequencer/MasterServer.h -->
# sources/storage-engines/foundationdb/fdbserver/sequencer/include/fdbserver/sequencer/MasterServer.h

Purpose: exposes the public master/sequencer role actor entry point.

Important APIs and functions: declares `Future<Void> masterServer(MasterInterface mi, Reference<AsyncVar<ServerDBInfo> const> db, Reference<AsyncVar<Optional<ClusterControllerFullInterface>> const> ccInterface, ServerCoordinators serverCoordinators, LifetimeToken lifetime, bool forceRecovery)`.

Control flow, state, and persistence: none in the header. The implementation waits for cluster-controller alignment, constructs `MasterData`, serves version and live-committed-version endpoints, accepts recovery data, and terminates on lifetime replacement.

Dependencies and integration: includes coordination and master interfaces plus Flow primitives; forward-declares cluster-controller and server DB info. Exported through the sequencer library public include path.

Risks and test signals: risks are public signature drift and missing forward declarations. Link tests and role recruitment compilation are the key signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/sequencer/include/fdbserver/sequencer/MasterServer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/sequencer/masterserver.cpp -->
# sources/storage-engines/foundationdb/fdbserver/sequencer/masterserver.cpp

Purpose: implements the master/sequencer actor that assigns monotonically increasing commit-version ranges to commit proxies and publishes live committed version state to readers.

Important APIs and functions: `figureVersion` keeps versions close to wall-clock time while bounding advancement. `getVersion` serializes requests per proxy request number, suppresses duplicates, advances version, and embeds resolver changes. `LiveCommittedVersionServer` handles get/report live committed version requests, including version-vector deltas and waiting for previous versions when needed. `updateRecoveryData` installs epoch/recovery versions, proxy/resolver lists, reference version, and locality. `masterServer` validates cluster-controller identity, composes actors, and exits on lifetime mismatch or normal master errors.

Control flow, state, and persistence: state is in-memory `MasterData`. Recovery data arrives over RPC from recovery machinery; this file does not write disk. Duplicate reply maps are pruned by `mostRecentProcessedRequestNum`.

Dependencies and integration: integrates `MasterInterface`, commit proxies, resolvers via `ResolutionBalancer`, `ServerDBInfo`, cluster controller, version vectors, debug version timestamps, and Flow actor collections.

Risks and test signals: risks include version gaps from clock bugs, request-number ordering stalls, duplicate reply memory growth, live committed version ordering, and forced-recovery locality. Tests cover `figureVersion`; broader signals are master counters, version-vector samples, `MasterTerminated` reasons, and commit proxy progress.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/sequencer/masterserver.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/storageserver/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbserver/storageserver/CMakeLists.txt

Purpose: defines the storage-server support library target and its tests.

Important APIs and functions: `fdb_find_sources(FDBSERVER_STORAGESERVER_SRCS)` gathers sources, `add_flow_target` builds `fdbserver_storageserver`, link and unit tests include core, kvstore, and logsystem dependencies, common include setup exports the public include path, and private local includes are enabled.

Control flow, state, and persistence: declarative build metadata only.

Dependencies and integration: storage-server utilities depend on `fdbserver_core`, key-value store abstractions, and logsystem pieces. The library is a modular subset around storage server helpers rather than the monolithic actor implementation.

Risks and test signals: risks are missing linkage when utilities use kvstore/logsystem types, public include path mistakes, and source discovery omissions. Successful library, link test, and `fdbserver_storageserver_test` build/run are the main signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/storageserver/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/storageserver/ReadLatencySamples.cpp -->
# sources/storage-engines/foundationdb/fdbserver/storageserver/ReadLatencySamples.cpp

Purpose: implements storage-server read latency metric sampling by constructing aggregate and per-read-type latency sketches.

Important APIs and functions: private `createSample` builds a `LatencySample` named from a prefix and metric name using server id, logging interval, sketch accuracy, and silent-interval suppression. `ReadLatencySamples::Entry` creates samples for read, getKey, getValue, getRange, read-version wait, queue wait, KV getRange, mapped range, remote mapped range, and local mapped range. `ReadLatencySamples::sample` records into aggregate and optional per-type samples.

Control flow, state, and persistence: state is owned `LatencySample` objects that emit metrics through tracing infrastructure. No durable storage is used.

Dependencies and integration: depends on storage server knobs and `LatencySample`. Called by storage read paths to report latency dimensions for aggregate and eager/fetch/priority read categories.

Risks and test signals: risks are enum index mismatch between `SampleType` and arrays, missing per-type sample when `ReadType` exceeds `MAX`, and metric-name drift. Signals are expected TraceEvent latency metric names and non-overlapping aggregate/per-type counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/storageserver/ReadLatencySamples.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/storageserver/ReadLatencySamples.h -->
# sources/storage-engines/foundationdb/fdbserver/storageserver/ReadLatencySamples.h

Purpose: declares the storage-server read latency sampler.

Important APIs and types: `ReadLatencySamples::SampleType` enumerates ten latency dimensions plus `END`. Private `Entry` owns a fixed array of `LatencySample` pointers. The class stores an aggregate entry and a `ReadType::MAX + 1` array of per-type entries. Public API is `ReadLatencySamples(UID serverId)` and `sample(double latency, SampleType, Optional<ReadType>)`.

Control flow, state, and persistence: in-memory metric sample holders only. Sampling produces trace/metric output through `LatencySample`.

Dependencies and integration: includes FDB type definitions and stats. Storage-server read code can include this header without depending on construction details.

Risks and test signals: risks are array bounds if new sample/read types are added without matching constructors, and optional read type misuse. Tests should instantiate the sampler, sample every enum value, and verify no crash with absent read type.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/storageserver/ReadLatencySamples.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/storageserver/StorageServerUtils.cpp -->
# sources/storage-engines/foundationdb/fdbserver/storageserver/StorageServerUtils.cpp

Purpose: implements helper utilities for storage-server throughput limiting and persistent keys/values used by physical shard move-in state.

Important APIs and functions: `ThroughputLimiter::ready`, `addBytes`, and `settle` implement a simple byte-cap scheduler based on `nextAvailableSec`. `persistMoveInShardsKeyRange`, `persistUpdatesKeyRange`, `persistUpdatesKey`, `decodePersistUpdateVersion`, `persistMoveInShardKey`, `decodeMoveInShardKey`, `moveInShardValue`, and `decodeMoveInShardValue` encode/decode system-key ranges and values for move-in shard metadata and update streams.

Control flow, state, and persistence: `ThroughputLimiter` is in-memory. Move-in helpers define durable key layout under `\xff\xffMoveInShards/` and `\xff\xffMoveInShardUpdates/`; update versions are big-endian to preserve key ordering. Values serialize `MoveInShardMetaData` with versioned object serialization.

Dependencies and integration: depends on Flow time/delay, FDB binary reader/writer, object serialization, UID/version/key types, and `StorageServerUtils.h`. Used by storage-server shard fetch/restore paths.

Risks and test signals: risks are key prefix collisions, endian decode mistakes, limiter time math when cap changes or zero cap, and serialization compatibility. Tests should round-trip UIDs, versions, metadata values, key ranges, and limiter scheduling under positive and disabled caps.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/storageserver/StorageServerUtils.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/storageserver/StorageServerUtils.h -->
# sources/storage-engines/foundationdb/fdbserver/storageserver/StorageServerUtils.h

Purpose: declares move-in shard metadata, move-in phase states, throughput limiting, and persistent key helper APIs for storage-server physical shard movement.

Important APIs and types: `MoveInPhase` enumerates pending, fetching, ingesting, applying updates, read-write pending, complete, cancel, and error. `MoveInShardMetaData` stores shard id, data move id, key ranges, create/high-watermark versions, phase, checkpoints, optional error, start time, and bulk-load flag. It exposes constructors, ordering by first range begin, phase helpers, destination shard id formatting, `toString`, and serialization. `ThroughputLimiter` exposes `ready`, `addBytes`, and `settle`. Free functions declare move-in key/value encoders.

Control flow, state, and persistence: metadata is serializable persistent state used to resume move-in work. The limiter state is in-memory timing and byte accounting.

Dependencies and integration: depends on FDB key/version/UID types, Flow futures/time, deterministic random IDs, and checkpoint metadata. Storage-server actor code uses these helpers when fetching physical shards and applying updates.

Risks and test signals: risks are phase enum compatibility, omitted `error`/`startTime` from serialization, empty `ranges` in `operator<`, and high-watermark correctness. Tests should cover serialization compatibility, constructor defaults, phase transitions, and key helper round-trips.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/storageserver/StorageServerUtils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/storageserver/TransactionTagCounter.cpp -->
# sources/storage-engines/foundationdb/fdbserver/storageserver/TransactionTagCounter.cpp

Purpose: implements per-storage-server read request tag accounting to identify busiest read tags for ratekeeper auto-throttling.

Important APIs and functions: `TransactionTagCounterImpl::addRequest` converts read bytes to operation cost, scales tagged costs by `READ_TAG_SAMPLE_RATE`, and accumulates interval totals. `startNewInterval` computes elapsed time, selects top K tags above a minimum rate with a priority queue, stores them as `BusyTagInfo`, emits `BusiestReadTag` and `BusyReadTag` traces, and resets interval state. Public `TransactionTagCounter` forwards constructor, destructor, `addRequest`, `startNewInterval`, and `getBusiestTags`. Local tests check max-tag and min-rate filtering.

Control flow, state, and persistence: state is in-memory interval cost maps, total cost, previous busiest tags, and TraceEvent cache holder. There is no durable persistence.

Dependencies and integration: depends on transaction tags, `getReadOperationCost`, client/server knobs, Flow tracing, and the PImpl wrapper declared in `TransactionTagCounter.h`. Storage read paths feed it; ratekeeper later consumes busy tags through storage queuing metrics.

Risks and test signals: risks are sampling-rate zero handling, elapsed-time zero, arena ownership for copied tags, and top-K ordering not being sorted highest-first. Existing tests cover ignoring beyond max tags and below-min-rate tags; additional tests should cover multi-tag requests and zero sample rate.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/storageserver/TransactionTagCounter.cpp -->
