# Research report: subset-b-008459

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/commitproxy/CommitProxyServer.cpp -->
# sources/storage-engines/foundationdb/fdbserver/commitproxy/CommitProxyServer.cpp

## Purpose
This file implements the FoundationDB commit proxy role. It accepts `CommitTransactionRequest` messages from clients, batches them, obtains commit versions from the master, sends conflict ranges to resolvers, applies metadata effects into the transaction state store, assigns durable mutations to TLog tags, pushes commit messages to the log system, reports live committed versions, and replies to clients. It also exposes auxiliary commit-proxy endpoints for key-server location lookup, storage server rejoin information, data-distributor metrics, snapshot requests, exclusion safety checks, throttled shard updates, and transaction-state recovery broadcasts.

## Important APIs, types, and functions
The public entry point is `commitProxyServer(CommitProxyInterface, InitializeCommitProxyRequest, Reference<AsyncVar<ServerDBInfo> const>, std::string)`, declared in the commit proxy header. `CommitProxyServerCore` owns the actor graph and the `ProxyCommitData` state object. `commitBatcher` consumes the proxy's commit stream and emits byte/count-limited batches while enforcing the hard commit-batch memory budget. `CommitBatch::CommitBatchContext` is the per-batch state carrier for all commit phases. `ResolutionRequestBuilder` rewrites versionstamped mutations, maps read/write conflict ranges to resolver requests, records transaction-to-resolver indexes, and keeps maps needed to report conflicting key-range indexes back to clients.

The commit pipeline is split across `preresolutionProcessing`, `getResolution`, `postResolution`, `transactionLogging`, and `reply`, all driven by `commitBatchImpl`. Metadata and mutation helpers include `applyMetadataEffect`, `determineCommittedTransactions`, `applyMetadataToCommittedTransactions`, `rejectMutationsForReadLockOnRange`, `assignMutationsToStorageServers`, `addBackupMutations`, `buildIdempotencyIdMutations` integration, `addAccumulativeChecksumMutations`, and `acknowledgeTransactionStateStoreCommits`. Service actors include `readRequestServer`, `rejoinServer`, `ddMetricsRequestServer`, `monitorRemoteCommitted`, `proxySnapCreate`, `proxyCheckSafeExclusion`, `TxnTagCommitCostReporter`, `IdempotencyIdsExpireServer`, `processTransactionStateRequestPart`, and `updateLocalDbInfo`.

## Control flow
Startup waits until the local DB info has the matching master lifetime and reaches `RECOVERY_TRANSACTION`. It then initializes resolvers, key-resolver maps, log system consumer, disk-queue-backed transaction state store, optional range lock, idempotency cleaner, metrics reporters, and the commit batcher. Incoming batcher output is converted into `commitBatch` futures; non-empty batches always run, and empty batches can advance recovery/commit state once the proxy is accepting commits and the previous commit has completed.

For each batch, pre-resolution waits for local batch ordering, can reject queued batches as `transaction_too_old`, computes version-vector written tags when enabled, checks hot-shard throttling, asks the master for a commit version, and applies resolver assignment changes. Resolution sends per-resolver `ResolveTransactionBatchRequest`s and waits for replies. Post-resolution waits for ordered logging, applies metadata effects from prior proxy batches, merges resolver commit decisions, handles database and range locks, applies committed metadata mutations, assigns user mutations to storage-server tags, emits backup/idempotency/accumulative-checksum mutations, waits if the semi-committed pipeline would exceed the MVCC window, and pushes the assembled `LogPushData`. Logging waits for the log-system push or a later committed-version signal, then pops transaction-state data. Reply reports the live committed version to the master, advances local committed state, sends `CommitID` or conflict errors to clients, coalesces key-resolver history, updates adaptive batching, and releases the local resolving order future.

## State and persistence behavior
Durable commit effects are persisted through the log system and the `txnStateStore` backed by `LogSystemDiskQueueAdapter`. `ProxyCommitData::version` tracks the transaction state store's applied version, while `committedVersion` tracks durable committed versions. `keyResolvers` and `systemKeyVersions` are in-memory resolver-routing history trimmed after the write transaction life window. `keyInfo`, `storageCache`, `tssMapping`, `tag_popped`, backup ranges, range-lock state, and idempotency clears are derived from metadata mutations or transaction-state recovery. Idempotency clear requests are accumulated in memory and later included in commit batches. Remote transaction-state pop progress is tracked by `txsPopVersions` and `lastTxsPop`, with remote-log queue metrics used to decide when remote transaction-state data can be popped.

## Dependencies and integration points
This file sits at the center of the master/resolver/TLog/storage-server/client integration. It depends on `CommitProxyInterface`, `MasterInterface`, `ResolverInterface`, `LogSystem`, `LogSystemConsumer`, `ApplyMetadataMutations`, `ServerDBInfo`, `RatekeeperInterface`, backup mutation helpers, idempotency helpers, accumulative checksum utilities, range locks, actor collection/error plumbing, and tracing. It returns key-server location data used by clients, data distribution, and consistency checks; it relays DD snapshot and exclusion requests; it reports commit-cost estimates to ratekeeper; and it updates version-vector data paths through tag and TPCV maps.

## Risks and edge cases
Correctness depends on strict local ordering between resolving and logging, correct resolver range maps, and atomic metadata effects. The code has explicit liveness timeout conversion to `failed_to_progress`, connection reset heuristics for master/resolver stalls, and memory protection in the batcher. Risky areas include private mutation behavior when `PROXY_USE_RESOLVER_PRIVATE_MUTATIONS` changes who computes metadata mutations, version-vector unicast paths where tag sets and TPCV maps must match the log configuration, range-lock rejection only being enabled outside version vector, the idempotency expiration handshake between clients and expected-count notifications, and snapshot command whitelist parsing. A declaration/implementation mismatch in nearby consistency-scan code was observed, but the commit proxy header and implementation agree on `commitProxyServer`.

## Test signals
The file contains many simulation `CODE_PROBE`s and `TraceEvent`s around queued-batch rejection, shard boundary clears, MVCC-window waits, force recovery, resolver/private mutation behavior, idempotency, snapshot errors, range-lock fast/slow paths, and detailed proxy metrics. `forceLinkCommitProxyTests()` suggests external tests are linked by build machinery. The commit proxy build should exercise this through fdbserver link tests, simulation workloads that force recovery, transaction conflicts, hot shard throttling, range locks, idempotency IDs, backup ranges, version vector, TSS mappings, and data-distribution key-location callers.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/commitproxy/CommitProxyServer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/commitproxy/ProxyCommitData.h -->
# sources/storage-engines/foundationdb/fdbserver/commitproxy/ProxyCommitData.h

## Purpose
This header defines the in-memory data structures shared by the commit proxy implementation. It centralizes counters, histograms, durable-state handles, resolver and storage-server caches, idempotency bookkeeping, version-vector and accumulative-checksum state, range-lock state, and the adapter context that `applyMetadataMutations()` needs without exposing the entire proxy implementation.

## Important APIs and types
`ProxyStats` owns `CounterCollection` metrics, latency sketches, histograms, and special counters for assigned version, committed version, batch memory, and compute estimates. `ExpectedIdempotencyIdCountForKey` carries the expected number of idempotency expiration acknowledgements for a `(commitVersion, high-order batch index)` key group. `ProxyCommitData` is the main mutable role state. Its key helpers are `tagsForKey`, `updateLatencyBandConfig`, `updateSSTagCost`, `rangeLockEnabled`, the constructor, and `getApplyMetadataProxyContext`. `RangeLock` implements `ApplyMetadataRangeLock`, stores decoded range-lock state in a `KeyRangeMap<RangeLockStateSet>`, and exposes the fast-path `anyExclusiveLockHeld()` plus `isLocked()`.

## State and persistence behavior
The header itself persists nothing directly, but it owns handles to persistent subsystems. `txnStateStore` stores transaction subsystem metadata. `logSystem` and `logSystemConsumer` publish and consume durable log data. `version`, `committedVersion`, and `minKnownCommittedVersion` model progress across durable and applied state. `keyInfo`, `storageCache`, `tssMapping`, `tag_popped`, `vecBackupKeys`, `uid_applyMutationsData`, and range-lock maps are populated from recovered state or metadata mutations. `idempotencyClears` is a memory buffer of clear-range mutations to be included in later commits. `acsBuilder` is created only when mutation checksum and accumulative checksum are enabled and version-vector modes are disabled.

## Control flow and integration
`ProxyCommitData` is constructed by `CommitProxyServerCore` before log-system and transaction-state-store initialization are complete; pointer fields such as `logAdapter` and `txnStateStore` start as null and are filled during startup. The commit pipeline reads and mutates this state at every phase: batcher memory counters and stats in intake, resolver and key-info maps during conflict and tag assignment, transaction-state fields during metadata application, ratekeeper maps during commit cost reporting, and range locks before final mutation assignment. `getApplyMetadataProxyContext()` builds the smaller context consumed by the shared metadata mutation engine, passing pointers into `ProxyCommitData` plus a borrowed `RangeLock`.

## Dependencies
The header depends on `FDBTypes`, `RangeLock`, `Stats`, accumulative checksum utilities, `ApplyMetadataMutation`, `Knobs`, log-system interfaces, master/resolver interfaces, and Flow random/actor types. It bridges commitproxy code to core fdbserver metadata logic and the fdbclient id/type definitions used by wire requests.

## Risks and edge cases
The struct is large and mostly unsynchronized because FoundationDB actors run cooperatively; accidental blocking or reentrancy assumptions can still be dangerous. Cached tags in `ServerCacheInfo` must be invalidated by metadata code when tag assignments change. `rangeLockEnabled()` deliberately disables range locks under version-vector and TLog-unicast modes, so callers must not assume configured read locks are always active. `RangeLock::anyExclusiveLockHeld_` is a derived summary; recovery uses monotonic initialization, but normal updates recompute after coalescing so stale fast-path state is a correctness risk if new update paths bypass `consumePendingRequest`. `acsBuilder` availability depends on several knobs, so checksum mutation paths must null-check consistently.

## Test signals
`ProxyStats` exposes production metrics such as `RangeLockFastPath`, `RangeLockSlowPath`, commit latency bands, transaction-size distribution, and commit-batch memory. The range-lock comments and counters identify a specific hot-path optimization that simulation and performance tests should verify. Accumulative checksum paths have trace events in the implementation; idempotency count structures are exercised by commit idempotency workflows; and the header participates in commit proxy link/build tests through the commitproxy target.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/commitproxy/ProxyCommitData.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/commitproxy/include/fdbserver/commitproxy/CommitProxyServer.h -->
# sources/storage-engines/foundationdb/fdbserver/commitproxy/include/fdbserver/commitproxy/CommitProxyServer.h

## Purpose
This public include is the narrow module boundary for starting a commit proxy actor. It hides the large `CommitProxyServer.cpp` implementation and exposes only the `commitProxyServer` coroutine signature needed by worker recruitment code.

## Important API
`Future<Void> commitProxyServer(CommitProxyInterface proxy, InitializeCommitProxyRequest req, Reference<AsyncVar<ServerDBInfo> const> db, std::string whitelistBinPaths)` starts and supervises the commit proxy role. The inputs provide the role's network interface, master initialization request, changing database information, and snapshot-command binary whitelist string. The function returns normally only when handled termination conditions are swallowed in the implementation; unexpected errors are rethrown.

## Control flow and state
The header declares no state and performs no logic. Its main design decision is to forward declare `InitializeCommitProxyRequest` and `ServerDBInfo`, reducing include coupling for callers. Runtime state is owned entirely by `CommitProxyServerCore` and `ProxyCommitData` in the implementation file.

## Dependencies and integration points
The header includes `fdbclient/CommitProxyInterface.h` for the role interface and `flow/flow.h` for `Future`, `Reference`, and `AsyncVar`. It is included by server-role wiring that recruits commit proxies during recovery and passes live `ServerDBInfo` updates.

## Risks and test signals
The API is intentionally small, so the primary risk is signature drift between declaration and implementation. The implementation matches this declaration. Link tests for the commitproxy library and any server recruitment tests should catch missing symbols or include dependency regressions. Behavior-level tests are in the implementation's simulation workload coverage, not in this header.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/commitproxy/include/fdbserver/commitproxy/CommitProxyServer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/consistencyscan/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbserver/consistencyscan/CMakeLists.txt

## Purpose
This build file defines the consistency scan module as a static Flow actor library and wires its public include directory, common fdbserver includes, core dependency, and link test.

## Important build APIs
`fdb_find_sources(FDBSERVER_CONSISTENCYSCAN_SRCS)` gathers module sources. `add_flow_target(STATIC_LIBRARY NAME fdbserver_consistencyscan SRCS ...)` builds them as a Flow-aware static library. `add_fdbserver_link_test(fdbserver_consistencyscanlinktest fdbserver_consistencyscan fdbserver_core)` creates a link-time sanity target. `configure_fdbserver_common_includes(fdbserver_consistencyscan)` applies shared include configuration. `target_include_directories(... PUBLIC include)` exports the module's public headers. `target_link_libraries(... PRIVATE fdbserver_core)` links the implementation to core server functionality.

## Control flow and integration
The file has no runtime control flow. It integrates `ConsistencyScan.cpp` and its header into the fdbserver build graph. The public include directory exposes `fdbserver/consistencyscan/ConsistencyScan.h` to modules and workloads that call `consistencyScan`, `getKeyServers`, `getKeyLocations`, or `checkDataConsistency`.

## State and persistence behavior
Build configuration only; no persistent runtime state. The important persistence implication is indirect: linking this module brings in code that reads and writes `ConsistencyScanState` keys in the system database and issues low-priority storage server reads.

## Dependencies, risks, and test signals
The library links privately to `fdbserver_core`, which supplies worker interfaces, knobs, storage metrics, ratekeeper/server DB info, simulation policy, and system metadata utilities. The link test catches unresolved symbols caused by missing source files or dependencies. A risk observed while reading the sources is that the public header declares `getVersion(Database cx)`, but the implementation defines `getStorageServerReadVersion(Database cx)` instead; this CMake link test may not catch that mismatch unless a consumer references `getVersion`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/consistencyscan/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/consistencyscan/ConsistencyScan.cpp -->
# sources/storage-engines/foundationdb/fdbserver/consistencyscan/ConsistencyScan.cpp

## Purpose
This file implements two related consistency-checking surfaces. The first is the `CONSISTENCYSCAN` server role: a long-lived actor that reads consistency scan configuration from system keys, incrementally scans replicated shard data at controlled rates, compares storage server replies, persists round/lifetime progress, and supports simulation corruption injection. The second, below an explicit divider comment, contains helper routines used by the `ConsistencyCheck` workload for quiescent and workload-level data, shard-size, key-location, and TSS checks.

## Important APIs, types, and functions
Role-local types include `ConsistencyScanStats` for counters and special counters, and `ConsistencyScanMemoryState` for non-persistent role state such as `databaseSize`, `dbInfo`, and stats. Core role functions are `pollDatabaseSize`, `loadShardInterfaces`, `consistencyCheckReadData`, `consistencyScanCore`, `sometimesRandomlyClearStatsInSim`, `resetSimCorruptionCheckOnDeath`, and exported `consistencyScan`. Workload helper functions are `getStorageServerReadVersion`, `testFailure`, `getKeyServers`, `getKeyLocations`, `getStorageSizeEstimate`, `getDatabaseSize`, and exported `checkDataConsistency`.

`consistencyCheckReadData` is the shared comparator. It constructs low-priority `GetKeyValuesRequest`s, optionally supplies version-vector latest commit versions per storage server, waits for all replicas, chooses the first successful reply as the reference, compares data and `more` flags, emits detailed mismatch traces, recognizes expected simulation/TSS/failure cases, and returns an issue count.

## Control flow
`consistencyScan` opens a lock-aware server database, creates memory state, starts role tracing and wait-failure handling, and races `consistencyScanCore` against halt requests and actor errors. `consistencyScanCore` watches `ConsistencyScanState` configuration until enabled. When enabled, it loads lifetime/current-round stats, archives complete or stale rounds, initializes new rounds, trims history, waits for a database-size estimate, and enters an incremental scan loop.

Each scan-loop iteration computes a read rate from database size, estimated replication factor, target round time, and max rate. It loads shard boundaries, storage server interfaces, the config trigger version, and range-specific scan configuration in one transaction. If config changed, it restarts the main loop. Otherwise it skips excluded ranges or scans the target shard/range in chunks. Each chunk reads all replicas at the same read version, compares responses, advances `lastEndKey`, accounts logical and replicated bytes, and handles retryable errors such as `transaction_too_old`, `wrong_shard_server`, `all_alternatives_failed`, and `process_behind`. Progress and stats are committed in a fresh transaction to avoid using an expired read transaction after long replica reads. At `allKeys.end`, the current round is completed, persisted, and the actor waits until `minRoundTimeSeconds` has elapsed before restarting.

The workload section first discovers key-server locations through commit proxies, then reads key-location records directly from storage servers, checks shard metrics and team sizes, optionally includes TSS pairs, compares all replicas for every selected shard, validates byte-sampling estimates, checks split feasibility, and rate-limits based on bytes read in the previous round.

## State and persistence behavior
Persistent scan state lives in `ConsistencyScanState`: config, trigger version, current round stats, lifetime stats, range config, and round history. The actor treats current round and lifetime stats as owned while running, but defends against config updates with trigger-version checks before saving progress. Non-persistent state includes database size estimates from DD tracker status, counters, read-rate controller budget, and simulation corruption state in `fdbSimulationPolicyState`. The workload helpers do not persist their own state except through caller-owned success flags and byte counters.

## Dependencies and integration points
The code depends on system key metadata (`keyServersPrefix`, `serverTagKeys`, `serverListKeyFor`), `ReadYourWritesTransaction`, `SystemDBWriteLockedNow`, `ConsistencyScanState`, worker interfaces/event log requests, storage server `getKeyValues` and `waitMetrics`, data distribution configuration, shard sizing, rate control, simulation policy, TSS mappings, commit proxy `getKeyServersLocations`, and version-vector mapping APIs. It intentionally uses low-priority reads and disables cache result to reduce live-traffic impact.

## Risks and edge cases
The scan must compare replicas at a version before it becomes too old; large shards can force retries and partial progress. Failed or relocating storage servers, killed regions, TSS mismatches, simulation corruption injection, and version-vector latest-version requirements all receive special handling. The range-config skip path appears to assign `lastEndKey` to `configRange->range.begin` when skipping, even though the adjacent comment says it should advance to the configured range end; that is a progress-risk area worth reviewing. The public header declares `getVersion(Database cx)`, but this file defines `getStorageServerReadVersion(Database cx)`; consumers of `getVersion` would fail to link unless another translation unit provides it. Some FIXME/TODO notes identify unimplemented canary keys, cache invalidation, history trim buggification, range-config randomization, change-feed/blob checks, and scan-speed tuning.

## Test signals
The file is heavily instrumented with `TraceEvent`, counters, and `CODE_PROBE`s. Simulation can inject corrupt reads and expects the scan to detect and clear the policy state. `sometimesRandomlyClearStatsInSim` tests stat reset behavior. Workload helpers emit `TestFailure` traces for key-server inconsistency, invalid team size, unavailable storage servers, incorrect sampled estimates, inaccurate shard estimates, and invalid shard sizes. The CMake link test validates module linkage, while simulation workloads should exercise role halt, corruption injection, TSS checks, version vector, relocation, transaction-too-old retries, and range-config skips.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/consistencyscan/ConsistencyScan.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/consistencyscan/include/fdbserver/consistencyscan/ConsistencyScan.h -->
# sources/storage-engines/foundationdb/fdbserver/consistencyscan/include/fdbserver/consistencyscan/ConsistencyScan.h

## Purpose
This public header exposes the consistency scan role entry point and the legacy consistency-check workload helpers implemented in `ConsistencyScan.cpp`.

## Important APIs
`consistencyScan(ConsistencyScanInterface, Reference<AsyncVar<ServerDBInfo> const>)` starts the server role. `getKeyServers` asks commit proxies for shard-to-storage mappings over a key range. `getKeyLocations` reads key-location metadata from storage servers and verifies replica agreement. `checkDataConsistency` performs the main workload-level shard data, metric, team-size, TSS, split, and sampling checks. The header also declares `Future<Version> getVersion(Database cx)`.

## Control flow and state
The header declares APIs only. Callers provide the database or role interface, promises for async results, consistency-check mode flags, client distribution parameters, rate settings, and mutable output pointers such as `success` and `bytesReadInPreviousRound`. Runtime state is kept in the implementation and in caller-owned arguments.

## Dependencies and integration points
The header includes `fdbclient/ConsistencyScanInterface.h` and `flow/flow.h`, relying on transitive availability of FoundationDB database, key range, storage server, and configuration types. It is the exported include path from the `fdbserver_consistencyscan` CMake target and is consumed by server role wiring and consistency workload code.

## Risks and test signals
The declaration `getVersion(Database cx)` does not match the implementation name `getStorageServerReadVersion(Database cx)` in the corresponding source file. If no compatibility wrapper exists elsewhere, any caller using `getVersion` will fail to link; if nobody uses it, the mismatch can remain latent. The large `checkDataConsistency` signature is brittle because many booleans and counters are positional. Link tests and workload builds are the primary signals for API drift, while simulation consistency-check workloads validate behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/consistencyscan/include/fdbserver/consistencyscan/ConsistencyScan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/coordinator/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbserver/coordinator/CMakeLists.txt

## Purpose
This build file defines the coordinator module as a static Flow actor library and wires its link tests, unit tests, include directories, and dependencies. The module contains coordinator server logic and on-demand durable store support, based on the file list in the same directory.

## Important build APIs
`fdb_find_sources(FDBSERVER_COORDINATOR_SRCS)` gathers coordinator sources. `add_flow_target(STATIC_LIBRARY NAME fdbserver_coordinator SRCS ...)` builds them as a Flow-aware static library. `add_fdbserver_link_test(fdbserver_coordinatorlinktest fdbserver_coordinator fdbserver_kvstore fdbserver_core)` validates linkage with core and kvstore dependencies. `add_fdbserver_unit_test(fdbserver_coordinator_test coordinator ...)` registers coordinator unit tests. `configure_fdbserver_common_includes` applies shared include paths. Public includes are exported from `include`, while private includes include the source and binary directories. The library privately links `fdbserver_core` and `fdbserver_kvstore`.

## Control flow, state, and persistence
This file has no runtime control flow. Its dependency choices indicate that coordinator code integrates with core server interfaces and key-value store persistence. The private binary include directory suggests generated/configured headers may be consumed internally. Runtime persistence details are in `Coordination.cpp`, `OnDemandStore.cpp`, and related headers rather than this CMake file.

## Dependencies and integration points
The coordinator library is built as a reusable fdbserver component with public headers under `fdbserver/coordinator`. It depends on `fdbserver_kvstore` for durable local storage and `fdbserver_core` for shared actor/server infrastructure. The unit test target names the suite category `coordinator`, making this module explicitly testable outside full simulation.

## Risks and test signals
The build file is small but important: missing dependencies would surface as link-test failures, and missing public include paths would break downstream role wiring. The explicit unit test target is a strong signal that coordinator logic has dedicated tests. Because this CMake target exports only the `include` directory publicly, internal headers such as `OnDemandStore.h` remain private unless included through the private source path by module sources.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/coordinator/CMakeLists.txt -->
