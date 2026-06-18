# Research Report: subset-b-008481

This grouped report covers three FoundationDB storage-server headers for `subset-b-008481`. Each source file section is delimited for reconciliation into the source-tree-aligned `Docs/researches/<source_path>_research.md` files.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/storageserver/TransactionTagCounter.h -->
# sources/storage-engines/foundationdb/fdbserver/storageserver/TransactionTagCounter.h

## Purpose
`TransactionTagCounter.h` declares the storage-server helper that measures recent read load by transaction tag. Storage servers call it from read request paths to attribute request byte cost to the optional `TagSet` carried by client requests, roll the measurements at a configured interval, and expose the busiest tags to storage queuing metrics so ratekeeper and status surfaces can reason about tag-specific read pressure.

The header is intentionally narrow: it hides the implementation behind `PImpl<class TransactionTagCounterImpl>` so storage-server users do not include the implementation's priority queue, tag map, tracing, and knob dependencies. The public API is the lifecycle and interval interface needed by `storageserver.actor.cpp`.

## Important APIs, Types, and Functions
- `TransactionTagCounter(UID thisServerID, int maxTagsTracked, double minRateTracked)` constructs the counter for one storage server. `thisServerID` is used in trace events, `maxTagsTracked` bounds the retained top-K tag set, and `minRateTracked` filters low-rate tags.
- `~TransactionTagCounter()` is out-of-line because the implementation type is opaque at the declaration site.
- `void addRequest(Optional<TagSet> const& tags, int64_t bytes)` records one read request's cost for the current interval. It accepts absent tags, which still contribute to total interval cost in the implementation but do not create per-tag entries.
- `void startNewInterval()` finalizes the current interval, stores the previous interval's busiest tags, emits trace events, and resets current counters.
- `std::vector<BusyTagInfo> const& getBusiestTags() const` returns the retained busiest tags from the last completed interval. `BusyTagInfo` and `TagSet` come from `fdbclient/StorageServerInterface.h` and `fdbclient/TagThrottle.h`.

## Control Flow
`StorageServer` embeds a `TransactionTagCounter` member. During `storageServerCore`, the server calls `startNewInterval()` once, then schedules a recurring call every `SERVER_KNOBS->TAG_MEASUREMENT_INTERVAL`. Read request actors call `addRequest()` after responding or erroring where the byte cost is known. Call sites include `getValueQ`, `getKeyValuesQ`, `getMappedKeyValuesQ`, `getKeyValuesStreamQ`, and `getKeyQ`; the byte estimate is usually returned bytes, with some path-specific additions such as key size for `getValue`.

At each interval boundary, the implementation computes per-tag rates from accumulated sampled read operation cost divided by elapsed wall-clock time, filters tags below `minRateTracked`, keeps at most `maxTagsTracked` using a min-priority queue, and saves that vector as `previousBusiestTags`. `getQueuingMetrics()` later copies `self->transactionTagCounter.getBusiestTags()` into `StorageQueuingMetricsReply::busiestTags`, integrating the previous interval into queue metrics responses.

## State and Persistence Behavior
The header exposes no persistent state. Runtime state lives only inside `TransactionTagCounterImpl`: server ID, a `TransactionTagMap<double>` of interval costs, total interval cost, interval start time, configuration bounds, a vector of previous busy tags, and an event-cache holder for busiest-read-tag tracing. State resets on process restart and is not written to the storage engine.

The implementation bills each tagged request by `getReadOperationCost(bytes)` and scales per-tag cost by `CLIENT_KNOBS->READ_TAG_SAMPLE_RATE`, while total interval cost is kept unscaled. This makes the busy-tag rate an estimate based on sampled tagged reads. `fractionalBusyness` is derived from the tag cost over interval total cost and is capped at `1.0`. Untagged reads increase total cost but not per-tag cost, lowering fractional busyness for tagged traffic when untagged traffic is present.

## Dependencies and Integration Points
The declaration depends on `fdbclient/PImpl.h` for opaque ownership, `fdbclient/StorageServerInterface.h` for `UID` and `BusyTagInfo`, and `fdbclient/TagThrottle.h` for transaction tag types. The implementation depends on `NativeAPI.actor.h` for read-cost calculation, client knobs, Flow time, `TraceEvent`, and FoundationDB test macros.

The main integration points are the storage-server read actors and `StorageQueuingMetricsRequest` handling in `storageserver.actor.cpp`. Ratekeeper consumes storage queuing metrics from each storage server, so the data exposed by this counter participates in read tag throttling and cluster status observability. Trace events `BusiestReadTag` and `BusyReadTag` are also integration points for diagnostics and status event caches.

## Risks and Edge Cases
The first interval is intentionally ignored because `intervalStart` is zero until the initial `startNewInterval()` call. If the recurring interval is not started, `getBusiestTags()` remains empty even if reads call `addRequest()`.

The returned vector is a const reference to internal state, so callers must not retain it beyond the counter lifetime or expect it to remain stable across `startNewInterval()`. Storage-server code currently copies it into a reply promptly, which matches the contract.

Cost accounting is approximate. Some request paths undercount true scanned bytes, and `getKeyValuesStreamQ` appears to call `addRequest()` inside the stream loop using `resultSize` without updating that local variable in the visible loop, then calls it again after the loop. That is an integration risk for read tag throttling accuracy rather than a persistence risk. The top-K vector is not sorted highest-first when drained from the min-priority queue, so implementation code explicitly scans for the busiest tag when emitting the single `BusiestReadTag` trace. Any consumer that assumes the vector is sorted by descending rate would be fragile.

If `CLIENT_KNOBS->READ_TAG_SAMPLE_RATE` is zero, interval finalization suppresses calculations to avoid division by zero. However, `addRequest()` still divides per-tag cost by the sample rate when tags are present in the implementation, so the surrounding configuration should not allow tagged sampled reads with a zero sample rate between interval ticks.

## Test Signals
`TransactionTagCounter.cpp` contains focused unit tests. `/fdbserver/TransactionTagCounter/IgnoreBeyondMaxTags` verifies that the counter keeps only the configured number of busiest tags and drops lower-rate tags. `/fdbserver/TransactionTagCounter/IgnoreBelowMinRate` verifies that low-rate tags are filtered out. Runtime signals include `BusiestReadTag` and `BusyReadTag` trace events, non-empty `StorageQueuingMetricsReply::busiestTags` during tagged read workloads, and ratekeeper behavior when read tag throttling is enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/storageserver/TransactionTagCounter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/storageserver/include/fdbserver/storageserver/StorageCorruptionBug.h -->
# sources/storage-engines/foundationdb/fdbserver/storageserver/include/fdbserver/storageserver/StorageCorruptionBug.h

## Purpose
`StorageCorruptionBug.h` declares a simulation-only bug descriptor used to inject storage mutation loss in the storage server. It gives FoundationDB simulation workloads a typed handle for enabling, configuring, and counting deliberate corruption events through `SimBugInjector`.

The file contains only the bug payload and its identifier factory. The actual fault behavior is implemented in `StorageServerDisk::writeMutationsBuggy()` in `storageserver.actor.cpp`, and the workload that enables the bug lives in `fdbserver/workloads/StorageCorruption.cpp`.

## Important APIs, Types, and Functions
- `class StorageCorruptionBug : public ISimBug` is the bug payload. It inherits the shared simulation bug accounting behavior, including hit counting through `ISimBug::hit()`.
- `double corruptionProbability = 0.001` controls the per-mutation probability that a mutation is skipped when the bug is active. The default is one corruption attempt per thousand mutation positions.
- `class StorageCorruptionBugID : public IBugIdentifier` identifies this bug type to the injection registry.
- `std::shared_ptr<ISimBug> StorageCorruptionBugID::create() const override` returns a new `StorageCorruptionBug` instance for the injector.

## Control Flow
The header itself has no runtime control flow beyond the inline factory. In simulation, `StorageCorruptionWorkload` creates a `SimBugInjector`, enables a `StorageCorruptionBug` by passing `StorageCorruptionBugID`, optionally overrides `corruptionProbability` from workload options, and enables the injector for a configured duration.

On the storage server side, `StorageServerDisk::writeMutationsBuggy()` asks `SimBugInjector().get<StorageCorruptionBug>(StorageCorruptionBugID())` for the active bug. If none is present, it delegates to the normal `writeMutations()` path. If a bug is active, it scans the mutation vector, writes the contiguous slice before each selected mutation, calls `bug->hit()`, skips that selected mutation, and continues. `makeVersionMutationsDurable()` calls `writeMutationsBuggy()` when applying mutation-log entries to the key-value store, so the fault drops durable storage writes rather than client request handling directly.

## State and Persistence Behavior
`StorageCorruptionBug` stores only the mutable probability in memory. It does not persist to disk and is active only while the simulation injector is enabled. The injected effect, however, deliberately changes storage persistence behavior: selected mutations are not written to the backing `IKeyValueStore` during durable version application. This creates storage contents that diverge from the expected mutation stream, allowing consistency-check and recovery paths to observe corruption.

The workload sets `corruptionProbability` back to `0.0` after its delay, logs the number of hits, disables the injector, and re-enables data distribution. The skipped mutations remain as durable corruption in the simulated storage engine unless later overwritten or cleared by normal cluster activity.

## Dependencies and Integration Points
The header depends on `flow/SimBugInjector.h`, specifically `ISimBug`, `IBugIdentifier`, and the shared injector API. It is included by `storageserver.actor.cpp` and by the `StorageCorruption` simulation workload.

The main integration points are simulation policy and consistency checking. `StorageCorruptionWorkload` disables all other failure-injection workloads, disables data distribution with `setDDMode(cx, 0)`, enables this bug, waits, stops corruption, installs an uncancellable listener for `ConsistencyCheckFailure`, then turns data distribution back on. A severity-error consistency-check failure is treated as negative-test success by tracing `NegativeTestSuccess`.

## Risks and Edge Cases
This type must remain simulation-scoped. Accidentally enabling the injector in non-simulation or production-like tests would intentionally corrupt durable storage data. The current use depends on `SimBugInjector` availability and workload control rather than compile-time exclusion in the header itself.

The probability is public and unconstrained. Values below zero behave like zero in the comparison against `random01()`, values above one drop every mutation encountered, and very high probabilities can make a storage server unusable before the intended consistency-check signal occurs. Because `writeMutationsBuggy()` drops whole mutation entries, not bytes, the impact depends on workload mutation shape: dropping a clear range is much larger than dropping a small set.

The header's identifier creates a fresh bug instance; callers must use the same identifier type when enabling and retrieving the bug or the storage-server path will not see the workload's configuration. The `writeMutationsBuggy()` loop has a critical normal-path behavior: if `get()` returns no bug, it calls `writeMutations()` but does not explicitly return before continuing to dereference `bug`. That implementation detail should be checked carefully in context before changes, because the intended contract is clearly "no bug means normal writes." The test workload exercises the active-bug path, so a separate no-bug coverage signal is useful.

## Test Signals
The direct workload signal is `fdbserver/workloads/StorageCorruption.cpp`. It logs `CorruptionInjections` with `NumCorruptions`, observes `ConsistencyCheckFailure`, and emits `NegativeTestSuccess` when the expected severe consistency-check error is detected. Broader signals include simulation tests using the `StorageCorruption` workload, storage consistency-check traces, and successful cleanup after data distribution is re-enabled. Compile coverage verifies the `IBugIdentifier` factory and typed `SimBugInjector::enable/get` calls remain compatible.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/storageserver/include/fdbserver/storageserver/StorageCorruptionBug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/storageserver/include/fdbserver/storageserver/StorageServer.h -->
# sources/storage-engines/foundationdb/fdbserver/storageserver/include/fdbserver/storageserver/StorageServer.h

## Purpose
`StorageServer.h` declares the two public actor entry points for running a FoundationDB storage server on a worker. One overload initializes a newly recruited storage server, and the other recovers an existing storage server from an already opened key-value store. The implementation in `storageserver.actor.cpp` owns the long-running storage-server state machine, persistence recovery, interface registration, read and mutation-serving actors, metrics, data movement, change feeds, watches, checkpointing, and shutdown cleanup.

The header is intentionally small because `StorageServer` itself is a large internal struct in the actor implementation. External worker code only needs to spawn the actor with the correct persistent store, network interface, cluster state, folder paths, and recruitment/recovery promises.

## Important APIs, Types, and Functions
- `Future<Void> storageServer(IKeyValueStore* persistentData, StorageServerInterface ssi, Tag seedTag, Version startVersion, Version tssSeedVersion, ReplyPromise<InitializeStorageReply> recruitReply, Reference<AsyncVar<ServerDBInfo> const> db, std::string folder)` starts a newly recruited storage server. It initializes the key-value store, registers or adopts a tag, makes new server metadata durable, replies to the recruiter with `InitializeStorageReply`, and then enters `storageServerCore`.
- `Future<Void> storageServer(IKeyValueStore* persistentData, StorageServerInterface ssi, Reference<AsyncVar<ServerDBInfo> const> db, std::string folder, Promise<Void> recovered, Reference<IClusterConnectionRecord> connRecord)` starts an existing storage server during worker recovery. It initializes and commits the store, restores durable state, registers the recovered interface, resolves memory-store removal races, signals `recovered`, and then enters `storageServerCore`.
- Forward declarations keep this public header light: `IClusterConnectionRecord`, `IKeyValueStore`, `InitializeStorageReply`, and `ServerDBInfo`.
- Included types from `fdbclient/StorageServerInterface.h` and `flow/flow.h` provide `StorageServerInterface`, `Tag`, `Version`, `ReplyPromise`, `Promise`, `Reference`, `AsyncVar`, and `Future`.

## Control Flow
Worker code opens or reuses an `IKeyValueStore`, builds a `StorageServerInterface`, and calls the appropriate overload. For new recruitment, `worker.actor.cpp` passes seed tag and initial cluster versions from the recruitment request and wires the returned future through I/O error handling and rollback reboot logic. For recovery, worker startup iterates existing stores and calls the recovery overload, collecting the `recovered` promises so process startup can wait for durable state restoration.

In the new-server path, the implementation constructs an internal `StorageServer self`, sets shard-aware mode, handles TSS pairing if needed, initializes and commits the storage engine, creates checkpoint directories, clears bulk dump/load scratch folders, and either calls `addStorageServer()` to allocate a fresh tag or uses the supplied seed tag. It persists new-storage-server metadata with `makeNewStorageServerDurable()`, starts interface registration, sends `InitializeStorageReply`, initializes byte-sample recovery to `Void()`, then runs `storageServerCore(&self, ssi)`.

In the recovery path, the implementation reconstructs folder subpaths, ensures checkpoint folders exist, clears transient bulk folders, starts RocksDB log cleanup, initializes and commits the storage engine, races memory-store commit against `memoryStoreRecover()` to handle servers that should be removed, calls `restoreDurableState()`, validates TSS identity, publishes `recovered`, registers the interface, and then runs the same `storageServerCore`.

`storageServerCore` starts the major service actors: update processing, metrics, read request streams, watches, change feeds, shard-state and checkpoint handlers, storage audits, bulk dump/load handling, consistency checks, tag measurement intervals, and queue-metric handling. It then loops on database-info changes, tlog update progress, endpoint requests, and actor failures.

## State and Persistence Behavior
The header's parameters define the persistence boundary. `persistentData` is the durable `IKeyValueStore` owned by the storage server actor until termination. The new path persists server identity and metadata by calling `makeNewStorageServerDurable()` and committing before replying to recruitment. The recovery path reads persisted durable state through `restoreDurableState()` and may return early if no valid durable storage server state exists.

The implementation stores and restores versions, tags, shard metadata, byte sample data, TSS quarantine state, checkpoint metadata, and mutation-log application state. `folder` is used to derive checkpoint, fetched-checkpoint, bulk dump, and bulk load directories; checkpoint directories are created if missing, and transient bulk directories are cleared on start. Termination closes, disposes, or leaves the key-value store depending on error code: worker removal and recruitment failure dispose persistent data, reboot leaves it alone, and most other exits close it.

The actor publishes its network endpoints through `StorageServerInterface`. Registration updates system keys such as server list, server tag, tag history, and TSS mappings with lock-aware system-immediate transactions. The recovered overload uses `IClusterConnectionRecord` only for memory-backed stores that may need to connect to the cluster and determine whether the server can be removed safely.

## Dependencies and Integration Points
The declaration depends directly on `StorageServerInterface` and Flow actor types. The implementation integrates with worker recruitment and reboot logic, `IKeyValueStore` implementations, the log system, data distribution, ratekeeper, commit proxies, storage metrics, consistency scan, checkpoint and bulk dump subsystems, change feed streams, watch APIs, TSS pairing/quarantine, and system-key metadata helpers.

Worker call sites in `worker.actor.cpp` wrap the returned future with `handleIOErrors`, `storageServerRollbackRebooter`, and role error forwarding. `StorageServerInterface` is persisted in the database server list, so changes to interface behavior must be coordinated with client and management APIs. The storage server also reports queuing metrics, busy read tags, and storage state to ratekeeper and status collection.

## Risks and Edge Cases
The overloads take a raw `IKeyValueStore*`; ownership is managed by actor lifetime and termination code. A caller must not delete or reuse the store while the returned future is active. Error-code-specific cleanup is critical: disposing data on the wrong error could destroy recoverable storage, while closing when removal is final could leave stale files.

Recruitment and recovery have different interface-registration timing. New servers start accepting requests before `addStorageServer()` when no seed tag is provided, then durable metadata and recruiter reply follow; recovered servers first perform a non-accepting registration, then create a second registration future gated by `registerInterfaceAcceptingRequests`. Changes to this sequencing can affect availability, duplicate registration, and wrong-shard behavior.

TSS handling is intertwined with persistent identity. The new path sets the TSS pair before initialization, while recovery treats the persisted storage file as source of truth for TSS identity and updates the interface pair ID. Incorrect pair handling can cause a TSS to be registered as a normal storage server or rejoin the TSS map while quarantined.

The actor stack stores `StorageServer self` on the coroutine frame and passes `&self` to many child actors. The implementation cancels `storageServerCore`, halts locks, clears move-in shards, and waits a tick on termination to avoid dangling uses. Any new long-lived child actor must be added to the same lifetime discipline.

## Test Signals
Direct signals are build/link coverage for worker call sites and both overload signatures. Runtime signals include storage-server recruitment tests, worker reboot/recovery simulation, storage engine rollback tests, TSS simulation, memory-store recovery/removal behavior, and shard movement tests. Important traces include `StorageServerInitProgress`, `StorageServerInit`, `StorageServerRebootStart`, `SSTimeRestoreDurableState`, `StorageServerStartingCore`, `StorageServerTerminated`, `KVSRemoved`, and registration/tag traces such as `SSTag` and `SSHistory`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/storageserver/include/fdbserver/storageserver/StorageServer.h -->
