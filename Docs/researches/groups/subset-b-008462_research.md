# subset-b-008462 Research

Grouped research for FoundationDB `fdbserver/core` files. Each section preserves the source path and is bounded by the reconciliation markers required for source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/ServerCheckpoint.cpp -->
## sources/storage-engines/foundationdb/fdbserver/core/ServerCheckpoint.cpp

Purpose: central dispatch for server-side checkpoint lifecycle operations. It hides checkpoint format differences from callers that need readers, deletion, full fetch, range fetch, or deterministic local directory naming.

Important APIs: `newCheckpointReader`, `deleteCheckpoint`, `fetchCheckpoint`, `fetchCheckpointRanges`, `serverCheckpointDir`, and `fetchedCheckpointDir`. The only implemented formats are RocksDB-backed: `DataMoveRocksCF`, `RocksDB`, and the range-fetch `RocksDBKeyValues` wrapper. Unsupported formats throw `not_implemented`.

Control flow and state: reader creation delegates to `newRocksDBCheckpointReader`. Deletion yields at `TaskPriority::FetchKeys`, then recursively erases `checkpoint.dir` when present and logs a warning if the metadata lacks a directory. Full fetch asserts it is not already a `RocksDBKeyValues` checkpoint, then delegates to `fetchRocksDBCheckpoint` and traces begin/end by checkpoint UID. Range fetch validates non-empty ranges, converts `DataMoveRocksCF` metadata into `RocksDBKeyValues` metadata by setting `ranges`, `dir`, and serialized `RocksDBCheckpointKeyValues`, then fetches through the same RocksDB path.

Dependencies and integration: depends on `ServerCheckpoint.h`, `RocksDBCheckpointUtils.h`, Flow actors, `ObjectWriter`, deterministic random UIDs, and platform directory deletion. It is used by storage fetch/checkpoint transfer paths and data movement that fetch full or range-limited SST checkpoints.

Risks and tests: format dispatch is intentionally narrow; adding another checkpoint format requires all four operations. Range fetch mutates the input metadata copy before serialization, so metadata compatibility matters. Directory deletion is irreversible and should be tested with missing-dir, unsupported-format, RocksDB, and range-limited checkpoint transfer simulations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/ServerCheckpoint.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/ServerKnobs.cpp -->
## sources/storage-engines/foundationdb/fdbserver/core/ServerKnobs.cpp

Purpose: defines global server knob storage, parsing, mutation helpers, and the authoritative initialization table for `ServerKnobs`. This file is the runtime configuration surface for transaction logs, data distribution, storage engines, recovery, ratekeeper, worker health, backup, bulk load/dump, simulation fault injection, and many timing/resource limits.

Important APIs: `ServerKnobs::ServerKnobs`, `ServerKnobs::initialize`, `resetServerKnobs`, `initializeServerKnobs`, `tryParseServerKnobValue`, `parseServerKnobValue`, `trySetServerKnob`, `setServerKnob`, and `setupServerKnobs`. It also owns the global `SERVER_KNOBS` pointer plus bootstrap/global instances of Flow, client, and server knobs.

Control flow and state: process startup begins with bootstrap knobs, then `resetServerKnobs` points `FLOW_KNOBS`, `CLIENT_KNOBS`, and `SERVER_KNOBS` at global instances and reinitializes all three. `initializeServerKnobs` mutates already-selected global instances. Parsing searches Flow, client, then server knob registries. Setting attempts all three mutable knob objects and reports invalid name/value warnings through stderr and trace events. `ServerKnobs::initialize` uses `INIT_KNOB` for hundreds of values, with many derived from earlier knobs and with simulation/buggify branches that deliberately shrink timeouts, limits, shard sizes, or queue sizes.

State and persistence behavior: knobs are in-memory process-global configuration, but many values affect persistent protocols and on-disk interpretation. Examples include byte sampling constants that cannot change after database creation, DBCoreState serialization gates, RocksDB and sharded RocksDB layout/checkpoint behavior, transaction log recovery limits, and data distribution priorities.

Dependencies and integration: depends on `fdbserver/core/Knobs.h`, client knobs, Flow randomization, trace events, and simulation helpers. Nearly every server component reads `SERVER_KNOBS`; this file is therefore a cross-cutting integration point.

Risks and tests: ordering matters because later knobs depend on earlier values. Simulation-only randomization should not leak into production defaults. Changes can destabilize recovery, storage queue throttling, shard splitting/merging, RocksDB performance, or compatibility. Test signals include simulation suites with buggify, restart/downgrade tests for persistent knobs, storage metric split tests, data distribution tests, and targeted workload tests for any changed knob family.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/ServerKnobs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/ShardSizing.cpp -->
## sources/storage-engines/foundationdb/fdbserver/core/ShardSizing.cpp

Purpose: computes data distribution shard size bounds and feature gates for large teams. It converts database size estimates and key-range context into `ShardSizeBounds` consumed by data distribution and shard splitting/merging logic.

Important APIs: `ShardSizeBounds::shardSizeBoundsBeforeTrack`, `getShardSizeBounds`, `getMaxShardSize`, and `ddLargeTeamEnabled`.

Control flow and state: `shardSizeBoundsBeforeTrack` returns sentinel bounds where byte fields are `-1` and non-byte maxima/permitted errors are infinity, representing pre-tracking behavior. `getShardSizeBounds` gives system keyspace shards under `keyServersKeys` a separate `KEY_SERVER_SHARD_BYTES` maximum, otherwise uses the supplied maximum. The first shard beginning at `allKeys.begin` may shrink to zero bytes, while other shards use `maxShardSize / SHARD_BYTES_RATIO` as the minimum. `getMaxShardSize` scales from `MIN_SHARD_BYTES + sqrt(dbSizeEstimate) * SHARD_BYTES_PER_SQRT_BYTES`, multiplies by `SHARD_BYTES_RATIO`, caps at `MAX_SHARD_BYTES`, optionally raises to `MAX_LARGE_SHARD_BYTES`, and traces the result with suppression.

Dependencies and integration: depends on `SystemData` key ranges, `StorageMetrics`, and `SERVER_KNOBS`. Data distribution uses these bounds when deciding whether shards are too large, too small, or eligible for large-team handling.

Risks and tests: size math directly impacts movement volume and shard churn. Negative/sentinel byte fields are meaningful and should not be treated as real sizes. Large-team enablement is disabled when location metadata encoding is active, so tests should cover both metadata modes, system key ranges, zero database estimates, and large-shard knob combinations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/ShardSizing.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/SimulatorSupport.cpp -->
## sources/storage-engines/foundationdb/fdbserver/core/SimulatorSupport.cpp

Purpose: provides a tiny helper for checking whether the current simulated process is unreliable.

Important API: `isSimulatorProcessUnreliable`.

Control flow and state: the function returns true only when `g_network->isSimulated()` and the current simulator process reports `!isReliable()`. It reads simulator state and does not mutate anything.

Dependencies and integration: depends on `fdbrpc/simulator.h`, `SimulatorProcessInfo`, and Flow network globals. Callers can use it to gate behavior that should differ for unreliable simulated processes.

Risks and tests: it assumes `g_simulator->getCurrentProcess()` is valid whenever the network is simulated. Test signal is simulation-only coverage that calls this from reliable and unreliable process contexts; production should always return false because `isSimulated()` is false.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/SimulatorSupport.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/StorageMetrics.cpp -->
## sources/storage-engines/foundationdb/fdbserver/core/StorageMetrics.cpp

Purpose: implements storage-server metric sampling, range estimates, shard split calculations, read-hot range detection, wait-for-metric notifications, and transient metric expiry. It is a core input to data distribution, storage throttling, split/merge decisions, and read hot-spot tooling.

Important APIs/types: `CommonStorageCounters`, `isKeyValueInSample`, `StorageMetrics::readLoadKSecond`, `StorageMetricSample::getEstimate` and `splitEstimate`, `StorageServerMetrics` methods for `getMetrics`, `notify`, `notifyBytesReadPerKSecond`, `notifyBytes`, `notifyNotReadable`, `poll`, `getSplitKey`, `splitMetrics`, `getStorageMetrics`, read-hot range methods, split point methods, wait-map maintenance, and `TransientStorageMetricSample` methods. It also contains unit tests for sample estimates, range split points, and read-hot detection.

Control flow and state: byte sampling hashes the key and samples by size-adjusted probability. Metric samples are stored in indexed sets keyed by FDB keys, with sums used for range estimates and split lookup. `notify` and `notifyBytesReadPerKSecond` add transient sampled write/read/I/O data with expiration and immediately send deltas to watchers in `waitMetricsMap`. `poll` expires queued transient samples and notifies watchers with negative deltas. `splitMetrics` loops over a range until byte or write traffic bounds are satisfied, selecting candidate keys from byte, IOPS, and write samples while enforcing minimum split bytes and max rows. `waitMetrics` first checks whether current metrics are already outside requested min/max, otherwise registers a `PromiseStream` on intersecting ranges, races metric changes against timeout, sends final metrics or wrong-shard, then removes watchers and coalesces the map.

State and persistence behavior: all samples and waiters are in-memory storage-server state. Persistent behavior is indirect: byte sample contents are derived from stored data and affect shard boundaries and movement choices. Comments note `TransientStorageMetricSample::erase` variants are broken because future queued expirations remain.

Dependencies and integration: depends on `StorageMetrics.h`, `SERVER_KNOBS`, `CLIENT_KNOBS`, Flow hashing/random/unit-test utilities, `KeyRangeMap`, `IndexedSet`, request/reply structs, and trace/code probes. Data distribution, storage server disk code, wait metrics RPCs, and read-hot monitors consume this behavior.

Risks and tests: risks include divide-by-zero on untrusted split inputs, incorrect split keys near boundaries, watcher leaks, excessive `waitMetricsMap` fragmentation, sampling bias, and stale queued expirations after erase. Existing unit tests cover simple estimates, split point generation, unsplittable ranges, and read-hot detection including consecutive ranges and equal division; changes should also be exercised in simulation with storage metrics polling and data distribution.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/StorageMetrics.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/TSSMappingUtil.cpp -->
## sources/storage-engines/foundationdb/fdbserver/core/TSSMappingUtil.cpp

Purpose: reads the mapping from storage server IDs to testing storage server interfaces from system keyspace metadata.

Important APIs: `readTSSMappingRYW` for `ReadYourWritesTransaction` and `readTSSMapping` for regular `Transaction`.

Control flow and state: the RYW variant uses `KeyBackedMap<UID, UID>` at `tssMappingKeys.begin` to read all UID pairs, asserts the result is below `CLIENT_KNOBS->TOO_MANY`, fetches the mapped TSS server-list value, decodes it, and stores it in the output `std::map<UID, StorageServerInterface>` keyed by source storage server ID. The regular transaction variant reads the raw key range, unpacks source IDs from tuple-encoded keys and TSS IDs from tuple-encoded values, then decodes corresponding server-list values.

Dependencies and integration: depends on `SystemData`, `KeyBackedTypes`, tuple codecs, `serverListKeyFor`, and `decodeServerListValue`. It integrates with TSS recruitment, data distribution checks, and simulation/performance testing paths needing source-to-TSS interface mappings.

Risks and tests: both functions assume server-list values exist and call `v.get()`, so corrupted/incomplete mappings will throw/assert. Large mappings are bounded by `TOO_MANY`. Tests should cover empty mapping, multiple TSS mappings, missing server-list entries, and both transaction APIs producing identical maps.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/TSSMappingUtil.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/WaitFailure.cpp -->
## sources/storage-engines/foundationdb/fdbserver/core/WaitFailure.cpp

Purpose: implements the wait-failure RPC pattern used by server interfaces to detect endpoint failure through long-poll reply promises and the failure monitor.

Important APIs: `waitFailureServer`, `waitFailureClient`, `waitFailureClientStrict`, and `waitFailureTracker`.

Control flow and state: `waitFailureServer` stores incoming `ReplyPromise<Void>` objects in a deque. It does not reply unless the queue exceeds `MAX_OUTSTANDING_WAIT_FAILURE_REQUESTS`, at which point it releases the oldest promise. Cancellation breaks outstanding promises. `waitFailureClient` repeatedly sends a reply promise using `getReplyUnlessFailedFor`; absence of a reply indicates endpoint failure and optionally traces details. Successful replies are rate-limited by `WAIT_FAILURE_DELAY_LIMIT`. `waitFailureClientStrict` repeatedly detects failure and then waits for the endpoint to remain failed for `failureReactionTime` unless the failure monitor observes recovery. `waitFailureTracker` keeps an `AsyncVar<bool>` synchronized with the failure monitor and active wait-failure probes.

Dependencies and integration: depends on `fdbrpc` request streams, `IFailureMonitor`, Flow deque/delay, server knobs, task priorities, and trace events. It underpins liveness detection for worker, backup, data distributor, and other interfaces that expose `waitFailure`.

Risks and tests: queue overflow deliberately replies to old requests, so knob sizing affects detection latency and memory. Unknown errors assert. Tests should exercise failure, recovery before strict timeout, cancellation, queue overflow, trace context, and different task priorities.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/WaitFailure.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/WorkerEvents.cpp -->
## sources/storage-engines/foundationdb/fdbserver/core/WorkerEvents.cpp

Purpose: queries workers for their latest trace event fields, optionally filtered by event name, and returns both results and failed workers.

Important API: `latestEventOnWorkers`.

Control flow and state: for each `WorkerDetails`, the actor builds an `EventLogRequest`, sends it to the worker's `eventLogRequest` stream, wraps it with `timeoutError(..., 2.0)` and `errorOr`, then waits for all futures. It builds a `WorkerEvents` map keyed by worker address. Failed or timed-out requests add the address string to the failed set and store empty `TraceEventFields`; successful requests store returned fields. Only actor cancellation should escape because per-worker errors are captured.

Dependencies and integration: depends on `WorkerEvents.h`, worker interfaces, Flow futures, event log RPCs, trace field serialization, and address formatting. It is useful for status, diagnostics, and latest-role/event inspection across workers.

Risks and tests: the fixed two-second timeout can report slow workers as failed. Empty event names request default latest events. Tests should cover all-success, partial timeout/error, empty event names, named event lookup, and cancellation propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/WorkerEvents.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/WorkerInterface.cpp -->
## sources/storage-engines/foundationdb/fdbserver/core/WorkerInterface.cpp

Purpose: adapts a full cluster-controller interface stream into the client-facing `ClusterInterface` async variable needed by clients and dependent actors.

Important API: `extractClusterInterface`.

Control flow and state: the actor loops forever. If the input `AsyncVar<Optional<ClusterControllerFullInterface>>` is present, it writes the embedded `clientInterface` to the output `AsyncVar<Optional<ClusterInterface>>`; otherwise it clears the output. It then waits on `in->onChange()` and repeats.

Dependencies and integration: depends on `WorkerInterface.actor.h`, `AsyncVar`, `ClusterControllerFullInterface`, and `ClusterInterface`. It is a small glue actor used when worker or client code only needs the client subset of the cluster controller interface.

Risks and tests: output freshness depends on `onChange()` notifications and actor lifetime. Tests should verify transitions from absent to present, present to absent, replacement of a full interface, and cancellation without leaving dependent code with unexpected state.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/WorkerInterface.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/WorkerSupport.cpp -->
## sources/storage-engines/foundationdb/fdbserver/core/WorkerSupport.cpp

Purpose: provides worker-side helpers for broadcasting database information, classifying addresses by database region, tracing worker roles, and registering static role descriptors.

Important APIs/types: explicit `RequestStream`/`NetNotifiedQueue` instantiations for master/proxy/db-info requests; `broadcastDBInfoRequest`, `broadcastTxnRequest`, `addressInDbAndPrimarySatelliteDc`, `addressInDbAndRemoteDc`, `startRole`, `endRole`, `traceRole`, and static `Role` constants.

Control flow and state: broadcast helpers partition `broadcastInfo` endpoints over `sendAmount` streams, reset reply promises between sends, wait for all replies, and optionally reply to the original requester. DB-info broadcast returns endpoints that were not updated, including sender when provided and failed sub-broadcasts from `tryDBInfoBroadcast`. Address helpers scan current `ServerDBInfo` log sets, remote log routers, and optional storage server address lists. Role lifecycle helpers update trace roles, emit begin/end/refresh trace events, maintain process-global `g_roles`, update `StringMetricHandle` values, manipulate latest event cache, and notify the simulator role map.

Dependencies and integration: depends on simulator, `ServerDBInfo`, Flow trace/metrics/generic actors, network addresses, log system locality tags, and worker role definitions. It integrates with cluster controller recruitment, status role reporting, transaction state propagation, and simulation visualization.

Risks and tests: broadcast partitioning must preserve all endpoints and not reuse stale reply promises. Global `g_roles` is process-local mutable state and must stay balanced across start/end paths. Tests should cover partial broadcast failure, sender exclusion, remote/satellite address classification, role metrics updates, and simulated add/remove role calls.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/WorkerSupport.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/WorkloadKeys.cpp -->
## sources/storage-engines/foundationdb/fdbserver/core/WorkloadKeys.cpp

Purpose: encodes doubles into deterministic test keys and decodes them back for workload/test key generation.

Important APIs: `doubleToTestKey(double)`, `testKeyToDouble(const KeyRef&)`, and prefix overloads for both directions.

Control flow and state: encoding treats the double bits as a `uint64_t` and formats them as a 16-character hexadecimal string. Decoding scans the hex string into a `uint64_t` and reinterprets the bits as a double. Prefix overloads add or remove a supplied key prefix.

Dependencies and integration: depends on C stdio/inttypes formatting, `WorkloadKeys.h`, and Flow key types. It is intended for workloads that need reproducible numeric keys.

Risks and tests: the implementation uses type punning through casts, so portability depends on platform representation and aliasing assumptions already common in this codebase. Lexicographic order is bit-pattern order, not necessarily numeric order for all doubles. Tests should cover round trips, prefix handling, NaN/negative/zero values, and fixed expected encodings.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/WorkloadKeys.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/AccumulativeChecksumUtil.h -->
## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/AccumulativeChecksumUtil.h

Purpose: declares utilities for attaching and validating accumulative checksums on mutation streams, primarily between commit proxies and storage servers.

Important APIs/types: constants `invalidAccumulativeChecksumIndex`, `resolverAccumulativeChecksumIndex`, `initialAccumulativeChecksum`; inline helpers `getCommitProxyAccumulativeChecksumIndex`, `calculateAccumulativeChecksum`, `tagSupportAccumulativeChecksum`, `aggregateAcs`; class `AccumulativeChecksumBuilder`; overloads of `updateMutationWithAcsAndAddMutationToAcsBuilder`; and class `AccumulativeChecksumValidator`.

Control flow and state: checksum indexes reserve commit-proxy indexes ending in `1`, while the resolver has index `2`. Accumulation is XOR of mutation checksums. Supported tags currently require non-negative locality. The builder tracks current version and an ACS table per tag, updates tag state on tag assignment or mutation tagging, and exposes the table for read-only inspection. The validator buffers non-ACS mutations, consumes the buffer when an ACS mutation arrives, compares generated state to carried state, restores persisted ACS state, clears stale buffers, and exposes counters for metrics.

State and persistence behavior: builder/validator state is in-memory, but validator `processAccumulativeChecksum` returns an `AccumulativeChecksumState` intended to be persisted in storage server private data. Restore overwrites table state from persisted data.

Dependencies and integration: depends on client ACS types, commit transaction mutations, system tags, versions, epochs, and storage metrics counters. It integrates with commit proxy mutation generation and storage server pull/apply paths.

Risks and tests: every aggregated mutation must carry a checksum. Missing ACS mutations leave buffered data until `clearCache`, trading bounded memory for later mismatch detection. Tests should cover multiple tags, tag reassignment, persisted restore, missing ACS mutation, unsupported tags, counter clearing, and XOR compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/AccumulativeChecksumUtil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BackupInterface.h -->
## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BackupInterface.h

Purpose: defines the RPC interface identity for backup workers.

Important type: `BackupInterface` with file identifier `6762745`, `waitFailure` stream, `LocalityData`, endpoint helpers, equality, and serialization.

Control flow and state: the interface is a value object. `id()` and `getToken()` derive identity from the `waitFailure` endpoint token; `address()` returns the endpoint primary address. `initEndpoints()` is empty because endpoint construction is handled by stream serialization/initialization elsewhere.

Dependencies and integration: depends on FDB key/types, fdbrpc streams, locality metadata, and wait-failure infrastructure. Cluster controller and backup recruitment/status paths use it to identify and monitor backup workers.

Risks and tests: identity depends entirely on `waitFailure` endpoint token, so default-constructed or uninitialized interfaces should not be used as real workers. Serialization compatibility is important for recruitment messages. Tests should verify endpoint initialization, locality propagation, equality semantics, and wait-failure liveness behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BackupInterface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BackupPartitionMap.h -->
## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BackupPartitionMap.h

Purpose: declares backup partition data structures and helpers for dividing user keyspace into backup ranges.

Important APIs/types: `Partition`, `PartitionList`, `PartitionMap`, `serializePartitionListJSON`, and `calculateBackupPartitionKeyRanges`.

Control flow and state: `Partition` stores an integer partition ID and a `KeyRange` with serialization support. `PartitionMap` maps `Tag` to ordered `PartitionList`; a note requires ordered `std::map` behavior so multiple backup workers uploading the same content to blob storage avoid conflicts caused by nondeterministic ordering. `calculateBackupPartitionKeyRanges` uses shard tracked data to produce balanced contiguous key ranges.

Dependencies and integration: depends on FDB types, `KeyRangeMap`, and `ShardMetrics`. It integrates with backup workers and blob storage metadata production.

Risks and tests: deterministic ordering is a correctness requirement for concurrent uploads. Partitioning quality depends on shard byte-size estimates. Tests should cover JSON stability, tag ordering, empty/small/large shard maps, contiguous range coverage, and no overlap/gap invariants.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BackupPartitionMap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BackupProgress.h -->
## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BackupProgress.h

Purpose: tracks backup progress by log epoch and tag, and computes unfinished backup ranges for log-router or range backup workers.

Important APIs/types: `BackupProgress`, `addBackupStatus`, `getUnfinishedPartitionedBackup`, `getUnfinishedRangePartitionedBackup`, `setBackupStartedValue`, `getEpochStatus`, and actor `getBackupProgress`.

Control flow and state: construction captures database ID and ascending epoch metadata. `addBackupStatus` merges worker progress by keeping the maximum saved version per tag. Unfinished backup calculation returns maps keyed by `(epoch, endVersion, tagCount)` to tag start versions, using epoch tag enumeration and adjusted begin/end versions. Private helpers update tag versions and remove completed tags. The object stores progress, epoch tag counts, and the raw `backupStartedKey` value decoded from system keyspace.

State and persistence behavior: the class itself is in-memory and reference-counted, but it represents backup progress persisted in system keyspace. `getBackupProgress` populates it from the database and reports through trace severity.

Dependencies and integration: depends on FDB types, `BackupProgressTypes`, arenas, and FastRef reference counting. It integrates with backup agents/workers determining which mutation log ranges still need upload.

Risks and tests: iteration order is explicitly significant. Off-by-one version math determines whether `[savedVersion + 1, endVersion)` gaps are backed up. Tests should cover multiple epochs, partially complete tags, missing progress, range-backup locality, backup started value, and duplicate worker statuses.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BackupProgress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BackupProgressTypes.h -->
## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BackupProgressTypes.h

Purpose: defines the epoch metadata used by backup progress calculation.

Important type: `EpochTagsVersionsInfo`, containing tag count plus epoch begin/end versions.

Control flow and state: this is a simple value struct with an explicit constructor. It does not serialize itself here and carries no logic beyond grouping the three fields.

Dependencies and integration: depends on FDB `Version` types. `BackupProgress` consumes maps from `LogEpoch` to this struct to enumerate tags and compute unfinished backup intervals.

Risks and tests: correctness depends on callers supplying accurate tag counts and epoch boundaries. Tests should cover begin/end boundaries and changing tag counts across epochs through `BackupProgress`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BackupProgressTypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BulkDumpUtil.h -->
## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BulkDumpUtil.h

Purpose: declares utilities and data holders for bulk dump jobs, including storage-server dump task construction, local/remote file naming, manifest generation, upload, and bounded parallelism.

Important APIs/types: `RangeDumpRawData`, `SSBulkDumpTask`, `getSSBulkDumpTask`, `generateRandomBulkDumpDataFileName`, `getLocalRemoteFileSetSetting`, `persistCompleteBulkDumpRange`, `generateBulkDumpJobFolder`, `getBulkDumpJobTaskFolder`, `dumpDataFileToLocalDirectory`, `uploadBulkDumpJobManifestFile`, `uploadBulkDumpFileSet`, and `ParallelismLimitor`.

Control flow and state: `RangeDumpRawData` bundles dumped KVs, byte samples, last key, and byte count. `SSBulkDumpTask` carries target storage server, checksum server IDs, and `BulkDumpState`, with a diagnostic `toString`. File-setting helpers define deterministic local and remote manifest/data/sample paths under job/task folders. Dumping produces SST data, byte samples, and manifest metadata from a range. Upload helpers move job and task manifests/file sets through the configured transport. `ParallelismLimitor` uses an `AsyncVar<int>` counter to gate concurrent tasks and exposes `onChange`.

State and persistence behavior: bulk dump completion is persisted by writing metadata in Complete phase to bulk dump system keyspace. Local and remote files are persistent external artifacts.

Dependencies and integration: depends on bulk dumping/loading client types and storage server interfaces. Data distributor creates tasks; storage servers dump data; bulk load can later consume produced manifests.

Risks and tests: path generation must match bulk load expectations. Parallelism counters assert on over/underflow. Tests should cover empty ranges, sampled/non-sampled ranges, local/remote path symmetry, upload failure, complete-state persistence, and parallel limiter wakeups.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BulkDumpUtil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BulkLoadUtil.h -->
## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BulkLoadUtil.h

Purpose: declares file and metadata utilities used by bulk load to stage, copy, sample, download, and interpret dumped file sets.

Important APIs: `clearFileFolder`, `resetFileFolder`, `copyBulkFile`, `readBulkFileBytes`, `writeBulkFileBytes`, `getBulkLoadTaskStateFromDataMove`, `bulkLoadDownloadTaskFileSet`, `bulkLoadDownloadTaskFileSets`, `doBytesSamplingOnDataFile`, `downloadBulkLoadJobManifestFile`, `getBulkLoadJobFileManifestEntryFromJobManifestFile`, and `getBulkLoadManifestMetadataFromEntry`.

Control flow and state: folder helpers erase or recreate local staging directories. Async file helpers copy/read/write with maximum byte limits. Data-move metadata lookup waits for the relevant `BulkLoadTaskState` at or after a version. Download helpers move remote file sets into local roots. Sampling produces byte-sample files from data files. Manifest helpers download a job manifest, extract entries intersecting a key range, and fetch manifest metadata for those entries.

State and persistence behavior: operates on local files, remote bulk-load storage, and data-move metadata persisted in FDB. Some actors can remain pending if required metadata reads fail, per comment.

Dependencies and integration: depends on `fdbclient/BulkLoading.h`, database transactions, transports, manifests, file sets, and data movement IDs. It bridges DD bulk-load metadata and storage-server local ingest preparation.

Risks and tests: file byte limits protect memory and disk. Folder clearing must avoid deleting wrong paths. Manifest range extraction must avoid gaps/overlaps. Tests should cover transport errors, oversized files, missing manifest entries, sampling correctness, and data-move version waits.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BulkLoadUtil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ConflictBatch.h -->
## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ConflictBatch.h

Purpose: defines compact commit-result codes for conflict batch processing.

Important type: `ConflictBatchStatus::TransactionCommitResult` with `TransactionConflict`, `TransactionTooOld`, reserved `TransactionUnusedResultValue1`, `TransactionCommitted`, and `TransactionLockReject`.

Control flow and state: this header contains only enum constants stored as `uint8_t`. Values are part of an inter-component contract and should be treated as stable.

Dependencies and integration: depends only on `<cstdint>`. Commit proxy/resolver/client commit result paths can use the enum to encode conflict-batch outcomes.

Risks and tests: changing numeric order can break serialized or compact result interpretation. Tests should cover mapping from transaction outcome to enum value and any wire/storage encoding that relies on the `uint8_t` values.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ConflictBatch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/CoordinatedState.h -->
## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/CoordinatedState.h

Purpose: declares abstractions for reading, exclusively updating, and moving the cluster coordinated state stored through server coordinators.

Important APIs/types: `CoordinatedState` with `read`, `onConflict`, `setExclusive`, and `getConflict`; `MovableCoordinatedState` with the same read/conflict/set flow plus `move`.

Control flow and state: callers must call `read()` before the single allowed `setExclusive()`. `onConflict()` is also single-use after read and completes when a future exclusive update would fail. `setExclusive()` attempts compare-and-set semantics against the value returned by read, but comments warn that concurrent reads/sets can make conflict outcomes ambiguous. `MovableCoordinatedState::move` runs only after successful `setExclusive` and transfers coordinated state to new uninitialized coordinators until a leader from the new coordinators should continue work.

State and persistence behavior: implementations hidden behind `PImpl` persist through coordination backends. The API is a concurrency-sensitive wrapper over cluster state history.

Dependencies and integration: depends on FDB values, `PImpl`, `ServerCoordinators`, and cluster connection strings. Master recovery and coordinator migration use these abstractions.

Risks and tests: lifetime comments require all outstanding operations to be cancelled before destruction. Single-use method ordering and concurrent calls are easy to misuse. Tests should cover successful exclusive set, conflict, onConflict behavior, move after set, cancellation/destruction, and ambiguous concurrent interleavings.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/CoordinatedState.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/CoordinationInterface.h -->
## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/CoordinationInterface.h

Purpose: defines server-side coordination and leader-election RPC interfaces, request/reply payloads, and coordinator collections.

Important APIs/types: `GenerationRegInterface`, `UniqueGeneration`, `GenerationRegReadReply`, `GenerationRegReadRequest`, `GenerationRegWriteRequest`, `LeaderElectionRegInterface`, `CandidacyRequest`, `ElectionResultRequest`, `LeaderHeartbeatReply`, `LeaderHeartbeatRequest`, `ForwardRequest`, `ServerCoordinators`, and `updateCCSInMovableValue`.

Control flow and state: generation registry reads/writes carry a key and `UniqueGeneration`; comments define total ordering semantics for read/write pairs. `UniqueGeneration` compares first by generation then UID and serializes both. Leader election extends the client leader registration interface with candidacy, election result, heartbeat, and forward streams. Election and heartbeat requests carry leader info, known leader/change IDs, coordinator host/address lists, and reply promises. Forward requests carry a cluster connection string value for movable-state handoff.

State and persistence behavior: these are wire contracts for coordination state and leader election. File identifiers and serialization fields must remain compatible across processes and versions.

Dependencies and integration: depends on client coordination interfaces and well-known endpoints. `ServerCoordinators` wraps client coordinators with server leader-election and generation-reg interfaces. Coordinated state and cluster controller election paths consume these messages.

Risks and tests: comment notes a specification bug around returned read generation after no prior write/data loss. Serialization ordering, host/address compatibility, and forwarding of movable connection strings are sensitive. Tests should cover generation ordering, stale leader heartbeat, candidacy races, hostname and address coordinator forms, and `updateCCSInMovableValue`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/CoordinationInterface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/DBCoreState.h -->
## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/DBCoreState.h

Purpose: defines the persistent core database state stored in coordinated state, including current and old transaction log topologies, recovery count, protocol versions, pseudo-localities, and backup tag counts.

Important APIs/types: `CoreTLogSet`, `OldTLogCoreData`, and `DBCoreState`; methods `CoreTLogSet::operator==`, serializers, `OldTLogCoreData::operator==`, `DBCoreState::getPriorCommittedLogServers`, `isEqual`, and serialization.

Control flow and state: `CoreTLogSet` records log server UIDs, write anti-quorum, replication factor, localities, replication policy, locality role, start version, satellite tag locations, and TLog version. `OldTLogCoreData` records prior log sets and epoch ranges needed for recovery/backup. `DBCoreState` records current log sets, old logs, recovery count, log system type, protocol compatibility, and deprecated encryption field retained for downgrade safety. `getPriorCommittedLogServers` flattens all current and old log server IDs.

State and persistence behavior: comments explicitly mark this as persisted in `CoordinatedState` and version-sensitive. Serialization gates fields on protocol features such as backup worker, GC transaction generations, software version tracking, encryption-at-rest, and range backup worker. Equality optionally includes `recoverAt` depending on `RECORD_RECOVER_AT_IN_CSTATE`.

Dependencies and integration: depends on replication policy, log system config, master interface, server knobs, object serializer traits, and protocol version helpers. Master recovery reads/writes it to define durable transaction log topology.

Risks and tests: adding/removing/reordering fields can break coordinator-persisted state and downgrade paths. Deprecated encryption bytes must remain until a deliberate migration exists. Tests should cover serialization across protocol versions, equality with/without recoverAt knob, recovery with old log data, and downgrade compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/DBCoreState.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/DataDistributorInterface.h -->
## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/DataDistributorInterface.h

Purpose: declares the data distributor RPC interface and request/reply payloads for halting, snapshots, exclusion checks, metrics, range splitting, storage wiggler state, and audit triggers.

Important APIs/types: `DataDistributorInterface`, `PrepareBlobRestoreReply`, `PrepareBlobRestoreRequest`, `HaltDataDistributorRequest`, `GetDataDistributorMetricsReply/Request`, `DistributorSnapRequest`, `DistributorExclusionSafetyCheckReply/Request`, `DistributorSplitRangeRequest`, `StorageWigglerState`, and `GetStorageWigglerStateReply/Request`.

Control flow and state: the interface includes `waitFailure`, halt, snapshot, exclusion check, metrics, split range, storage wiggler, and audit request streams plus locality and `myId`. Request payloads carry reply promises and typed state: blob restore preparation returns success or conflict type; metrics requests carry key range, shard limit, and mid-only flag; snapshot requests carry payload, snapshot UID, and debug ID; split requests carry split points and expect `SplitShardReply`.

State and persistence behavior: the interface is serialized and passed through cluster controller/db-info state, but most state changes occur in the data distributor implementation. Snapshot and blob restore requests can lead to persistent metadata changes outside this header.

Dependencies and integration: depends on cluster interfaces, FDB types, locality, fdbrpc, storage server interfaces, DDMetrics, address exclusions, and audit request declarations. It is the main control surface for external actors talking to DD.

Risks and tests: `GetStorageWigglerStateReply` has timestamp members but serializes only `primary` and `remote`, so consumers must not expect timestamp propagation. File identifiers and field order are wire-compatible contracts. Tests should cover serialization, equality by ID, DD halt, exclusion safety, snapshot fanout, metrics shard limits, split requests, and wiggler state responses.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/DataDistributorInterface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/DataMovement.h -->
## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/DataMovement.h

Purpose: declares conversion helpers between data movement reasons and priority integers.

Important APIs: `dataMovementPriority(DataMovementReason)` and `priorityToDataMovementReason(int)`.

Control flow and state: this header only declares mappings; implementation elsewhere must keep the two functions inverse for supported priorities.

Dependencies and integration: depends on `fdbclient/SystemData.h` for `DataMovementReason`. Data distributor and movement metadata code use priorities to schedule and explain relocation work.

Risks and tests: mismatched reason/priority mappings can cause wrong scheduling, confusing traces, or bad repair priority. Tests should cover every enum value, unknown priorities, and round-trip conversion.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/DataMovement.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/FDBSimulationPolicy.h -->
## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/FDBSimulationPolicy.h

Purpose: declares global simulation policy state and helpers used by FoundationDB simulation tests to configure replication, extra databases, backup/DR agents, TSS fault modes, consistency scan corruption, targeted restarts/delays, and restart/quiescence flags.

Important APIs/types: enums `FDBExtraDatabaseMode`, `FDBBackupAgentType`, `FDBTSSMode`, `FDBSimConsistencyScanState`, `FDBSimConsistencyScanCorruptionType`; struct `FDBSimulationPolicyState`; and functions `installFDBSimulationPolicy`, `fdbSimulationPolicyState`, `stringToFDBExtraDatabaseMode`, `updateFDBSimulationPolicy`, and `setFDBSimulationPolicyRemoteTLogPolicy`.

Control flow and state: the state struct carries desired coordinators, storage/tLog/remote/satellite replication policies, anti-quorums, region IDs, allowed fault behavior, backup/DR agent modes, disabled region strings, tester/restart flags, extra database list, consistency scan state and injected corruption fields, per-worker corruption map, and TSS mode. `updateConsistencyScanState` enforces monotonic transitions from an expected current state to a higher desired state and clears corruption details after corruption is found.

State and persistence behavior: simulation policy is process-global in-memory test harness state, not database persistence, but it drives database configuration and fault injection that affect persisted test data.

Dependencies and integration: depends on `DatabaseConfiguration`, replication policies, network addresses, UIDs, and optional string refs. Simulation setup, test workloads, consistency scan, TSS, backup agents, and region configuration code consume it.

Risks and tests: enum ordering matters for TSS fault modes because modes at or above `EnabledAddDelay` are injection modes. Consistency state transitions are monotonic and expected-current guarded. Tests should cover string mode parsing, configuration updates across restarts, consistency corruption lifecycle, remote TLog policy injection, and TSS mode behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/FDBSimulationPolicy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/IDiskQueue.h -->
## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/IDiskQueue.h

Purpose: defines the abstract durable byte-queue interface used by log-like storage components and the version enum for disk queue page checksums.

Important APIs/types: `IDiskQueue::location`, virtual methods `initializeRecovery`, `readNext`, `getNextReadLocation`, `getNextPushLocation`, `read`, `push`, `pop`, `commit`, `getCommitOverhead`, `getStorageBytes`, trace/serialization helpers for `location`, `numeric_limits<IDiskQueue::location>`, and `DiskQueueVersion`.

Control flow and state: callers initialize recovery from a minimum location. If recovery is incomplete, they repeatedly call `readNext` until it returns less than requested bytes; after recovery, `readNext` must not be called again. `push` appends bytes and returns the end location; `pop` removes bytes before a location; `commit` makes prior pushes/pops durable, but crash before completion may persist any prefix of pushes/pops. `read(start,end,CheckHashes)` reads arbitrary ranges with optional hash checking.

State and persistence behavior: implementations persist a virtually infinite byte stream. `location` is effectively the sequence index with `hi` always zero and `lo` equal to the sequence, but serialization includes both fields for compatibility. `DiskQueueVersion` selects hashlittle, crc32, or xxhash3 page checksums.

Dependencies and integration: depends on FDB storage byte metrics, `IClosable`, Flow boolean params, serialization, traceability, and numeric limits. Transaction logs and spill/reference queues can implement or consume this abstraction.

Risks and tests: recovery protocol ordering is strict. Commit durability is prefix-based, so callers must tolerate partial persistence. Location comparison/limits must remain stable. Tests should cover recovery boundaries, read/push/pop ordering, crash during commit, hash versions, arbitrary reads, close behavior, and storage byte reporting.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/IDiskQueue.h -->
