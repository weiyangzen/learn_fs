# Research: subset-b-007492

Grouped research for Hadoop HDFS DataNode FsDataset implementation files. Each section preserves the source path and is bounded for deterministic per-file reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetImpl.java

## Purpose
`FsDatasetImpl` is the central local-storage implementation behind the DataNode `FsDatasetSpi`. It coordinates all physical HDFS replica state on a DataNode: volume activation/removal, in-memory replica maps, block creation and recovery, block reports, directory-scanner reconciliation, cache management, RAM-disk lazy persistence, async deletion, storage reports, and management metrics.

## Important APIs and Types
- Implements `FsDatasetSpi<FsVolumeImpl>` and `FSDatasetMBean` behavior through methods such as `getStorageReports`, `getBlockReports`, `createRbw`, `createTemporary`, `append`, `recoverAppend`, `recoverClose`, `recoverRbw`, `finalizeBlock`, `invalidate`, `checkAndUpdate`, `addBlockPool`, `shutdownBlockPool`, `deleteBlockPool`, and cache operations.
- Owns `FsVolumeList volumes`, `ReplicaMap volumeMap`, `storageMap`, `FsDatasetAsyncDiskService`, `FsDatasetCache`, `RamDiskReplicaTracker`, and `RamDiskAsyncLazyPersistService`.
- Uses `DataSetLockManager` with `LockLevel.BLOCK_POOl`, `LockLevel.VOLUME`, and `LockLevel.DIR`, plus `DataNodeLayoutSubLockStrategy` to split per-block directory locks.
- Inner `LazyWriter` persists RAM-disk replicas to durable volumes and evicts lazy-persist replicas when cache memory is needed.
- Static helpers `moveBlockFiles`, `copyBlockFiles`, `hardLinkBlockFiles`, `computeChecksum`, `initReplicaRecoveryImpl`, and `checkReplicaFiles` are shared by volume and recovery paths.

## Control Flow
Construction validates tolerated failed volumes, builds `FsVolumeList`, creates services, adds every `DataStorage` directory as a volume, loads replica maps, starts lazy-persist support when needed, registers MBeans and metrics, and initializes directory-scanner notification limits.

Adding a startup volume builds an `FsVolumeImpl`, obtains a reference, scans it into a temporary `ReplicaMap`, then `activateVolume` merges the replicas, installs storage IDs, adds async services, registers scanner volume references, and adds dataset locks. Dynamic `addVolume` first prepares storage with `DataStorage.VolumeBuilder`, initializes block-pool slices for each namespace, scans replicas, starts lazy-persist support, commits the storage builder, and activates the volume. `removeVolumes` disables async services, removes the volume from `FsVolumeList`, waits for references to drain, removes all replicas from memory, invalidates them outside the object lock, then removes storage and lock entries.

Replica writes are state-machine driven. `createTemporary` chooses a target volume, handles existing in-pipeline or provided replicas, deletes conflicting old blocks, creates a temp file, and inserts a `TEMPORARY` replica. `createRbw` may reserve locked memory and choose transient storage for lazy persist, otherwise chooses persistent storage, creates an RBW file, and inserts an `RBW` replica. `convertTemporaryToRbw`, `append`, and recovery paths move or mutate replica files, bump generation stamps, and replace entries in `volumeMap`. `finalizeBlock` calls `finalizeReplica`, which moves the files into finalized storage, releases reservations, tracks RAM-disk replicas, and updates `volumeMap`.

Recovery has explicit writer arbitration. `recoverCheck`, `recoverAppend`, `recoverClose`, `recoverRbw`, `initReplicaRecovery`, and `updateReplicaUnderRecovery` stop or take over in-flight writers, validate generation stamps and lengths, truncate corrupt trailing bytes when needed, create `RUR` state, and finalize recovered replicas. Copy-on-truncate uses a new block ID and creates a temporary/RBW copy before finalizing.

Invalidation separates memory removal, client-cache invalidation, NameNode notification, and disk deletion. `invalidate` schedules async or sync deletion through `FsDatasetAsyncDiskService`; `removeReplicaFromMem` removes a replica under a directory lock, marks it in `deletingBlock`, releases pipeline reservations, discards RAM-disk tracker state, invalidates short-circuit descriptors, and uncaches it.

Directory-scanner reconciliation in `checkAndUpdate` compares scanner `ScanInfo` with `volumeMap`. It can add missing disk blocks, remove memory-only blocks, delete orphan metadata, resolve duplicate replicas, update generation stamps or file locations, report corrupt length/regular-file mismatches, and handle provided storage specially.

## State and Persistence
The durable state is block and metadata files under each volume's block-pool directory, plus DataStorage version/trash/rolling-upgrade state. In-memory state includes `volumeMap`, `storageMap`, cache maps, failed-volume info, RAM-disk lazy-persist queues, `deletingBlock`, and lock structures. Persistence-sensitive transitions are file renames, copies, hard links, fsyncs on finalize when requested, async deletion tasks, and lazy-persist copy/activation. `computeChecksum` writes metadata headers and chunk CRCs when a copy target needs a full checksum.

## Dependencies and Integration Points
This class sits between DataNode services and the local filesystem. It integrates with `DataNode`, `DataStorage`, `BlockScanner`, `DirectoryScanner`, `ShortCircuitRegistry`, `FsDatasetAsyncDiskService`, `FsDatasetCache`, `RamDiskAsyncLazyPersistService`, `FileIoProvider`, `DataNodeMetrics`, `DefaultMetricsSystem`, and NameNode notifications. It depends heavily on `ReplicaInfo` subclasses, `FsVolumeImpl`, `BlockPoolSlice`, `StorageLocation`, `DatanodeStorage`, and HDFS protocol classes.

## Risks
The main risks are lock-order regressions, missed reference cleanup, stale `volumeMap` entries after disk failure, races between async deletion and scanner repair, memory leaks in cache/lazy-persist reservation accounting, generation-stamp mistakes during recovery, and data loss during same-mount hard-link moves or copy-on-truncate. Directory-scanner notification throttling must not hide sustained loss. `getStorageUuidForLock` can throw before lock acquisition, so callers must tolerate missing replicas. Several paths intentionally do disk I/O outside broader locks; moving that work under locks would risk stalls.

## Test Signals
High-value tests include append/recover/finalize state transitions, failed writer takeover, dynamic volume add/remove, duplicate storage UUID detection, volume failure toleration, directory-scanner add/remove/corrupt reconciliation, block reports by storage, async deletion and `deletingBlock` cleanup, pmem cache input stream paths, RAM-disk lazy persist and eviction, same-disk tiering moves, and copy-on-truncate recovery. Metrics timers around create/finalize/recover/check operations also provide observable regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetUtil.java

## Purpose
`FsDatasetUtil` contains package-level and public helpers used by the FsDataset implementation for block metadata naming, generation-stamp parsing, file opening/seeking, checksum creation, direct-memory stream creation, and mapped-cache cleanup.

## Important APIs and Types
- `isUnlinkTmpFile` and `getOrigFile` identify and reverse DataNode unlink temporary filenames.
- `createNullChecksumByteArray` writes a block metadata header using `DataChecksum.Type.NULL`.
- `getMetaFile`, `findMetaFile`, `getGenerationStampFromFile`, and `parseGenerationStamp` encode HDFS block metadata filename conventions.
- `openAndSeek` returns a `FileDescriptor` from a read-only `RandomAccessFile`.
- `getInputStreamAndSeek` wraps a positioned file channel as an `InputStream`.
- `getDirectInputStream` reflectively constructs `java.nio.DirectByteBuffer` from a native address.
- `computeChecksum` creates a lightweight `FinalizedReplica` wrapper and delegates full checksum generation to `FsDatasetImpl.computeChecksum`.
- `deleteMappedFile` removes pmem cache files by path.

## Control Flow
The metadata helpers rely on filenames shaped as `blk_<id>_<generation>.meta`. `findMetaFile` lists the block's parent and requires exactly one matching metadata file. Seek helpers open a `RandomAccessFile`, position it, then expose either the descriptor or channel stream while cleaning up on failure. Direct-stream creation uses reflection and wraps the direct buffer in Jackson's `ByteBufferBackedInputStream`.

## State and Persistence
This class has no persistent fields. It reads and deletes local files and writes metadata only through delegated checksum generation. Failure handling is important because `openAndSeek` returns a descriptor while the `RandomAccessFile` object is not explicitly returned to the caller, making ownership subtle.

## Dependencies and Integration Points
It depends on `DatanodeUtil`, `Block`, `BlockMetadataHeader`, `DataChecksum`, `FinalizedReplica`, `ReplicaInfo`, `IOUtils`, and Java NIO/file APIs. It is used by `FsDatasetImpl`, `FsVolumeImpl`, cache loaders, and block scanner/iterator code.

## Risks
Risks include ambiguous metadata files, malformed generation stamps, reflective access to `DirectByteBuffer` breaking under module restrictions, integer truncation of direct-buffer length, and delete failures for persistent-memory cache paths. Metadata filename parsing is tightly coupled to HDFS block naming.

## Test Signals
Tests should cover single/missing/multiple metadata lookup, unlink suffix validation, generation-stamp parse failures, checksum generation against known data, direct input stream creation when native address access is allowed, and mapped-file deletion failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsVolumeImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsVolumeImpl.java

## Purpose
`FsVolumeImpl` represents one local DataNode storage volume. It owns per-volume block-pool slices, space accounting, reference counting, block file creation and movement, block iteration, directory scanning, volume health checks, lazy-persist target paths, and per-volume cache worker execution.

## Important APIs and Types
- Implements `FsVolumeSpi` and exposes `obtainReference`, `getCapacity`, `getAvailable`, `getDfsUsed`, `getBlockPoolUsed`, `getStorageLocation`, `getStorageType`, `newBlockIterator`, `loadBlockIterator`, `compileReport`, `check`, `loadLastPartialChunkChecksum`, and `getMetrics`.
- Holds `bpSlices`, `storageLocation`, `currentDir`, `DF usage`, `ReservedSpaceCalculator`, `reservedForReplicas`, `CloseableReferenceCount`, `DataNodeVolumeMetrics`, same-disk tiering fields, and `cacheExecutor`.
- Nested `FsVolumeReferenceImpl` enforces refcount ownership. Nested `BlockIteratorImpl` persists scanner cursor state using JSON `BlockIteratorState`.
- Block mutation helpers include `createTmpFile`, `createRbwFile`, `addFinalizedBlock`, `append`, `createRbw`, `convertTemporaryToRbw`, `createTemporary`, `updateRURCopyOnTruncate`, `moveBlockToTmpLocation`, `hardLinkBlockToTmpLocation`, and `copyBlockToLazyPersistLocation`.

## Control Flow
Construction validates storage location, creates reserved-space calculators and disk usage state, initializes metrics, base URI, cache executor, and same-disk tiering mount info. Non-RAM volumes with a live DataNode get a bounded thread pool for cache tasks. Reference acquisition increments `CloseableReferenceCount`; volume close marks the reference count closed and asks `FsDatasetImpl` to interrupt pipeline writers on this volume.

Capacity reporting subtracts reserved space, DFS-used bytes, and replica write reservations. With same-disk tiering, visible capacity is multiplied by mount/storage-type ratio from `MountVolumeMap`; non-DFS used also subtracts counterpart volume DFS usage when DISK and ARCHIVE share a mount.

Block creation reserves anticipated bytes before creating tmp or RBW files and releases on failure. Finalization delegates to `BlockPoolSlice.addFinalizedBlock`, preserves last partial checksum when needed, releases reserved write bytes, and returns a finalized `ReplicaInfo`. Append moves finalized files into RBW, loads the last partial checksum, decrements old DFS accounting, and reserves future bytes. Temporary-to-RBW and recovery-copy paths move, hard-link, copy, or truncate block files using `FsDatasetImpl` helpers.

`BlockIteratorImpl` walks the finalized block directory hierarchy in sorted order. It validates block directory placement, finds metadata files, populates generation stamp and length, and persists cursor state atomically to `<bpid>/<name>.cursor` via a temp file and atomic move. `compileReport` recursively scans finalized directories, pairing sorted block files with metadata files and adding `ScanInfo` entries for the directory scanner.

## State and Persistence
Persistent state includes block pool directories, finalized/RBW/tmp/lazypersist subdirectories, block and metadata files, and iterator cursor JSON files. In-memory state includes block-pool slices, refcounts, reserved write bytes, capacity cache, metrics, and executor queues. File movement, metadata copy, hard linking, truncation, and deletion update both disk state and `BlockPoolSlice` accounting.

## Dependencies and Integration Points
`FsVolumeImpl` depends on `FsDatasetImpl`, `BlockPoolSlice`, `FileIoProvider`, `DataStorage`, `DatanodeUtil`, `ReservedSpaceCalculator`, `ReplicaBuilder`, `ReplicaInfo` subclasses, `RamDiskReplicaTracker`, Jackson, Hadoop `DF`, and DataNode metrics. It is managed by `FsVolumeList`, called by `FsDatasetImpl`, and scanned by `BlockScanner`/`DirectoryScanner`.

## Risks
The largest risks are leaked references blocking removal, inaccurate reserved-space accounting after failed creates or pipeline releases, stale capacity ratios under same-disk tiering, incorrect last-partial-checksum preservation during append/finalize, cursor corruption causing scanner gaps or repeats, hard-link move crash safety, and recursive scanner behavior over large directories. `open` file operations use `FileIoProvider`, so bypassing it in new code would skip injected fault handling and metrics.

## Test Signals
Tests should cover reference close and volume removal waits, capacity/available math with reserved and same-disk tiering, tmp/RBW/finalized transitions, append checksum state, recovery truncate/copy, iterator save/load/resume, invalid-directory warnings, compileReport block/meta pairing, block-pool deletion safety, lazy-persist copy activation, and metrics unregistration on shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsVolumeImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsVolumeImplBuilder.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsVolumeImplBuilder.java

## Purpose
`FsVolumeImplBuilder` centralizes construction of `FsVolumeImpl` and `ProvidedVolumeImpl` instances from dataset, storage ID, storage directory, configuration, IO provider, and optional test disk-usage state.

## Important APIs and Types
The builder has fluent package-private setters for `FsDatasetImpl`, storage ID, `StorageDirectory`, `Configuration`, `FileIoProvider`, and test-only `DF usage`. `build()` selects `ProvidedVolumeImpl` when the storage type is `StorageType.PROVIDED`; otherwise it creates a `DF` rooted at the storage directory parent if tests did not inject one, and constructs `FsVolumeImpl`.

## Control Flow
The constructor initializes fields to null. `build()` first branches on storage type. Provided storage always receives a `FileIoProvider` fallback when none was supplied. Local filesystem storage ensures `usage` exists, then passes all inputs to the `FsVolumeImpl` constructor.

## State and Persistence
The builder itself is transient and has no persistence. It determines the `DF` object that will later drive capacity and mount accounting in the volume.

## Dependencies and Integration Points
It is used by `FsDatasetImpl.addVolume` and test helpers. It depends on `DataStorage.StorageDirectory`, `StorageLocation` storage type, `ProvidedVolumeImpl`, `FsVolumeImpl`, and `FileIoProvider`.

## Risks
Missing required fields are not validated locally, so nulls fail later in constructors. Incorrect PROVIDED detection would instantiate the wrong volume type. A null `FileIoProvider` receives a minimal fallback provider with null DataNode/context, which is suitable for tests but may hide instrumentation if used accidentally.

## Test Signals
Unit tests should verify PROVIDED and non-PROVIDED branching, injected `DF` usage preservation, fallback `FileIoProvider`, and failures for malformed storage directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsVolumeImplBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsVolumeList.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsVolumeList.java

## Purpose
`FsVolumeList` maintains the active `FsVolumeImpl` set for a DataNode. It chooses volumes for new blocks, aggregates capacity and usage, coordinates block-pool scans across volumes, tracks failed and removing volumes, integrates block scanners, and maintains same-disk tiering mount metadata.

## Important APIs and Types
- Active volumes live in a `CopyOnWriteArrayList`; failed volume data lives in synchronized `TreeMap<StorageLocation, VolumeFailureInfo>`; removed-but-referenced volumes live in `ConcurrentLinkedQueue`.
- Uses `VolumeChoosingPolicy<FsVolumeImpl>`, optional `BlockScanner`, optional `DataNodeDiskMetrics`, `AutoCloseableLock` and `Condition`.
- Key methods: `getNextVolume`, `getNextTransientVolume`, `getVolumeByMount`, `addVolume`, `removeVolume(StorageLocation, boolean)`, `handleVolumeFailures`, `waitVolumeRemoved`, `getAllVolumesMap`, `addBlockPool`, `removeBlockPool`, and usage aggregators.

## Control Flow
Volume choice first filters by requested storage type, then excludes slow disks from `DataNodeDiskMetrics`, calls the configured chooser, and obtains a reference. Closed chosen volumes are removed from the candidate list and selection retries. Same-disk tiering can directly return a volume by mount and storage type if enabled and enough capacity is available.

Adding a volume appends it to the active copy-on-write list, updates `MountVolumeMap` and capacity ratio config for same-disk tiering, registers the block scanner or releases the reference if no scanner exists, clears failure info, and logs the storage ID. Removing a volume removes it from active list, removes tiering and scanner state, closes it, shuts it down, and places it into `volumesBeingRemoved` until references drain. `handleVolumeFailures` records failure info, removes each failed volume, and waits for reference release.

Block pool and replica map initialization run one thread per volume using `SubjectInheritingThread`. Exceptions are collected in maps and rethrown as `AddBlockPoolException` after all threads join.

## State and Persistence
The class itself stores runtime volume lists and failure metadata; it does not write disk state. It invokes volume-level block-pool scanning, shutdown, and block-pool deletion hooks that affect disk state. Failure info preserves storage location, failure time, and estimated lost capacity.

## Dependencies and Integration Points
It is owned by `FsDatasetImpl`, feeds `BlockScanner`, uses `MountVolumeMap`/`MountVolumeInfo`, reads `StorageLocation.parseCapacityRatio`, and cooperates with DataNode disk metrics to avoid slow disks. It delegates all per-volume filesystem work to `FsVolumeImpl`.

## Risks
Candidate filtering mutates a local list but depends on volume chooser behavior when empty. Reference leaks can keep removed volumes in `volumesBeingRemoved` indefinitely. Capacity ratio configuration must match storage URIs exactly. Parallel add-block-pool scans can surface partial failures that must be merged by callers. Same-disk tiering allows only one volume per storage type per mount.

## Test Signals
Tests should cover slow-disk exclusion, closed-volume retry, transient volume choice, same-mount volume lookup, dynamic add/remove scanner references, failure info preservation and clearing, wait-for-reference behavior, capacity ratio application, and multi-volume scan exception aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsVolumeList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MappableBlock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MappableBlock.java

## Purpose
`MappableBlock` is the cache-layer abstraction for an HDFS block that has been mapped into a DataNode cache region, either DRAM-backed or persistent-memory-backed.

## Important APIs and Types
It extends `Closeable` and exposes `getLength()`, `getAddress()`, and `getKey()`. `getAddress()` returns a native address when applicable and `-1` otherwise. `getKey()` returns an `ExtendedBlockId` when the implementation tracks one.

## Control Flow
There is no implementation control flow in this interface. Implementations such as `MemoryMappedBlock` and pmem block types provide close behavior and cache identity.

## State and Persistence
The interface represents a mapped cache resource. Implementations may own mmap buffers, native addresses, persistent-memory files, or block identifiers. `close()` is the lifecycle boundary for unmapping or releasing native resources.

## Dependencies and Integration Points
It is used by `MappableBlockLoader` implementations and by `FsDatasetCache`. It depends only on `ExtendedBlockId` and `Closeable`.

## Risks
Consumers must not assume that `getAddress()` or `getKey()` is meaningful for all implementations; DRAM `MemoryMappedBlock` returns sentinel/null values. Failure to close leaks mapped memory or persistent-memory resources.

## Test Signals
Tests should verify each implementation's length, address/key semantics, idempotent close behavior, and interaction with cache release accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MappableBlock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MappableBlockLoader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MappableBlockLoader.java

## Purpose
`MappableBlockLoader` is the abstract base for DataNode cache loaders. It defines how cache backends initialize, reserve/release cache capacity, map a block, expose usage/capacity, recover persistent mappings, and verify checksums before a block is accepted into cache.

## Important APIs and Types
Abstract methods include `initialize`, `load`, `reserve`, `release`, `getCacheUsed`, `getCacheCapacity`, `isTransientCache`, `isNativeLoader`, and `getRecoveredMappableBlock`. The default `shutdown` is a no-op. Protected helpers `verifyChecksum` and `fillBuffer` implement common checksum validation over file channels.

## Control Flow
`load` implementations are expected to map or copy a block and then call `verifyChecksum`. `verifyChecksum` reads a `BlockMetadataHeader`, obtains `DataChecksum`, and loops over the block channel in up to 8 MiB batches. It fills both block and checksum buffers, computes chunk count including the final partial chunk, and calls `verifyChunkedSums`; premature EOF or missing channels throw `IOException`.

## State and Persistence
This base class keeps no fields. It reads block data and metadata streams but does not itself persist state. Reservation semantics are delegated to concrete `CacheStats` or pmem allocators.

## Dependencies and Integration Points
It is used by `MemoryMappableBlockLoader`, `PmemMappableBlockLoader`, `NativePmemMappableBlockLoader`, and `FsDatasetCache`. It depends on `DNConf`, `ExtendedBlockId`, `BlockMetadataHeader`, `DataChecksum`, Java file channels, and Hadoop `Preconditions`.

## Risks
Checksum verification is I/O intensive and sensitive to stream positioning. Very small `bytesPerChecksum` values increase buffer sizes/chunk counts. Implementations must clean up mapped resources when verification fails. `fillBuffer` returns partial EOF counts, so callers must correctly detect premature EOF.

## Test Signals
Tests should cover checksum pass/fail, premature EOF in data and metadata, final partial chunks, missing file channels, reservation failure propagation in implementations, recovered pmem mappings, and shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MappableBlockLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MappableBlockLoaderFactory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MappableBlockLoaderFactory.java

## Purpose
`MappableBlockLoaderFactory` selects the cache loader implementation for DataNode block caching based on persistent-memory configuration and native PMDK availability.

## Important APIs and Types
It is a non-instantiable final class with one public static method, `createCacheLoader(DNConf conf)`. It returns `MemoryMappableBlockLoader` when no pmem volumes are configured, `NativePmemMappableBlockLoader` when native IO and PMDK are available, and `PmemMappableBlockLoader` otherwise.

## Control Flow
The selection is a simple ordered decision tree: no pmem configuration means DRAM mmap/mlock; pmem plus native PMDK means native loader; pmem without native support means file-backed pmem loader.

## State and Persistence
The factory holds no state. The chosen loader determines whether cache state is transient memory or persistent files/native mappings.

## Dependencies and Integration Points
It depends on `DNConf.getPmemVolumes()` and `NativeIO.POSIX.isPmdkAvailable()`. It is consumed by `FsDatasetCache` initialization.

## Risks
Misdetected native availability changes the cache persistence and performance profile. Configuration with pmem volumes but missing PMDK falls back rather than failing, so tests should verify intended behavior.

## Test Signals
Tests should mock no pmem, pmem with PMDK, and pmem without PMDK, and assert returned loader classes and transient/native flags after initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MappableBlockLoaderFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MemoryMappableBlockLoader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MemoryMappableBlockLoader.java

## Purpose
`MemoryMappableBlockLoader` implements transient DRAM cache loading by memory-mapping a block file, locking it into memory with native cache manipulation, and verifying checksums before returning a `MemoryMappedBlock`.

## Important APIs and Types
It extends `MappableBlockLoader`, owns `CacheStats memCacheStats`, and implements `initialize`, `load`, capacity/usage accessors, `reserve`, `release`, `isTransientCache`, `getRecoveredMappableBlock`, and `isNativeLoader`.

## Control Flow
`initialize` creates `CacheStats` using `DNConf.getMaxLockedMemory()`. `load` maps the block channel read-only from offset zero to the provided length, calls `NativeIO.POSIX.getCacheManipulator().mlock`, verifies the checksum through the inherited helper, then wraps the mapping in `MemoryMappedBlock`. If any step fails before the wrapper is created, the `finally` block unmaps the buffer, which also unlocks it.

## State and Persistence
Cache state is transient and tracked only in `CacheStats` and mmap/locked memory. There is no recovery for DRAM cache; `getRecoveredMappableBlock` returns null. Closing the returned block releases the mmap.

## Dependencies and Integration Points
It depends on native IO cache manipulation, Java `MappedByteBuffer`, file channels, `CacheStats`, and `FsDatasetCache`. It is selected by `MappableBlockLoaderFactory` when no pmem volumes are configured.

## Risks
Native `mlock` and `munmap` failures or platform differences can break caching. The loader assumes `blockIn` has a channel and `length` is valid for mmap. Resource cleanup on checksum failure is critical because locked memory is scarce.

## Test Signals
Tests should cover initialization capacity, successful mmap/mlock/checksum, checksum failure cleanup, reserve/release accounting, null recovery, transient/native flags, and close-driven unmapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MemoryMappableBlockLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MemoryMappedBlock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MemoryMappedBlock.java

## Purpose
`MemoryMappedBlock` is the DRAM mmap-backed implementation of `MappableBlock`.

## Important APIs and Types
It stores a `MappedByteBuffer mmap` and immutable `length`. `getLength` returns the cached byte count. `getAddress` returns `-1L` because a Java mmap address is not exposed. `getKey` returns null because this implementation does not store an `ExtendedBlockId`. `close` unmaps through `NativeIO.POSIX.munmap` and nulls the buffer.

## Control Flow
Construction asserts positive length. Close is idempotent at the Java level: only a non-null buffer is unmapped. There is no explicit synchronization.

## State and Persistence
The mapped data is transient virtual memory backed by the original block file. No persistent cache file or block key is stored here.

## Dependencies and Integration Points
Created by `MemoryMappableBlockLoader` and managed by `FsDatasetCache`. Depends on Java NIO and Hadoop native IO.

## Risks
Consumers must not expect address/key access for this implementation. Concurrent close/read misuse could unmap a buffer while another user still expects it. Native unmap behavior is platform-sensitive.

## Test Signals
Tests should verify length reporting, sentinel address/key values, idempotent close, and integration with cache eviction/release paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MemoryMappedBlock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MountVolumeInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MountVolumeInfo.java

## Purpose
`MountVolumeInfo` stores the per-filesystem-mount relationship between storage types and volumes for same-disk tiering. It lets the dataset locate a counterpart volume by `StorageType` and compute capacity ratios for DISK/ARCHIVE sharing one mount.

## Important APIs and Types
It holds an `EnumMap<StorageType, FsVolumeImpl>`, an `EnumMap<StorageType, Double>` of configured capacity ratios, and `reservedForArchiveDefault` from `DFS_DATANODE_RESERVE_FOR_ARCHIVE_DEFAULT_PERCENTAGE`. Methods include `getVolumeRef`, `getCapacityRatio`, `addVolume`, `removeVolume`, `setCapacityRatio`, and `size`.

## Control Flow
Construction clamps the default archive reservation to `[0, 1]`. `getVolumeRef` obtains a volume reference for the requested type and returns null if absent or closed. `getCapacityRatio` returns an explicit ratio if present; otherwise, if another ratio is set, it returns the leftover capacity; otherwise, for paired DISK/ARCHIVE volumes it applies the default archive split, and for all other cases returns 1. `addVolume` rejects duplicate storage types on a mount.

## State and Persistence
State is runtime-only. It influences capacity reporting and same-mount block placement but does not persist configuration changes to disk.

## Dependencies and Integration Points
It is owned by `MountVolumeMap`, called by `FsVolumeList` and `FsVolumeImpl`, and depends on `StorageType`, `FsVolumeReference`, and DFS configuration keys.

## Risks
Capacity ratios can leave unexpected leftover capacity when only one side is configured. Duplicate storage types are logged and skipped rather than throwing. Closed-volume references become null and can force fallback placement. Ratio validation only ensures the sum does not exceed 1 at set time.

## Test Signals
Tests should cover clamping defaults, explicit ratio lookup, leftover ratio calculation, DISK/ARCHIVE default split, duplicate storage type rejection, closed-volume reference handling, removal cleanup, and ratio sum failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MountVolumeInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MountVolumeMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MountVolumeMap.java

## Purpose
`MountVolumeMap` maps filesystem mount strings to `MountVolumeInfo` for same-disk tiering. It lets DataNode block placement choose another storage type on the same mount and lets capacity reporting apply per-mount capacity ratios.

## Important APIs and Types
It owns a `ConcurrentMap<String, MountVolumeInfo>` and a `Configuration`. Methods include `getVolumeRefByMountAndStorageType`, `getCapacityRatioByMountAndStorageType`, `addVolume`, `removeVolume`, `setCapacityRatio`, and public `hasMount`.

## Control Flow
`addVolume` ignores empty mount strings, creates a `MountVolumeInfo` for new mounts, and delegates volume insertion. `removeVolume` removes the volume by storage type and drops the mount entry when empty. `setCapacityRatio` delegates to `MountVolumeInfo` and throws `IOException` when configured ratios for a mount would exceed 1. Lookups return null or 1 when the mount is unknown.

## State and Persistence
All state is runtime-only and derived from active volumes plus configuration. It affects volume selection and capacity math but stores nothing on disk.

## Dependencies and Integration Points
It is created by `FsVolumeList`, returned through `FsDatasetImpl.getMountVolumeMap`, used by `FsVolumeImpl.getCapacity` and `getActualNonDfsUsed`, and supports same-mount placement in `FsDatasetImpl.moveBlockAcrossStorage`.

## Risks
Concurrent map operations avoid map corruption, but per-mount `MountVolumeInfo` updates are not independently synchronized. Empty mount strings disable tiering for a volume. Configuration errors surface as `IOException` during add-volume ratio application. If a mount is removed concurrently, callers must tolerate null lookups.

## Test Signals
Tests should verify add/remove lifecycle, empty-mount no-op behavior, default capacity ratio for unknown mounts, ratio failure exception messages, concurrent lookup during removal, and `hasMount` visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MountVolumeMap.java -->
