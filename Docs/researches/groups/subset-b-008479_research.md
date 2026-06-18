# subset-b-008479 Research

Grouped research report for FoundationDB logsystem cursor/recovery interfaces and mock S3 support. Each source section preserves the exact source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/logsystem/LogSystemPeekCursor.cpp -->
# sources/storage-engines/foundationdb/fdbserver/logsystem/LogSystemPeekCursor.cpp

## Purpose
Implements the concrete log peek cursor stack used by FoundationDB recovery and log consumers to read ordered log messages from one TLog, from replicated TLogs, across multiple log sets, across epoch history, or through a buffering merge. It is the runtime implementation behind the cursor declarations in `LogSystemTypes.h` and the `IPeekCursor`/`IReplayPeekCursor` contracts in `LogSystem.h`.

## Important APIs, Types, And Functions
`ServerPeekCursor` reads one TLog via `TLogInterface::peekMessages` or `peekStreamMessages`. `MergedPeekCursor` merges replicas within one log set by quorum or replication policy. `SetPeekCursor` merges candidate `LogSet`s and prefers a best set/server when available. `ReplayMultiCursor` and `MultiCursor` stitch epoch ranges. `BufferedCursor` preloads and sorts messages from multiple cursors. Helper actors include `tryEstablishPeekStream`, `serverPeekParallelGetMoreImpl`, `serverPeekStreamGetMoreImpl`, `serverPeekGetMoreImpl`, `mergedPeekGetMore`, `setPeekGetMore`, `bufferedGetMoreLoader`, and `bufferedGetMore`.

## Control Flow
`ServerPeekCursor::getMore()` returns immediately when a message is already buffered for non-parallel peeks; otherwise it chooses streaming, parallel, or single-request peek paths. Replies are normalized through `updateCursorWithReply()`, which resets the arena reader, updates spilled/popped state, advances to the prior cursor position, and exposes the next message. Merge cursors repeatedly request data from a preferred active cursor or enough peer cursors to make progress, then select a message version by best-server, read quorum, or policy satisfaction. Multi cursors drop completed epoch-range cursors once the active cursor reaches its epoch end. Buffered cursor loaders fill per-source queues until a common minimum version boundary allows globally ordered output.

## State And Persistence Behavior
The file does not write durable state; it tracks transient read state in arenas, readers, message versions, popped versions, outstanding futures, reply streams, locality/policy metadata, and buffered queues. `popped()` aggregates observed popped versions so consumers can discard safe ranges. `getMinKnownCommittedVersion()` and `getMaxKnownVersion()` expose TLog progress returned in peek replies. Connection reset metrics are maintained per cursor and may reset a transport connection after slow peek statistics cross knob thresholds.

## Dependencies And Integration Points
The implementation depends on `TLogInterface` RPC endpoints, `FailureMonitor`, Flow futures/coroutines, `SERVER_KNOBS`, replication policy helpers, `LocalitySet`, `TagsAndMessage`, and debug trace utilities. It is used by `LogSystemConsumer.cpp` to construct peek cursors for storage, log-router, TXS, and recovery paths. Version-vector unicast recovery integrates through `knownLockedTLogIds`, `bestServer`, and `returnEmptyIfStopped` behavior.

## Risks And Edge Cases
Peek progress depends on correctly handling interface changes, end-of-stream, broken promises, and request timeouts. Parallel peeks must reject stale replies whose begin version does not match the expected begin. Streaming peeks must reset on connection failure, obsolete operations, or maybe-delivered requests. Merge selection can advance past a target sequence when one replica lacks the exact message, so the code loops until stable and emits probes. Version-vector unicast empty-range returns are intentionally conservative when best-set information is unclear. Buffered cursor `isExhausted()` is asserted false and should not be used as a reliable exhaustion signal.

## Test Signals
Signals include Flow unit/simulation tests that exercise log recovery, storage-server log replay, transaction-state recovery, and version-vector unicast paths. Runtime trace events such as `SPC_GetMore`, `PeekReplyTimeout`, `SlowPeekStats`, and merge/set cursor probes help diagnose stalls, slow TLogs, stale endpoints, and policy-selection issues.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/logsystem/LogSystemPeekCursor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/logsystem/LogSystemRecoveryTests.cpp -->
# sources/storage-engines/foundationdb/fdbserver/logsystem/LogSystemRecoveryTests.cpp

## Purpose
Provides focused Flow unit tests for `getRecoverVersionUnicast()`, the version-vector/unicast recovery-version calculation declared in `LogSystem.h` and implemented in `LogSystem.cpp`.

## Important APIs, Types, And Functions
`makeSingleLogSet()` builds a `LogSet` containing synthetic `TLogInterface`s. `makeLogGroupResults()` creates the tuple consumed by `getRecoverVersionUnicast()`: replication factor, `TLogLockResult` vector, and the unavailable-TLog policy result. Test cases construct `UnknownCommittedVersions` chains and assert returned `(maxKCV, recoverVersion)` tuples.

## Control Flow
Each test exits early when `SERVER_KNOBS->ENABLE_VERSION_VECTOR_TLOG_UNICAST` is disabled. Otherwise it creates local TLog interfaces, packages lock results and unknown committed versions, calls `getRecoverVersionUnicast()`, asserts that a result exists, and checks the maximum known committed version plus selected recovery version.

## State And Persistence Behavior
No persistent state is written. Test state is synthetic in-memory log-set metadata, `TLogLockResult` contents, and unknown committed version vectors. The tests intentionally vary known committed versions, replication factor, local/non-local log sets, unavailable policy flags, delivery sets, and version chains.

## Dependencies And Integration Points
The file includes `LogSystem.h` and `flow/UnitTest.h`. It indirectly validates how `LogSystem::getDurableVersion()` results are interpreted during epoch recovery, especially when version-vector unicast is enabled and recovery must decide how far beyond max KCV it can safely advance.

## Risks And Edge Cases
Covered cases include fallback to max KCV with no unknown versions, halting on missing delivery, replication-policy failure, respecting versions above max KCV, broken `prevVersion` chains, ignoring non-local extra log sets, partial availability policy failure, filtering versions at or below max KCV, and sparse/random version chains that should not skip gaps.

## Test Signals
The file is itself the test signal. Trace events with names like `SimpleTestRecoverVersionFailed` and `BrokenChainTestRecoverVersionFailed` provide detailed diagnostics before assertions fail.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/logsystem/LogSystemRecoveryTests.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/ApplyMetadataMutation.h -->
# sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/ApplyMetadataMutation.h

## Purpose
Defines the shared metadata-mutation application interface used by commit-proxy, resolver, and related recovery/configuration code. It intentionally avoids depending on the full commit-proxy data structure by exposing narrow context structs.

## Important APIs, Types, And Functions
`ApplyMetadataRangeLock` abstracts pending range-lock request handling. `ApplyMutationsData` tracks an apply worker, end version, and key-version map. `ApplyMetadataProxyContext` packages proxy-side state such as transaction state store, backup key map, server cache, commit stream, committed version, storage cache, popped tags, TSS mapping, checksum builder, epoch, and optional range lock. `ResolverData` packages resolver-side fields including `LogSystemConsumer`, `LogPushData`, pop version, and caches. Functions include `isMetadataMutation()`, `getStorageInfo()`, overloads of `applyMetadataMutations()`, and `containsMetadataMutation()`.

## Control Flow
Callers first detect system-key mutations using `isMetadataMutation()` or `containsMetadataMutation()`. Proxy or resolver code then calls the appropriate `applyMetadataMutations()` overload with an arena, span context, version, pop version, and context. The concrete implementation, outside this header, applies system-key changes to transaction state, storage metadata, backup metadata, log-system pop state, and configuration-change signals.

## State And Persistence Behavior
The header defines pointers/references to persistent or semi-persistent state: `IKeyValueStore` transaction state, `KeyRangeMap` metadata, storage caches, tag popped versions, committed-version notification, and checksum builder. The header itself persists nothing, but its interfaces are used to mutate metadata durable enough to participate in recovery and configuration management.

## Dependencies And Integration Points
Depends on FDB client/server metadata types: `BackupAgent`, `MutationList`, `Notified`, `StorageServerInterface`, `SystemData`, `IKeyValueStore`, `LogProtocolMessage`, `LogSystemConsumer`, and Flow reference utilities. It integrates resolver metadata application with commit-proxy log pushes and cluster-controller style initial/broadcast metadata application.

## Risks And Edge Cases
`isMetadataMutation()` is explicitly conservative: many system-key mutations may be treated as metadata even if not all are processed by the implementation. Most context fields are raw pointers and must outlive the call. Resolver and proxy paths differ in available state, so overload selection and null handling are important. Range-lock and checksum hooks add high-impact side effects if inconsistently wired.

## Test Signals
Test signals are mostly indirect through resolver, commit-proxy, recovery, configuration-change, range-lock, backup, and TSS mapping tests. A useful local signal is whether metadata mutation batches force `confChanges` when expected and whether tag pop versions and transaction-state keys are updated consistently.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/ApplyMetadataMutation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/LogSystem.h -->
# sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/LogSystem.h

## Purpose
Declares the central FoundationDB log-system API: push-side message construction, log epoch state, recovery and epoch transitions, log-set routing, pop tracking, TLog locking/durable-version computation, and the peek cursor base interfaces used by consumers.

## Important APIs, Types, And Functions
`IPeekCursor` defines sequential log-consumption operations. `IReplayPeekCursor` adds replay-specific location, max-known-version, clone, and advance operations. `LogPushData` batches tagged log messages and encodes span/transaction info. `OldLogData`, `IdToInterf`, `LogLockInfo`, and `DurableVersionInfo` model old epochs, lock replies, and durability policy results. `LogSystem` exposes construction from configs, `recoverAndEndEpoch()`, `newEpoch()`, `push()`, `makeConsumer()`, pop helpers, backup-worker mutation, rejoin tracking, durable version helpers, and `getRecoverVersionUnicast()`.

## Control Flow
Callers construct a `LogSystem` from core state/log-system config, build `LogPushData`, route tags to TLogs through log-set location helpers, and call `push()` with a `LogPushVersionSet`. Consumers obtain a `LogSystemConsumer` for peeking and popping. During recovery, old state is converted to a log system, TLogs are locked, durable/recover versions are computed, old generations are purged, and a new epoch is recruited/written back to core state.

## State And Persistence Behavior
`LogSystem` carries epoch-local and old-generation state: TLog sets, router/TXS tag counts, pseudo-localities, recovery futures, recovered-version variables, lock results, known locked/stopped TLog IDs, recover-at/recovered-at versions, known committed version, backup start version, pop actors, outstanding pops, old log data, and backup-worker tags. Template `LogPushData::writeTypedMessage()` serializes messages with length, subsequence, tags, optional remote router tag, and span context into per-location binary writers.

## Dependencies And Integration Points
The header depends on database configuration, replication/locality policy, backup progress, DBCoreState, mutation tracking, span context messages, TLog interfaces, WorkerInterface, Flow actor/future utilities, histograms, and knobs. It is used by commit proxies, GRV proxies, resolvers, cluster recovery, backup workers, TLog servers, and logsystem implementation files.

## Risks And Edge Cases
Correctness relies on matching replication policy, locality routing, pop semantics, old epoch history, pseudo-locality mapping, and remote/satellite log behavior. `LogPushData::writeTypedMessage()` reuses serialized bytes across locations after writing the first copy, so writer offsets and message lengths are critical. Recovery code must distinguish known committed, durable, minimum durable, recover-at, and stopped/locked TLog states. Raw pointers and actor futures in `LogSystem` make lifetime and shutdown ordering important.

## Test Signals
Signals include log-system unit tests, recovery simulation tests, `LogSystemRecoveryTests.cpp`, transaction-state recovery, proxy commit-path tests, and traces around push, epoch end, lock replies, rejoin tracking, and durable-version computation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/LogSystem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/LogSystemConsumer.h -->
# sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/LogSystemConsumer.h

## Purpose
Declares a narrow consumer-facing wrapper around `LogSystem` so storage servers and other log readers can peek and pop without direct access to epoch recruitment, push, and recovery internals.

## Important APIs, Types, And Functions
`LogSystemConsumer` is reference-counted and stores a `Reference<LogSystem>`. It exposes `peekAll()`, `peekRemote()`, multiple `peek()` overloads, `peekLocal()`, `peekTxs()`, `peekSingle()`, `peekLogRouter()`, `popLogRouter()`, `popTxs()`, `pop()`, `getTxsPoppedVersion()`, `getEnd()`, and `getPseudoPopTag()`.

## Control Flow
Consumers call peek methods with a database ID, begin/end versions, tags, locality hints, and parallel-get-more options. The implementation constructs appropriate cursor combinations from current and old log generations. Consumers call pop methods after durable consumption to advance TLog pop state for data tags, TXS tags, or log-router tags.

## State And Persistence Behavior
The wrapper stores only the underlying `LogSystem` reference. Popping mutates `LogSystem` state and sends pop requests to TLogs in the implementation. Peek calls expose cursor state but do not themselves persist data.

## Dependencies And Integration Points
Depends directly on `LogSystem.h` and thus the cursor interfaces and log-system model. Used by storage servers, backup/range-backup consumers, transaction-state recovery through `LogSystemDiskQueueAdapter`, and resolver/proxy metadata mutation code.

## Risks And Edge Cases
Multiple peek modes differ subtly: local versus remote, TXS versus log-router, single-tag history versus multi-tag buffered reads, and use of satellite/known-stopped TLog IDs. Incorrect locality or end-version selection can over-read, under-read, or miss old generation data. Pop calls require durable-known-committed context for safe trimming.

## Test Signals
Signals are mostly integration-level: storage recovery, backup log reading, log-router tests, TXS transaction-state replay, and traces in `LogSystemConsumer.cpp` plus cursor traces in `LogSystemPeekCursor.cpp`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/LogSystemConsumer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/LogSystemDiskQueueAdapter.h -->
# sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/LogSystemDiskQueueAdapter.h

## Purpose
Declares an `IDiskQueue` adapter that lets `KeyValueStoreMemory` treat the log system as a backing queue for transaction-state/configuration data during recovery and commit processing.

## Important APIs, Types, And Functions
`PeekTxsInfo` carries primary locality, secondary locality, and known committed version for TXS peeking. `LogSystemDiskQueueAdapter` implements `IDiskQueue`, exposes `setNextVersion()`, `getCommitMessage()`, `readNext()`, `getNextReadLocation()`, `push()`, `pop()`, `commit()`, close/error methods, and the factory `openDiskQueueAdapter()`. `CommitMessage` packages pushed messages, a pop target, and an acknowledge promise.

## Control Flow
During recovery the constructor can create a `LogSystemConsumer::peekTxs()` cursor from the TXS popped version and locality info. `push()` stores data for the next commit version, `pop()` records the durable pop target, and `commit()` does not push to TLogs directly; instead it makes a `CommitMessage` available and waits for the caller to acknowledge after calling `LogSystem::push()` and `LogSystemConsumer::pop()`.

## State And Persistence Behavior
The adapter tracks recovery read locations and queued recovery bytes, pending pushed data, popped-up-to version, promise waiters, next commit version, discarded data state, and total recovered bytes. Persistent durability is delegated to the log system and TLogs; the adapter is a coordination layer over log messages.

## Dependencies And Integration Points
Depends on `IDiskQueue`, `LogSystem`, and `LogSystemConsumer`. Implementation references show use by commit proxy, GRV proxy, resolver, and cluster recovery for transaction-state replay and configuration commit discard/ack handling.

## Risks And Edge Cases
Several `IDiskQueue` methods intentionally assert or throw because random reads, push-location reporting, and storage-byte accounting are not supported. Commit correctness depends on the caller honoring the two-phase contract: receive commit message, push/pop externally, then acknowledge. Locality changes during TXS recovery can switch peek behavior, so read ordering and popped-data handling are sensitive.

## Test Signals
Signals are integration tests for recovery and transaction subsystem state, plus implementation-level behavior in `LogSystemDiskQueueAdapter.cpp`. Failures tend to appear as stalled `commit()` futures, missing transaction-state replay, or incorrect configuration recovery.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/LogSystemDiskQueueAdapter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/LogSystemFactory.h -->
# sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/LogSystemFactory.h

## Purpose
Declares convenience factory functions that construct `LogSystem` or `LogSystemConsumer` instances from `ServerDBInfo`, `LogSystemConfig`, old log-system config, or recovery epoch state.

## Important APIs, Types, And Functions
Functions include `makeLogSystemFromServerDBInfo()`, `makeLogSystemConsumerFromServerDBInfo()`, `makeLogSystemFromLogSystemConfig()`, `makeOldLogSystemFromLogSystemConfig()`, and `recoverAndEndLogSystemEpoch()`.

## Control Flow
Callers pass database ID, locality, core DB info/config, optional recovered-at behavior, remote-log exclusion, and an actor collection stream. Factories delegate to static `LogSystem` constructors and `recoverAndEndEpoch()` so callers do not manually select the constructor path.

## State And Persistence Behavior
The header owns no state. Returned log systems carry epoch/core-state-derived state, and `recoverAndEndLogSystemEpoch()` writes through the recovery flow implemented by `LogSystem`.

## Dependencies And Integration Points
Depends on `LogSystem.h`. Search references show use in TLog server data setup, commit proxy, GRV proxy, resolver, backup worker, range backup worker, and cluster recovery.

## Risks And Edge Cases
Factory defaults (`useRecoveredAt=false`, `excludeRemote=false`) matter for recovery and backup callers. Passing incorrect locality or old/current config choice can cause log consumers to read the wrong generation or include/exclude remote logs incorrectly.

## Test Signals
Signals are primarily downstream: successful proxy/resolver/TLog startup, recovery from `ServerDBInfo`, and backup/range-backup log reads. `LogSystemFactory.cpp` is the implementation target for direct factory behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/LogSystemFactory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/LogSystemTypes.h -->
# sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/LogSystemTypes.h

## Purpose
Declares concrete log-system data structures and cursor classes that are implemented across `LogSystem.cpp`, `LogSet.cpp`, and `LogSystemPeekCursor.cpp`.

## Important APIs, Types, And Functions
`LogSet` models one replicated log-set with TLogs, routers, backup workers, connection/push metrics, replication factor, write anti-quorum, locality data, policy, satellite tag locations, and push-location helpers. Cursor classes include `ServerPeekCursor`, `MergedPeekCursor`, `SetPeekCursor`, `ReplayMultiCursor`, `MultiCursor`, and `BufferedCursor`. `BufferedCursor::BufferedMessage` stores arena-owned message, tags, and version for sorted merge output.

## Control Flow
`LogSet` constructors convert `TLogSet`/`CoreTLogSet` config into runtime interfaces and locality/policy data. `getPushLocations()` maps tags to TLog indexes for writing. Cursor classes expose a common flow: `getMore()`, inspect `hasMessage()`, read message/tags, `nextMessage()`, advance or clone if needed. Merge/set cursors combine multiple `ServerPeekCursor`s, multi cursors sequence epochs, and buffered cursors reorder batched input from multiple sources.

## State And Persistence Behavior
These classes hold in-memory routing, cursor, arena, message, future, locality, replication-policy, and pop-version state. They do not persist directly; persistent log data lives in TLogs and core-state/log-system config. `LogSet` stores backup-worker and log-router interfaces that affect external state through other implementation files.

## Dependencies And Integration Points
Depends on `LogSystemConfig` and `DBCoreState`; cursor inheritance depends on interfaces from `LogSystem.h`. The types integrate with log pushing, log-system recovery, consumer peek methods, replication policy checks, backup worker assignment, and old-generation replay.

## Risks And Edge Cases
`LogSet` routing must preserve tag locality mapping, satellite tag tables, replication policy membership, and write anti-quorum assumptions. Cursor clones must be no-more snapshots that do not accidentally continue network reads. Buffering and merge cursors depend on stable `LogMessageVersion` ordering and arena lifetimes. Locality and known locked/stopped TLog IDs affect version-vector unicast safety.

## Test Signals
Signals include log-system cursor behavior, old-generation replay, backup/log-router recovery, push-location tests, and traces from `LogSystemPeekCursor.cpp` and `LogSet.cpp`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/LogSystemTypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/mocks3/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbserver/mocks3/CMakeLists.txt

## Purpose
Builds the FoundationDB mock S3 server support library and its unit test target.

## Important APIs, Types, And Functions
Uses `fdb_find_sources(FDBSERVER_MOCKS3_SRCS)`, `add_flow_target(STATIC_LIBRARY NAME fdbserver_mocks3 ...)`, `add_fdbserver_unit_test(fdbserver_mocks3_test mocks3 ...)`, `configure_fdbserver_common_includes()`, include-directory configuration, and `target_link_libraries()`.

## Control Flow
CMake discovers mock S3 sources, builds them into the static `fdbserver_mocks3` library, registers `fdbserver_mocks3_test` with dependencies on `fdbserver_mocks3`, `fdbserver_core`, and `fdbclient`, exposes the local `include` directory publicly, adds RapidJSON privately, and links `fdbclient`.

## State And Persistence Behavior
No runtime state is managed. Build state consists of generated targets, include paths, and link dependencies in the CMake graph.

## Dependencies And Integration Points
Integrates the mock S3 library into FoundationDB's Flow/FDB server build system and unit-test infrastructure. RapidJSON is required privately by `MockS3Server.cpp` persistence metadata serialization.

## Risks And Edge Cases
If source discovery omits a new mock S3 source or RapidJSON include path changes, the target or tests fail to compile. Public include exposure is required for consumers of `fdbserver/mocks3/*.h`.

## Test Signals
Successful configuration/build of `fdbserver_mocks3` and execution/registration of `fdbserver_mocks3_test` are the primary signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/mocks3/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/mocks3/MockS3Server.cpp -->
# sources/storage-engines/foundationdb/fdbserver/mocks3/MockS3Server.cpp

## Purpose
Implements a deterministic mock S3 HTTP server for FoundationDB simulation and ctests, supporting object CRUD, bucket operations, list operations, tagging, multipart upload, optional persistence, and direct request processing for chaos wrappers.

## Important APIs, Types, And Functions
`MockS3GlobalStorage` stores buckets, objects, multipart uploads, persistence directory, and load/enabled flags. `ObjectData` stores content, headers, tags, ETag, and last-modified timestamp. `MultipartUpload` stores upload ID, target bucket/object, parts, metadata, and initiation time. Persistence helpers include `atomicWriteFile()`, `readFileContent()`, `deletePersistedFile()`, JSON serializers/deserializers, `persistObject()`, `persistMultipartState()`, `deletePersistedObject()`, `deletePersistedMultipart()`, `loadPersistedObjects()`, and `loadPersistedMultipartUploads()`. `MockS3ServerImpl` routes requests through handlers for multipart, tags, list, bucket, and object operations. Public entry points include `processMockS3Request()`, `startMockS3Server()`, `startMockS3ServerReal()`, `clearMockS3Storage()`, `enableMockS3Persistence()`, `loadMockS3PersistedStateFuture()`, `initializeMockS3Persistence()`, and `registerMockS3Server()`.

## Control Flow
Incoming requests are logged, parsed into bucket/object/query parameters, and routed by query keys and HTTP verb. Multipart start returns an existing upload ID for the same object when present or creates and persists a new upload. Upload-part stores part content by part number and persists multipart state. Complete concatenates parts in key order, creates the final object, persists it, deletes upload state, and returns XML. Object `PUT`, `GET`, `DELETE`, and `HEAD` update/read global storage and response headers. List builds XML pages from sorted object names using prefix, marker/continuation token, and max-keys. Simulation registration enables persistence, loads prior state, and registers an HTTP handler once per address.

## State And Persistence Behavior
All mock S3 data is in a function-local static `MockS3GlobalStorage`, intentionally shared across simulated processes. Persistence writes objects under `<dir>/objects/<bucket>/<object>.data` plus `.meta.json`, and multipart state under `<dir>/multipart/<uploadId>.state.json` plus per-part files and metadata. Atomic writes use unique nondeterministic temp paths and `OPEN_ATOMIC_WRITE_AND_CREATE`; deletes are durable and best-effort. Loading sorts directory listings for deterministic replay. `clearMockS3Storage()` clears in-memory buckets/uploads but not the server registry.

## Dependencies And Integration Points
Depends on `fdbrpc/HTTP`, simulator HTTP registration, Flow trace/random/async-file/platform utilities, and RapidJSON. `processMockS3Request()` is used by `MockS3ServerChaos.cpp` to wrap normal processing. The server backs S3 blob-store tests and workloads that need deterministic S3 semantics inside FoundationDB simulation or standalone ctest HTTP mode.

## Risks And Edge Cases
The implementation is intentionally simplified and not a full S3 clone. XML parsing for tags is regex-based. Path components are not URL-decoded, but query values are. Range requests support `bytes=start-end` and open-ended ranges, but suffix byte ranges are not supported. `handleGetObject()` clamps ranges to `content.size() - 1`, which is delicate for empty content. Persistence skip-if-exists behavior avoids duplicate concurrent writes but can conflict with true last-writer-wins overwrite expectations. Multipart completion trusts stored parts and ignores the client completion XML part list. Registry state must stay aligned with simulator HTTP handlers to avoid duplicate registration assertions.

## Test Signals
Inline unit tests cover request parsing and range-header parsing. Build target `fdbserver_mocks3_test` exercises these tests. Integration signals include S3 blob-store workload success, persistence load/restore trace events, correct ETag/MD5 headers, multipart final object size, and real HTTP ctest startup.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/mocks3/MockS3Server.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/mocks3/MockS3ServerChaos.cpp -->
# sources/storage-engines/foundationdb/fdbserver/mocks3/MockS3ServerChaos.cpp

## Purpose
Implements a chaos-injecting HTTP wrapper around `MockS3Server` for simulation tests that need S3 latency, throttling, server/auth errors, and response corruption.

## Important APIs, Types, And Functions
Private helpers include `registeredMockS3ChaosServers()`, `classifyS3Operation()`, `getOperationMultiplier()`, `generateS3ErrorXML()`, `maybeInjectDelay()`, `maybeInjectError()`, and `maybeCorruptResponse()`. `MockS3ChaosServerImpl::handleRequest()` is the core wrapper. Public functions include `clearMockS3ChaosRegistry()`, `MockS3ChaosRequestHandler::handleRequest()`, `clone()`, internal `registerMockS3ChaosServer()`, and `startMockS3ServerChaos()`.

## Control Flow
For each request the chaos server classifies the method/resource into read, write, delete, list, or multipart, optionally delays based on `S3FaultInjector`, optionally returns a throttling or weighted HTTP error XML response, delegates normal processing to `processMockS3Request()`, and optionally corrupts a successful response by replacing its ETag. Startup requires simulated network mode, deduplicates address registration in a static set, ensures mock S3 persistence is enabled/loaded, registers an HTTP handler with the simulator, and calls `initializeMockS3Persistence()`.

## State And Persistence Behavior
The chaos layer stores only a process-static set of registered chaos server addresses. Persistent object and multipart state is delegated to `MockS3Server.cpp`; chaos startup explicitly enables/loads it before and after registration to avoid request races.

## Dependencies And Integration Points
Depends on `MockS3ServerChaos.h`, `MockS3Server.h`, `ChaosMetrics`, simulator HTTP registration, Flow tracing, deterministic random, and `S3FaultInjector`. It integrates with S3 blob-store simulation workloads by replacing the normal mock S3 server endpoint with a chaos endpoint.

## Risks And Edge Cases
Operation classification is heuristic: PUT/POST with `"uploads"` in the resource are multipart, while other unrecognized verbs default to read. `maybeInjectError()` applies an error-rate gate and then another random check for general errors, so effective general error probability is lower than a naive reading of the configured rate. Corruption only changes ETag headers on successful responses and does not mutate payload bytes. Clearing the registry in production simulation can desynchronize it from simulator HTTP handler state.

## Test Signals
Signals include trace events `MockS3ChaosDelay`, `MockS3ChaosThrottle`, `MockS3ChaosError`, `MockS3ChaosCorruption`, and chaos metrics counters `s3Throttles`, `s3Errors`, `s3Corruptions`. S3 chaos workloads and retry/error-handling simulation tests are the main validation path.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/mocks3/MockS3ServerChaos.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/mocks3/include/fdbserver/mocks3/MockS3Server.h -->
# sources/storage-engines/foundationdb/fdbserver/mocks3/include/fdbserver/mocks3/MockS3Server.h

## Purpose
Declares the public interface for the deterministic mock S3 server used by FoundationDB simulation and ctest HTTP scenarios.

## Important APIs, Types, And Functions
`MockS3RequestHandler` implements `HTTP::IRequestHandler` with `handleRequest()`, `clone()`, reference counting, and an atomic destruction guard. Public functions start/register the server, clear global storage, enable/check/load/initialize persistence, and process a request directly: `startMockS3Server()`, `startMockS3ServerReal()`, `clearMockS3Storage()`, `registerMockS3Server()`, `enableMockS3Persistence()`, `isMockS3PersistenceEnabled()`, `loadMockS3PersistedStateFuture()`, `initializeMockS3Persistence()`, and `processMockS3Request()`.

## Control Flow
Normal HTTP use constructs/clones `MockS3RequestHandler` and calls `handleRequest()`, which delegates to the implementation. Simulation callers usually call `registerMockS3Server()` or `startMockS3Server()`. Real ctest callers use `startMockS3ServerReal()`. Chaos code calls `processMockS3Request()` after injecting faults.

## State And Persistence Behavior
The header exposes controls for global in-memory storage and optional disk persistence, but state is implemented in `MockS3Server.cpp`. The destruction guard avoids handling or cloning while a handler is being destroyed.

## Dependencies And Integration Points
Depends on Flow futures/network and `fdbrpc/HTTP`. It is consumed by mock S3 implementation, chaos wrapper, simulator setup, S3 client workloads, and tests.

## Risks And Edge Cases
The direct request processor is low-level and assumes callers pass initialized HTTP request/response objects with usable content queues. Persistence APIs are global, so callers must be aware that state can span simulated processes and tests. `clone()` can return an empty reference during destruction.

## Test Signals
Signals include `fdbserver_mocks3_test`, simulation workloads using `registerMockS3Server()`, and chaos wrapper integration through `processMockS3Request()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/mocks3/include/fdbserver/mocks3/MockS3Server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/mocks3/include/fdbserver/mocks3/MockS3ServerChaos.h -->
# sources/storage-engines/foundationdb/fdbserver/mocks3/include/fdbserver/mocks3/MockS3ServerChaos.h

## Purpose
Declares the chaos-enabled mock S3 server interface and documents its configuration philosophy for FoundationDB simulation testing.

## Important APIs, Types, And Functions
`S3Operation` categorizes requests as `READ`, `WRITE`, `DELETE`, `LIST`, or `MULTIPART`. `MockS3ChaosRequestHandler` implements `HTTP::IRequestHandler` with reference counting and an atomic destruction guard. Public functions are `startMockS3ServerChaos()` and `clearMockS3ChaosRegistry()`.

## Control Flow
Simulation tests configure `S3FaultInjector` rates/multipliers, start a chaos server at a `NetworkAddress`, and point S3 blob-store clients at that endpoint. The request handler delegates to `MockS3ServerChaos.cpp`, which injects faults before/after base mock S3 processing.

## State And Persistence Behavior
This header owns no state. The implementation keeps a chaos registration set, uses `S3FaultInjector` and `ChaosMetrics` globals, and delegates persistence to the base mock S3 server.

## Dependencies And Integration Points
Depends on Flow futures/network and `fdbrpc/HTTP`. The comments describe integration with `S3BlobStoreEndpoint`, S3 client workloads, chaos metrics, and test configs such as S3 client workload with chaos.

## Risks And Edge Cases
The header notes that registry clearing is for testing/debugging only because simulator HTTP handler state persists. Fault injection has no master boolean; misconfigured per-rate settings can unintentionally target all operations or none. The operation enum must stay aligned with classification logic in the implementation.

## Test Signals
Signals are S3 chaos workloads, retry/error-handling behavior, and chaos metrics/traces for injected S3 errors, throttles, delays, and corruptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/mocks3/include/fdbserver/mocks3/MockS3ServerChaos.h -->
