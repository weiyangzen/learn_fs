# Research: subset-b-007491

Grouped research report for Hadoop HDFS DataNode fsdataset volume, stream, cache, block-pool, and async disk service classes. Each section is delimited for reconciliation into its source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/DataNodeVolumeMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/DataNodeVolumeMetrics.java

Purpose: maintains per-DataNode-volume IO metrics and publishes them through Hadoop Metrics2 as the `DataNodeVolume` source. It records metadata operation latency, data file IO latency, flush/sync/read/write/transfer/native-copy latency, and file IO error latency.

Important APIs/types/functions: `create(Configuration, String)` registers a metrics source in `DefaultMetricsSystem` with a sanitized volume name; `unRegister()` removes it. `getVolumeName()` exposes a tag by stripping `DataNodeVolume-` or `UndefinedDataNodeVolume` prefixes. `add*Latency` methods update `MutableRate` instances and optional `MutableQuantiles`; `addMetadataOperationLatency`, `addDataFileIoLatency`, and `addFileIoError` also increment counters. Getter methods expose last interval sample counts, mean, stddev, total counters, and selected quantile arrays.

Control flow: construction allocates one `MutableQuantiles` array per configured percentile interval. `create` reads `DFS_METRICS_PERCENTILES_INTERVALS_KEY`; if no intervals are configured, percentile arrays are zero length and update loops are no-ops. Each update path performs a counter/rate update and then appends the latency to every quantile bucket for that operation.

State and persistence: all state is in-memory Metrics2 mutable counters/rates/quantiles. There is no on-disk persistence. Metrics source naming must be unique; empty volume names receive an `UndefinedDataNodeVolume` random suffix.

Dependencies and integration points: depends on Metrics2 annotations, `MetricsRegistry`, `MutableRate`, `MutableCounterLong`, `MutableQuantiles`, `DFSConfigKeys`, and `ThreadLocalRandom`. It is exposed through `FsVolumeSpi.getMetrics()` and is updated by volume/file IO code through `FileIoProvider` and dataset operations.

Risks: `getVolumeName()` recompiles a regex on every call. Last-stat getters depend on Metrics2 snapshot behavior, so tests must trigger metric snapshots if asserting values. Duplicate sanitized names can collide if two non-empty volume names differ only by colon replacement. Quantile overhead grows with configured interval count.

Test signals: verify source registration/unregistration, empty-name uniqueness, counter/rate increments after `add*Latency`, no failure when percentile intervals are empty, and expected quantile additions when intervals are configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/DataNodeVolumeMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/FsDatasetSpi.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/FsDatasetSpi.java

Purpose: defines the main service-provider interface for DataNode replica storage. The default implementation is local-disk `FsDatasetImpl`, but the SPI also allows simulated or custom storage backends.

Important APIs/types/functions: nested `Factory` loads `DFS_DATANODE_FSDATASET_FACTORY_KEY` with `ReflectionUtils` and creates datasets. `FsVolumeReferences` is a closeable snapshot of referenced volumes. Core methods cover volume lifecycle (`addVolume`, `removeVolumes`, `getStorageReports`), replica lookup (`getReplica`, `getStoredBlock`, `getLength`, `getBlockInputStream`), write lifecycle (`createTemporary`, `createRbw`, `append`, `recoverAppend`, `recoverRbw`, `recoverClose`, `finalizeBlock`, `unfinalizeBlock`), block reports, cache operations, invalidation, block-pool lifecycle, trash/rolling-upgrade markers, lazy persist callbacks, pinning, block moves, and dataset locking.

Control flow: callers obtain references with `getFsVolumeReferences()` when iterating volumes, use read/write/recovery methods during the DataNode data-transfer pipeline, and use report/cache/invalidation methods from NameNode command handling. `FsVolumeReferences` skips closed volumes, exposes read-only iteration, and releases all references on `close()`.

State and persistence: this file is contractual, not a state holder. Its methods describe persistence responsibilities for implementations: block files, metadata files, block-pool directories, cache state, trash, rolling upgrade markers, and volume maps. `acquireDatasetLockManager()` documents coordination around in-memory replica maps.

Dependencies and integration points: integrates DataNode, DataStorage, `ExtendedBlock`, `ReplicaInfo`, `ReplicaHandler`, `StorageReport`, NameNode protocol types, block scanner scan info, `MountVolumeMap`, `FsVolumeImpl`, and `FSDatasetMBean`. It is the central boundary between DataNode services and physical storage.

Risks: broad SPI changes have large blast radius. Many methods assume correct locking by callers or implementations. Deprecated `getReplica` still exposes mutable replica metadata. Reference leaks from `FsVolumeReferences` can prevent volume removal. Recovery methods must maintain exact generation stamp and length semantics.

Test signals: implementation conformance tests should cover volume add/remove, block write/finalize/recover, invalidation, cache reporting, trash behavior, rolling-upgrade markers, locking during scans, and failure paths for missing replicas or failed volumes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/FsDatasetSpi.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/FsVolumeReference.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/FsVolumeReference.java

Purpose: small closeable reference handle for an `FsVolumeSpi`. Obtaining a reference increments the volume reference count and closing it decrements the count, allowing safe IO while volume removal is coordinated.

Important APIs/types/functions: `close()` releases the reference and is documented as not practically throwing despite the `IOException` signature inherited from `Closeable`. `getVolume()` returns the referenced `FsVolumeSpi`, or `null` after release.

Control flow: callers use try-with-resources around volume operations such as replica creation, deletion, scans, and stream wrappers. `FsDatasetSpi.FsVolumeReferences` aggregates multiple handles and closes all of them when the snapshot is no longer needed.

State and persistence: the interface has no state itself. Implementations maintain reference counts and closed/released state in memory; there is no direct persistence.

Dependencies and integration points: used by `FsVolumeSpi.obtainReference()`, `ReplicaInputStreams`, `FsDatasetAsyncDiskService` deletion tasks, and dataset volume iteration. It is part of the volume-removal safety protocol.

Risks: forgetting to close a reference can keep a failed or removed volume alive. Continuing to use `getVolume()` after close can produce null behavior depending on implementation. Implementations must be idempotent enough for cleanup utilities that may call close during exception handling.

Test signals: verify try-with-resources decrements counts, `getVolume()` after close follows implementation contract, volume removal waits for outstanding references, and exception cleanup paths close references exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/FsVolumeReference.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/FsVolumeSpi.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/FsVolumeSpi.java

Purpose: defines the storage-volume contract beneath `FsDatasetSpi`. It exposes capacity/location/type, block-pool iteration, directory scan data, space reservation, IO provider, metrics, and health checking.

Important APIs/types/functions: core methods include `obtainReference`, `getStorageID`, `getBlockPoolList`, `getAvailable`, `getBaseURI`, `getStorageLocation`, `getStorageType`, `isTransientStorage`, `reserveSpaceForReplica`, `releaseReservedSpace`, `releaseLockedMemory`, `newBlockIterator`, `loadBlockIterator`, `compileReport`, `loadLastPartialChunkChecksum`, `getFileIoProvider`, and `getMetrics`. Nested `BlockIterator` supports persistent iteration state for scanners. Nested `ScanInfo` compactly represents block/meta files or provided-storage `FileRegion`s.

Control flow: DataNode services obtain a reference before IO, reserve space for writes, scan volumes through `compileReport` and `ScanInfo`, and use `BlockIterator` for incremental block scanning. `ScanInfo` reconstructs full block/meta paths from compact suffixes and compares/equates by block ID.

State and persistence: implementations persist block files, metadata files, iterator checkpoints, and volume health information. `ScanInfo` caches block length at construction time, so later disk changes are not reflected. Block iterators may save their position to the volume.

Dependencies and integration points: connects to `DF`, `StorageLocation`, `StorageType`, `ExtendedBlock`, `FileRegion`, `ReportCompiler`, `FileIoProvider`, `VolumeCheckResult`, `DataNodeVolumeMetrics`, and checksum utilities.

Risks: `ScanInfo` assumes path prefix relationships and throws runtime exceptions if violated. Cached scan lengths can be stale. Iterator staleness is explicit; consumers must handle deleted or changed blocks. Space reservation and locked-memory release must respect OS page rounding in implementations.

Test signals: scan info path reconstruction, generation stamp extraction, provided-storage scan info, block iterator save/load/rewind/staleness behavior, health checks, storage-type predicates, and reservation release accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/FsVolumeSpi.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/LengthInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/LengthInputStream.java

Purpose: wraps an `InputStream` with a known length, used when returning metadata streams whose byte length must accompany the stream.

Important APIs/types/functions: constructor stores the wrapped stream and length. `getLength()` returns the supplied length. `getWrappedStream()` exposes the underlying stream reference from `FilterInputStream`.

Control flow: callers receive this from dataset metadata APIs, read through the wrapper as a normal `FilterInputStream`, and use `getLength()` for framing or protocol responses.

State and persistence: stores only an in-memory `long length` and the inherited wrapped stream field. It does not validate that bytes read match the advertised length and does not persist anything.

Dependencies and integration points: used by `FsDatasetSpi.getMetaDataInputStream(ExtendedBlock)` and DataNode block-transfer code that sends block metadata to clients or peers.

Risks: length correctness depends entirely on the creator. Exposing `getWrappedStream()` allows callers to bypass wrapper identity, though behavior is still the same stream. No special close behavior beyond `FilterInputStream`.

Test signals: verify length is preserved, wrapper delegates read/close behavior, and metadata APIs populate length from actual meta file size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/LengthInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/ReplicaInputStreams.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/ReplicaInputStreams.java

Purpose: bundles data and checksum input streams for a replica, plus the volume reference that keeps the underlying volume valid during reads.

Important APIs/types/functions: constructor stores `dataIn`, `checksumIn`, `FsVolumeReference`, and `FileIoProvider`, and captures a `FileDescriptor` when the data stream is a `FileInputStream`. Accessors expose streams, descriptor, and volume reference. `readDataFully`, `readChecksumFully`, `skipDataFully`, and `skipChecksumFully` delegate to `IOUtils`. `dropCacheBehindReads` calls `FileIoProvider.posixFadvise`. `closeStreams()` closes streams and reference while preserving one thrown `IOException`; `close()` performs quiet cleanup.

Control flow: block read and recovery code consume both streams in lockstep for checksum verification. Optional cache-dropping uses the file descriptor after reads. Closing releases stream resources and the volume reference.

State and persistence: in-memory wrapper only. It does not persist data but directly controls open file descriptors and volume reference lifetime.

Dependencies and integration points: integrates with `DataNode.LOG`, `FileIoProvider`, `FsVolumeReference`, `NativeIOException`, and `IOUtils`. Used by block validation and data-transfer paths.

Risks: `dropCacheBehindReads` asserts `dataInFd` is non-null, so non-file streams or disabled assertions can produce different failure modes. `closeChecksumStream()` nulls only checksum input, while callers must still close data/reference. `close()` swallows IOExceptions by design.

Test signals: close ordering and reference cleanup, descriptor capture for `FileInputStream`, no descriptor for non-file streams, full read/skip behavior, and `posixFadvise` invocation with the referenced volume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/ReplicaInputStreams.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/ReplicaOutputStreams.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/ReplicaOutputStreams.java

Purpose: bundles data and checksum output streams for a replica together with the checksum algorithm, target volume, and IO provider.

Important APIs/types/functions: constructor captures streams, `DataChecksum`, `FsVolumeSpi`, `FileIoProvider`, and a data `FileDescriptor` when backed by `FileOutputStream`. Accessors expose descriptor, streams, and checksum. `isTransientStorage()` delegates to the volume. `syncDataOut`, `syncChecksumOut`, `flushDataOut`, and `flushChecksumOut` route through `FileIoProvider`. `writeDataToDisk` writes data bytes. `syncFileRangeIfPossible` and `dropCacheBehindWrites` expose native IO hints. `closeDataStream` closes only the data stream; `close` closes data and checksum streams.

Control flow: DataNode write pipelines use this wrapper while receiving packets, writing checksum and block data, flushing/syncing, and issuing background `sync_file_range` or cache-drop hints.

State and persistence: the wrapper does not persist metadata itself but controls durable write behavior through sync and flush calls. `dataOut` can become null after `closeDataStream`; checksum stream is final.

Dependencies and integration points: connects `DataChecksum`, `FileIoProvider`, `FsVolumeSpi`, native IO calls, and async disk sync requests.

Risks: native methods may receive a null descriptor if stream is not file-backed. `syncDataOut` is a no-op for non-`FileOutputStream` streams. `close()` swallows close exceptions via `IOUtils.closeStream`. After `closeDataStream`, callers must avoid data writes/flushes.

Test signals: descriptor capture, transient-storage delegation, flush/sync provider calls, native range and fadvise calls, and behavior after closing only the data stream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/ReplicaOutputStreams.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/RoundRobinVolumeChoosingPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/RoundRobinVolumeChoosingPolicy.java

Purpose: implements `VolumeChoosingPolicy` by selecting volumes in round-robin order among volumes of the same storage type, while ensuring enough available space exists.

Important APIs/types/functions: `setConf` reads `DFS_DATANODE_ROUND_ROBIN_VOLUME_CHOOSING_POLICY_ADDITIONAL_AVAILABLE_SPACE_KEY`; `chooseVolume(List<V>, long, String)` validates non-empty volume list, picks a storage-type-specific lock/cursor, and calls the private chooser. The private `chooseVolume` scans volumes once from the current cursor and returns the first with `available > blockSize + additionalAvailableSpace`.

Control flow: one cursor and lock are maintained per `StorageType.ordinal()`. On success, the cursor advances to the next volume. On failure, it logs each insufficient volume and throws `DiskOutOfSpaceException` with the largest available space observed.

State and persistence: `curVolumes` and `syncLocks` are in-memory arrays sized to `StorageType.values().length`. There is no persistence. The configured additional-space threshold is stored as a long.

Dependencies and integration points: used by dataset volume selection for new replicas. Depends on Hadoop `Configurable`, `StorageType`, `DFSConfigKeys`, and `DiskChecker.DiskOutOfSpaceException`.

Risks: the `storageId` hint is ignored. Volumes must all share a storage type as assumed by the comment. The strict `>` comparison rejects exactly equal available space. StorageType enum changes affect array indexing. Caller must synchronize mutations to the volume list.

Test signals: empty list exception, cursor advancement, per-storage-type independent cursors, additional-space threshold behavior, wraparound, and failure message with max available space.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/RoundRobinVolumeChoosingPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/VolumeChoosingPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/VolumeChoosingPolicy.java

Purpose: generic policy interface for selecting a volume on which to place a replica.

Important APIs/types/functions: single method `chooseVolume(List<V> volumes, long replicaSize, String storageId)` returns a chosen `FsVolumeSpi` subtype or throws `IOException` when storage is unavailable or full. The `storageId` parameter carries a NameNode-nominated storage ID that policies may use or ignore.

Control flow: dataset write paths pass candidate volumes and expected replica size to an implementation. The interface explicitly states that callers should synchronize access to the volume list.

State and persistence: no state or persistence in the interface. Implementations may maintain in-memory selection cursors, available-space thresholds, or storage-id mappings.

Dependencies and integration points: implemented by `RoundRobinVolumeChoosingPolicy` and potentially other storage policies. Used by `FsVolumeList`/dataset allocation code when creating temporary or RBW replicas.

Risks: implementations must handle empty, stale, or concurrently modified volume lists. Misinterpreting `replicaSize` can overcommit space. Ignoring `storageId` may conflict with NameNode placement nominations in specialized deployments.

Test signals: implementation contract tests should cover empty candidate lists, full volumes, storage ID hints, concurrency around shared candidate lists, and propagation of IO exceptions from volume availability checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/VolumeChoosingPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/AddBlockPoolException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/AddBlockPoolException.java

Purpose: runtime exception used to aggregate IO failures encountered while adding or scanning block pools across multiple volumes.

Important APIs/types/functions: constructors accept an existing `Map<FsVolumeSpi, IOException>` or create a new `ConcurrentHashMap`. `mergeException` merges another aggregate while preserving the first exception per volume. `hasExceptions` reports whether failures exist. `getFailingVolumes` exposes the volume-to-exception map. `toString` includes the map.

Control flow: block-pool initialization code can collect failures per volume and throw or merge them after parallel work. When merging, later errors for the same volume are discarded because the first is likely causal.

State and persistence: in-memory map only. No suppressed exceptions are attached to the Java throwable; details live in the map.

Dependencies and integration points: depends on `FsVolumeSpi` and `IOException`. Integrated with `FsDatasetImpl`/volume startup paths that need to distinguish unhealthy data directories.

Risks: extends `RuntimeException`, so callers may miss it if expecting checked IO failures. The exposed map is mutable. `toString` quality depends on volume and exception string forms. Merging over key sets assumes stable `FsVolumeSpi` identity/equality.

Test signals: empty aggregate, constructor with prefilled map, merge preserves original per-volume exception, duplicate-volume merge behavior, and caller handling of `hasExceptions`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/AddBlockPoolException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/BlockPoolSlice.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/BlockPoolSlice.java

Purpose: represents one block pool's storage slice on one `FsVolumeImpl`. It owns the on-disk block-pool directory layout, startup replica discovery, lazy-persist recovery, cached `dfsUsed`, replica cache persistence, duplicate-replica resolution, and block count tracking.

Important APIs/types/functions: constructor creates `current/finalized`, `current/rbw`, `tmp`, optional replica-cache directory, initializes `FSCachingGetSpaceUsed`, and registers a shutdown hook. Directory/file APIs include `createTmpFile`, `createRbwFile`, `addFinalizedBlock`, `activateSavedReplica`, `checkDirs`, and accessors. Startup APIs include `getVolumeMap`, `addToReplicasMap`, `recoverTempUnlinkedBlock`, `moveLazyPersistReplicasToFinalized`, and `validateIntegrityAndSetLength`. Cache APIs include `loadDfsUsed`, `saveDfsUsed`, `readReplicasFromCache`, and `saveReplicas`. Duplicate handling is in `resolveDuplicateReplicas`, `selectReplicaToDelete`, and `deleteReplica`. `AddReplicaProcessor` parallelizes recursive scans.

Control flow: on construction, stale `tmp` is deleted and RBW/tmp dirs are recreated. `getVolumeMap` first recovers lazy-persist files into finalized storage, tries a non-stale serialized replica cache, then falls back to parallel recursive scans of finalized and RBW directories. Scanned block files are paired with metadata generation stamps, converted to `ReplicaInfo`, inserted into `ReplicaMap`, and reconciled against duplicates. RBW startup may use restart marker files to reload as RBW; otherwise replicas become RWR. Integrity validation checks only the last checksum chunk and truncates extra invalid bytes.

State and persistence: persistent state includes block data/meta files, finalized/RBW/tmp/lazypersist directories, `dfsUsed` cache file, `replicas` cache file, restart marker files, and lazy-persist saved files. In-memory state includes `numOfBlocks`, `dfsUsage`, config, timer, and the static fork-join pool.

Dependencies and integration points: tightly integrated with `FsVolumeImpl`, `FsDatasetImpl`, `ReplicaMap`, `ReplicaBuilder`, `RamDiskReplicaTracker`, `DataStorage`, `DatanodeUtil`, `FsDatasetUtil`, `BlockListAsLongs`, `FileIoProvider`, checksum classes, `ShutdownHookManager`, and disk checking.

Risks: startup correctness depends on cache freshness and fallback scanning. Static fork-join pool lifecycle spans slices and can leak if shutdown paths are wrong. Duplicate deletion is destructive and policy-sensitive. `validateIntegrityAndSetLength` assumes only the last chunk may be corrupt. Some failure paths log and continue, potentially leaving files for future scans. The restart meta path uses `File.pathSeparator` in the string, which is unusual for file paths and merits regression coverage.

Test signals: cached vs full startup scan, stale replica cache deletion, lazy-persist recovery, tmp unlink recovery, duplicate selection policy, disabled duplicate deletion, RBW/RWR restart marker behavior, checksum truncation, `dfsUsed` cache age handling, shutdown cache writes, fork-join scan exception aggregation, and block count updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/BlockPoolSlice.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/CacheStats.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/CacheStats.java

Purpose: tracks approximate memory-cache usage and capacity for DataNode block caching, using OS page-size rounding.

Important APIs/types/functions: `PageRounder` obtains OS page size from `NativeIO.POSIX.getCacheManipulator()` and provides `roundUp`/`roundDown`. Inner `UsedBytesCount` stores an `AtomicLong` and implements CAS-based `reserve`, `release`, `releaseRoundDown`, and `get`. Public/package methods expose `getCacheUsed`, `getCacheCapacity`, `reserve`, `release`, `releaseRoundDown`, `getPageSize`, and `roundUpPageSize`.

Control flow: cache loaders call `reserve` before mapping/locking a block. The count is rounded up and rejected with `-1` if it would exceed capacity. Failed or completed cache operations call release methods. `releaseRoundDown` is used for locked-memory accounting where OS page multiples matter.

State and persistence: all state is in-memory. `usedBytes` intentionally overestimates by counting pending cache operations and not pending uncaches; this conservative view helps avoid NameNode over-assignment.

Dependencies and integration points: used by `FsDatasetCache` and cache loader implementations. Depends on `NativeIO` for page size and `AtomicLong` for concurrency.

Risks: release methods can drive the counter negative if call pairs are wrong. Rounding assumes page size is a power of two because it uses bit masking. Capacity is fixed after construction. The estimate is approximate by design and may differ from actual locked memory.

Test signals: reserve success/failure at capacity, page rounding, CAS behavior under concurrency, release and releaseRoundDown accounting, and negative-count detection in higher-level tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/CacheStats.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetAsyncDiskService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetAsyncDiskService.java

Purpose: manages per-volume thread pools for slow disk work such as replica deletion and `sync_file_range`, keeping heartbeat and dataset control paths from blocking on disk IO.

Important APIs/types/functions: constructor reads max threads per volume. `addVolume` and `removeVolume` manage one `ThreadPoolExecutor` per storage ID. `execute` routes tasks to the correct volume executor. `countPendingDeletions` sums outstanding executor tasks. `shutdown` shuts down all executors and nulls the map. `submitSyncFileRangeRequest` queues native range sync. `deleteAsync` and `deleteSync` run `ReplicaFileDeleteTask`. `updateDeletedBlockId` batches deleted block IDs and periodically calls `fsdatasetImpl.removeDeletedBlocks`.

Control flow: deletion tasks hold an `FsVolumeReference`, call `fsdatasetImpl.removeReplicaFromMem`, delete or move block/meta files to trash, notify the NameNode unless `NO_ACK`, update volume deletion accounting, record the deleted block ID, and always release the volume reference.

State and persistence: in-memory executor map, deleted-block ID map, and deletion batch count. Persistent effects are deletion or trash moves of block/meta files and volume usage updates.

Dependencies and integration points: ties together `DataNode`, `FsDatasetImpl`, `FsVolumeImpl`, `ReplicaInfo`, `ReplicaOutputStreams`, `BlockCommand`, `DataNodeFaultInjector`, `FileIoProvider`, native IO, and NameNode deletion notifications.

Risks: `countPendingDeletions` includes sync tasks despite its name. If `execute` fails, only delete tasks get explicit reference cleanup. Executors are keyed by storage ID, so duplicate/missing IDs are fatal. Batched deleted block cleanup occurs only every 64 deletions. Trash moves must handle partial rename failures.

Test signals: add/remove volume validation, task routing, shutdown rejection, async and sync deletion success, trash move path, reference cleanup on executor failure, NameNode notification suppression for `NO_ACK`, pending count, and deleted-block batch flushing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetAsyncDiskService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetCache.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetCache.java

Purpose: manages DataNode block caching by mapping and locking blocks into DRAM or persistent memory, verifying checksums before advertisement, and handling uncache requests safely around short-circuit readers.

Important APIs/types/functions: `Value` pairs `MappableBlock` with `State`; states are `CACHING`, `CACHING_CANCELLED`, `CACHED`, and `UNCACHING`, with only `CACHED` advertised. Constructor creates uncache executors, validates revocation polling config, creates a `MappableBlockLoader`, and initializes `CacheStats`. `initCache` creates persistent-memory block-pool dirs and optionally recovers cached blocks. `cacheBlock` inserts `CACHING` and schedules `CachingTask`; `uncacheBlock` transitions to cancelled or uncaching and schedules immediate/deferred `UncachingTask`. Metrics and query methods expose cache usage, capacity, failure counts, cached block IDs, PMEM paths/addresses, and `isCached`.

Control flow: caching reserves cache bytes, opens block and metadata streams from the dataset, asks the loader to checksum/map/lock, then atomically publishes `CACHED` unless cancelled. Failure closes streams, releases reservation, closes any mapped block, increments failure metrics, and removes the map entry. Uncaching may defer while DRAM short-circuit clients keep anchors; after timeout it forcibly uncaches, closes the mappable block, removes map state, releases bytes, and increments metrics.

State and persistence: `mappableBlockMap` and counters are synchronized/in-memory. DRAM cache is transient. Persistent-memory mode can recover cache state across restart and stores cache files under PMEM-managed paths.

Dependencies and integration points: depends on `FsDatasetImpl`, `DNConf`, `MappableBlockLoaderFactory`, `PmemVolumeManager`, `DatanodeUtil`, `ExtendedBlockId`, short-circuit registry, DataNode metrics, `CacheStats`, and checksum exceptions.

Risks: state transitions must remain synchronized; async tasks use map state as authority. Reservation release must match loader behavior. Deferred uncache can hold memory while clients retain anchors, then forcibly revoke after timeout. Persistent cache recovery must align with real block validity. `getCacheAddress` reads map state without explicit synchronization after `isCached`.

Test signals: duplicate cache request failure, successful cache advertisement only after checksum/load, cancellation during caching, cache reservation failure, file-not-found and checksum failures, immediate and deferred uncache, revocation timeout, PMEM recovery/path/address, metrics increments, and shutdown loader cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetFactory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetFactory.java

Purpose: concrete factory that wires the `FsDatasetSpi.Factory` extension point to the default local-disk `FsDatasetImpl`.

Important APIs/types/functions: `newInstance(DataNode datanode, DataStorage storage, Configuration conf)` constructs and returns `new FsDatasetImpl(datanode, storage, conf)`.

Control flow: `FsDatasetSpi.Factory.getFactory(conf)` selects this class by default unless configuration overrides `DFS_DATANODE_FSDATASET_FACTORY_KEY`. DataNode startup calls `newInstance` to build its dataset.

State and persistence: this factory has no state. Persistence is delegated entirely to the constructed `FsDatasetImpl`.

Dependencies and integration points: depends on `Configuration`, `DataNode`, `DataStorage`, `FsDatasetSpi.Factory`, and `FsDatasetImpl`. It is the default bridge between configuration and local dataset implementation.

Risks: constructor exceptions propagate as `IOException` and can fail DataNode startup. Any custom factory must remain compatible with the same SPI expectations. This class does not override `isSimulated`, so it reports non-simulated through the base implementation.

Test signals: default factory selection, successful `FsDatasetImpl` construction with test DataNode/storage, override behavior through configuration, and startup failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetFactory.java -->
