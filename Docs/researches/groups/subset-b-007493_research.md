# Research group subset-b-007493

This grouped report covers the requested Hadoop HDFS DataNode dataset, metrics, WebHDFS, and disk-balancer command files. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/NativePmemMappableBlockLoader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/NativePmemMappableBlockLoader.java

## Purpose

`NativePmemMappableBlockLoader` is the PMDK-backed persistent-memory cache loader for DataNode block caching. It maps a selected PMem cache file through `NativeIO.POSIX.Pmem`, verifies block checksums while copying block bytes into the mapped region, and returns a `NativePmemMappedBlock` that exposes the native address to the cache subsystem.

## Important APIs, Control Flow, and State

The important methods are `initialize(DNConf)`, `load(...)`, `verifyChecksumAndMapBlock(...)`, `isNativeLoader()`, and `getRecoveredMappableBlock(...)`. `load` obtains the source block `FileChannel`, asks `PmemVolumeManager` for the reserved cache path, maps it with `POSIX.Pmem.mapBlock(path, length, false)`, streams block/meta chunks through `DataChecksum.verifyChunkedSums`, copies verified bytes with `POSIX.Pmem.memCopy`, syncs the region with `memSync`, and creates the mapped-block handle. Recovery remaps an existing cache file with `mapBlock(..., true)`, reconstructs the `ExtendedBlockId` from the filename and block pool id, and restores the key-to-volume mapping in `PmemVolumeManager`.

State is mostly external: the cache file, native mapped address/length, and `PmemVolumeManager`'s block-to-volume index. On failure before a `NativePmemMappedBlock` is created, the loader unmaps the region and deletes the mapped file. Checksum and copy processing uses 8 MiB chunk groups sized by the block's checksum layout, so partial EOF and checksum failures abort before exposing the block as cached.

## Dependencies, Integration, Risks, and Tests

This class depends on `PmemMappableBlockLoader`, `PmemVolumeManager`, `BlockMetadataHeader`, `DataChecksum`, `NativeIO.POSIX.Pmem`, `FsDatasetUtil`, and `ExtendedBlockId`. It integrates with `FsDatasetCache` through the `MappableBlockLoader` abstraction and with PMem recovery through `getRecoveredMappableBlock`.

Risks include native-library availability, null cache paths if reservation state is missing, incorrect unmap/delete cleanup on partial copy, and native length/page alignment behavior. Tests should cover successful cache load, checksum failure cleanup, premature EOF, recovery of existing cache files, unavailable native PMem, and no stale mapped files left after failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/NativePmemMappableBlockLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/NativePmemMappedBlock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/NativePmemMappedBlock.java

## Purpose

`NativePmemMappedBlock` is the `MappableBlock` implementation for a block cached in persistent memory through a native PMDK mapping. It holds the mapped address, mapped length, and `ExtendedBlockId` needed by the cache and cleanup paths.

## Important APIs, Control Flow, and State

The public interface comes from `MappableBlock`: `getLength()`, `getAddress()`, `getKey()`, and `close()`. Construction asserts a positive length and stores the native address. `close` is idempotent through the `pmemMappedAddress != -1L` guard: it resolves the cache path through `PmemVolumeManager`, calls `NativeIO.POSIX.Pmem.unmapBlock`, marks the address invalid, deletes the cache file, and logs the uncache event.

State is per cached replica and in-memory only, while the cache file itself is durable until `close` deletes it. Exceptions during close are logged as warnings rather than propagated, which is consistent with cache cleanup paths but can leave files or mappings behind if native unmap fails.

## Dependencies, Integration, Risks, and Tests

The class integrates with `NativePmemMappableBlockLoader`, `PmemVolumeManager`, `NativeIO.POSIX.Pmem`, and `FsDatasetUtil`. `getAddress()` distinguishes this implementation from non-native `PmemMappedBlock`, which returns `-1`.

Risks center on cleanup reliability: cache path lookup can fail, native unmap may report false, and delete failure is swallowed after logging. Tests should assert idempotent close, native unmap invocation, cache-file deletion, warning behavior on failures, and that recovered native mappings use the expected key and length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/NativePmemMappedBlock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/PmemMappableBlockLoader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/PmemMappableBlockLoader.java

## Purpose

`PmemMappableBlockLoader` is the default file-backed persistent-memory cache loader that does not use PMDK native mappings. It copies a block into a PMem-backed filesystem path managed by `PmemVolumeManager`, verifies checksums against the copied data, and returns a `PmemMappedBlock` cache handle.

## Important APIs, Control Flow, and State

`initialize(DNConf)` initializes the singleton `PmemVolumeManager`, records whether cache recovery is enabled, and returns `CacheStats(0)` because PMem is used instead of locked DRAM. `load(...)` gets the block channel, resolves the reserved cache path, writes block bytes into a `RandomAccessFile` via `transferTo`, rewinds the cache file channel, verifies the cached bytes with inherited `verifyChecksum`, and returns a `PmemMappedBlock`. `reserve`, `release`, `getCacheUsed`, and `getCacheCapacity` are delegated to the volume manager.

The PMem file is persistent state. If loading fails, the partially copied mapped file is deleted. `getRecoveredMappableBlock` reconstructs the `ExtendedBlockId` from the cache filename and block pool id, creates a `PmemMappedBlock` using the cache file length, and restores the manager's volume mapping. `shutdown` deletes PMem cache contents only when recovery is disabled.

## Dependencies, Integration, Risks, and Tests

This loader depends on `MappableBlockLoader`, `PmemVolumeManager`, `PmemMappedBlock`, `DNConf`, `IOUtils`, and `FsDatasetUtil`. It is selected by cache-loader factory logic for PMem caching and integrates with the broader cache accounting path through `reserve/release`.

Risks include mismatches between reservation state and cache path lookup, partial `transferTo` behavior on some filesystems, checksum verification only after copy, and stale persistent cache files if recovery settings are wrong. Tests should cover reservation/release accounting, failed checksum cleanup, recovery-enabled shutdown preserving files, recovery-disabled shutdown cleanup, and block-id parsing from cache filenames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/PmemMappableBlockLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/PmemMappedBlock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/PmemMappedBlock.java

## Purpose

`PmemMappedBlock` represents a DataNode block cached on a PMem filesystem without a native mapped address. It is the lightweight handle returned by `PmemMappableBlockLoader`.

## Important APIs, Control Flow, and State

The implementation stores only `length` and `ExtendedBlockId`. `getLength()` and `getKey()` expose that metadata; `getAddress()` returns `-1L` to signal that no native address is available. `close()` resolves the cache path through `PmemVolumeManager`, deletes the cache file, and logs success or warning.

State is in-memory for the handle and persistent on disk for the cache file until close or loader shutdown. There is no explicit volume accounting update in this class; release accounting is handled by the cache manager and `PmemMappableBlockLoader`.

## Dependencies, Integration, Risks, and Tests

The class depends on `MappableBlock`, `PmemVolumeManager`, `FsDatasetUtil`, and `ExtendedBlockId`. It integrates with non-native PMem cache reads where the cache file path, rather than an address, is the durable identity.

Risks include silent cleanup failure and a null path if the volume-manager mapping was already removed. Tests should verify address sentinel behavior, close deletes the expected file, repeated close behavior is acceptable, and warning paths do not break cache-manager cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/PmemMappedBlock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/PmemVolumeManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/PmemVolumeManager.java

## Purpose

`PmemVolumeManager` is the singleton allocator, path resolver, recovery scanner, and cleanup owner for DataNode persistent-memory cache volumes. It validates configured PMem directories, tracks per-volume capacity/usage, maps each cached `ExtendedBlockId` to a volume index, and constructs hierarchical cache paths.

## Important APIs, Control Flow, and State

Important APIs include `init`, `getInstance`, `reserve`, `release`, `loadVolumes`, `recoverCache`, `recoverBlockKeyToVolume`, `verifyIfValidPmemVolume`, `createBlockPoolDir`, `chooseVolume`, `idToCacheFilePath`, and `getCachePath`. Initialization requires at least one configured PMem directory, creates/uses an `hdfs_pmem_cache` child directory, optionally cleans it if recovery is disabled, verifies mmap/write/force/delete behavior with a temporary file, and initializes `UsedBytesCount` counters using usable space or test override.

Reservations are synchronized and use round-robin `chooseVolume` with capacity checks; successful reservations insert `blockKeyToVolume`. Release removes that mapping and decrements the selected counter. Recovery walks each volume's block-pool directory recursively, asks the active cache loader to rebuild a `MappableBlock`, updates key-to-volume mappings, increases capacity by recovered bytes, and reserves the recovered used bytes. Cache paths are `pmemVolume/bpid/subdirN/subdirM/blockId`, with subdirectory numbers derived from block-id bits.

## Dependencies, Integration, Risks, and Tests

The manager depends on Commons IO directory traversal/cleanup, `NativeIO.POSIX.munmap`, `MappedByteBuffer`, `FsDatasetUtil`, `ExtendedBlockId`, and HDFS PMem configuration keys. It is shared by both native and non-native PMem loaders and mapped-block cleanup classes.

Risks include singleton lifecycle issues in tests, non-atomic interaction between reservation and file creation, `release` assuming a present mapping, recursive recovery accepting unexpected files, max-capacity adjustment during recovery, and cleanup deleting all files under configured PMem cache directories. Tests should cover invalid volume filtering, capacity exhaustion, round-robin selection, path layout, block-pool directory creation, recovery accounting, cleanup behavior, and concurrent reserve/release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/PmemVolumeManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/ProvidedVolumeImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/ProvidedVolumeImpl.java

## Purpose

`ProvidedVolumeImpl` implements an `FsVolumeImpl` for HDFS PROVIDED storage: blocks are not physically stored by the DataNode, but described by an external `BlockAliasMap<FileRegion>` and served from a remote `FileSystem`. The class presents those external regions as finalized replicas while rejecting write-oriented volume operations.

## Important APIs, Control Flow, and State

Key nested types are `ProvidedVolumeDF`, `ProvidedBlockPoolSlice`, `ProvidedBlockIteratorState`, and `ProviderBlockIteratorImpl`. The constructor enforces `StorageType.PROVIDED`, records the base URI, and opens the remote filesystem. `addBlockPool` creates a slice with a configurable alias-map implementation, defaulting to `TextFileRegionAliasMap`. `getVolumeMap` calls each slice's `fetchVolumeMap`, which retries alias-map reader creation, filters `FileRegion` entries whose paths belong under the volume URI, builds finalized `ReplicaInfo` objects with path prefix/suffix, offset, length, generation stamp, optional `PathHandle` from nonce bytes, and remote FS, then inserts them into the global `ReplicaMap` unless a local replica already exists.

Provided volume state is mostly in memory: `bpSlices`, per-slice `ReplicaMap`, block counts, and synthetic DFS-used counters. The durable source of truth is the alias map and remote storage. Directory scan/report flow calls `aliasMap.refresh()` and emits `ScanInfo` for current regions. Block iterators do not persist local cursor state; `save` only updates timestamps and `load` rewinds. Capacity is reported as DFS used, available is clamped to zero, non-DFS used is zero, and write/reservation/temp/RBW/lazy-persist operations throw `UnsupportedOperationException`.

## Dependencies, Integration, Risks, and Tests

This class integrates with provided-storage alias maps, `ReplicaBuilder`, `ReplicaMap`, `DirectoryScanner.ReportCompiler`, `FsDatasetImpl`, `FileSystem`, `PathHandle`, and `VolumeCheckResult`. It also inherits common volume behavior from `FsVolumeImpl` while overriding most mutation paths as unsupported.

Risks include alias-map reader failure silently producing an empty provided volume, URI prefix filtering mistakes in `containsBlock`, assumptions that alias-map iteration is sorted for iterator resume semantics, duplicate block IDs being skipped if local replicas exist, and stale in-memory volume maps after alias-map changes. Tests should cover suffix extraction, local and absolute URI containment, alias-map retry behavior, replica construction with nonce/path handle, duplicate handling, directory scan refresh, block iterator rewind/load, and that all unsupported write paths fail predictably.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/ProvidedVolumeImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/RamDiskAsyncLazyPersistService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/RamDiskAsyncLazyPersistService.java

## Purpose

`RamDiskAsyncLazyPersistService` owns per-volume worker queues for asynchronously copying transient RAM_DISK replicas to persistent storage. It lets lazy-persist work follow volume addition/removal while keeping only one persistence task active per target volume.

## Important APIs, Control Flow, and State

The service maintains a `Map<String, ThreadPoolExecutor>` keyed by storage ID, with one core/max thread per volume and `SubjectInheritingThread` workers. `addVolume`, `removeVolume`, `queryVolume`, `execute`, and `shutdown` manage executor lifecycle. `submitLazyPersistTask` wraps block-pool id, block id, generation stamp, creation time, source `ReplicaInfo`, and target `FsVolumeReference` in a `ReplicaLazyPersistTask` and schedules it on the target volume's executor.

`ReplicaLazyPersistTask.run` obtains the dataset, closes its `FsVolumeReference` with try-with-resources, calls `copyBlockToLazyPersistLocation`, and notifies `FsDatasetImpl.onCompleteLazyPersist`; on any exception it logs and calls `onFailLazyPersist`. State is volatile only in worker queues and the executor map; persisted state is the copied block/meta pair created by the target volume.

## Dependencies, Integration, Risks, and Tests

Dependencies include `DataNode`, `FsDatasetImpl`, `FsVolumeImpl`, `FsVolumeReference`, `ReplicaInfo`, `DFSUtilClient`, and Hadoop thread/security helpers. The service is part of DataNode lazy-persist eviction and recovery flow for transient storage.

Risks include executor map becoming null after shutdown, scheduling against removed volumes, resource leaks if scheduling fails before task execution, callbacks racing with dataset shutdown, and per-volume serialization limiting throughput. Tests should cover add/remove/query, duplicate volume rejection, failure cleanup of `FsVolumeReference`, success and failure callbacks, shutdown behavior, and ordering of multiple tasks for the same storage ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/RamDiskAsyncLazyPersistService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/RamDiskReplicaLruTracker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/RamDiskReplicaLruTracker.java

## Purpose

`RamDiskReplicaLruTracker` is the default `RamDiskReplicaTracker` implementation. It tracks RAM_DISK replicas, queues them for lazy persistence, and chooses persisted replicas for eviction using least-recently-used ordering.

## Important APIs, Control Flow, and State

State is split across `replicaMaps` (`bpid -> blockId -> RamDiskReplicaLru`), `replicasNotPersisted` FIFO queue, and `replicasPersisted` `TreeMultimap` keyed by last-used time. `addReplica` inserts a new record and queues it for persistence. `touch` increments read count and, if the block has been persisted, updates its LRU timestamp. `recordStartLazyPersist` records the target persistent volume; `recordEndLazyPersist` records saved files, removes the replica from the not-persisted queue, assigns last-used time, inserts it into the persisted LRU map, and marks it persisted.

`dequeueNextReplicaToPersist` lazily skips stale queue entries whose replica map entry was discarded. `getNextCandidateForEviction` removes oldest persisted entries until it finds one still present. `discardReplica` optionally deletes saved persistent copies, removes the in-memory map entry, and removes persisted LRU state while leaving not-persisted queue cleanup lazy.

## Dependencies, Integration, Risks, and Tests

The class depends on Guava `TreeMultimap`, `Time.monotonicNow`, and the abstract `RamDiskReplicaTracker` contract. It integrates with lazy writer scheduling, RAM_DISK eviction, read-hit accounting, and block deletion paths in `FsDatasetImpl`.

Risks include synchronized coarse locking, stale queue growth if many unpersisted replicas are discarded, `recordStartLazyPersist` assuming the replica exists, and LRU timestamp collisions handled by replica comparability. Tests should cover FIFO persistence ordering, failed persist reenqueue, LRU update on touch, eviction candidate selection, discard with and without saved-copy deletion, and stale-entry skipping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/RamDiskReplicaLruTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/RamDiskReplicaTracker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/RamDiskReplicaTracker.java

## Purpose

`RamDiskReplicaTracker` defines the pluggable policy contract for tracking replicas stored on transient RAM_DISK volumes and coordinating their lazy persistence and eviction. It also provides the shared `RamDiskReplica` state object used by implementations.

## Important APIs, Control Flow, and State

`getInstance(Configuration, FsDatasetImpl)` loads the configured tracker class from `DFS_DATANODE_RAM_DISK_REPLICA_TRACKER_KEY`, instantiates it with `ReflectionUtils`, and initializes it with the dataset. The nested `RamDiskReplica` stores block pool id, block id, RAM disk volume, optional lazy-persist volume, saved block/meta files, creation time, read count, locked bytes reservation, and persisted flag. It can record saved files, delete them, compare by block-pool id and block id, and expose the locked reservation.

The abstract operations define the lifecycle: `addReplica`, `touch`, `dequeueNextReplicaToPersist`, `reenqueueReplicaNotPersisted`, `recordStartLazyPersist`, `recordEndLazyPersist`, `getNextCandidateForEviction`, `numReplicasNotPersisted`, `discardReplica`, and `getReplica`. Persistent state exists only as saved block/meta files; the tracker state itself is memory-resident and rebuilt from dataset events.

## Dependencies, Integration, Risks, and Tests

Dependencies include `FsDatasetImpl`, `FsVolumeImpl`, `FsVolumeSpi`, `DFSConfigKeys`, `ReflectionUtils`, and `Time`. The contract is used by DataNode lazy-persist code to schedule writes, account read/eviction metrics, and decide what can be evicted from RAM_DISK.

Risks include policy implementations not honoring synchronization, saved-file deletion being best-effort, proxy policy misconfiguration causing startup failure, and `setLazyPersistVolume` only checking the target is non-transient. Tests should cover reflective construction, base `RamDiskReplica` equality/comparison, saved-file recording/deletion, invalid transient checkpoint volume rejection, and implementation-specific lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/RamDiskReplicaTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/ReplicaCachingGetSpaceUsed.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/ReplicaCachingGetSpaceUsed.java

## Purpose

`ReplicaCachingGetSpaceUsed` is an `FSCachingGetSpaceUsed` implementation that calculates HDFS-used bytes from the in-memory replica map instead of directory usage scans. It aims to be faster and more exact for block and metadata files on a specific volume/block-pool pair.

## Important APIs, Control Flow, and State

The constructor disables first refresh, records the target `FsVolumeImpl` and block pool id from the builder, and leaves periodic refresh behavior to the base class. `refresh` deep-copies replicas for the block pool through `FsDatasetSpi.deepCopyReplica`, filters them by matching volume storage ID, sums `getBytesOnDisk()` plus `getMetadataLength()`, and stores the result in the inherited atomic `used`.

There is no durable state. The value is a cache derived from dataset replica metadata, and debug logs are emitted if copying or full refresh exceeds fixed thresholds. Exceptions are logged and leave the last cached value intact.

## Dependencies, Integration, Risks, and Tests

The class depends on `FSCachingGetSpaceUsed`, `FsVolumeImpl`, `FsDatasetSpi`, `ReplicaInfo`, Commons Collections, and `Time`. It integrates with volume space accounting when configured as `fs.getspaceused.classname`.

Risks include stale values if refresh fails, cost of deep-copying large replica maps, undercounting files not represented by replicas, and volume identity depending on storage ID equality. Tests should compare against expected replica sums, verify empty/null replica collection behavior, simulate refresh exceptions, and cover multi-volume block pools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/ReplicaCachingGetSpaceUsed.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/ReplicaMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/ReplicaMap.java

## Purpose

`ReplicaMap` is the DataNode's block-pool-partitioned in-memory index from block id to `ReplicaInfo`. It is the primary fast lookup structure for finalized, in-progress, provided, and other replica records managed by `FsDatasetImpl`.

## Important APIs, Control Flow, and State

The map is `ConcurrentHashMap<String, LightWeightResizableGSet<Block, ReplicaInfo>>`, with operations protected by a `DataNodeLockManager` or a `NoLockManager` for tests and temporary maps. Public package APIs include `get` by `Block` or block id, `add`, `addAndGet`, `addAll`, `mergeAll`, `remove`, `size`, `replicas`, `initBlockPool`, and `cleanUpBlockPool`. Generation-stamp-sensitive `get/remove` variants verify the stored replica's generation stamp before returning or deleting it.

State is entirely in memory and keyed by block pool. `mergeAll` carefully copies another GSet into a temporary `HashSet` before inserting to avoid iterator corruption or endless loops. `replicas(String)` returns an unsynchronized collection, while `replicas(String, Consumer<Iterator<ReplicaInfo>>)` runs under the lock manager and uses the GSet iterator callback.

## Dependencies, Integration, Risks, and Tests

Dependencies include `Block`, `ReplicaInfo`, `LightWeightResizableGSet`, and the DataNode dataset lock abstractions. It integrates with volume scanning, block reports, replica recovery, provided volume population, and cache/space accounting.

Risks include using read locks around mutating operations in several methods, unsynchronized collection exposure, null block-pool errors, and `addAll` replacing entire block-pool maps without per-pool merging. Tests should cover generation-stamp checks, add-and-get semantics, merge behavior, block-pool init/cleanup, concurrent access under lock manager, and iterator callback safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/ReplicaMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/ReservedSpaceCalculator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/ReservedSpaceCalculator.java

## Purpose

`ReservedSpaceCalculator` encapsulates DataNode policy for reserving local filesystem capacity for non-HDFS use. It supports absolute byte reservation, percentage reservation, and conservative/aggressive combinations of both.

## Important APIs, Control Flow, and State

`Builder` collects `Configuration`, `DF`, `StorageType`, and directory string, then reflectively constructs the configured calculator class from `DFS_DATANODE_DU_RESERVED_CALCULATOR_KEY`. The base class stores those inputs and resolves reservation configuration with specificity order: `key.dir.storageType`, `key.dir`, `key.storageType`, then base key/default. `getReserved()` is implemented by nested classes.

`ReservedSpaceCalculatorAbsolute` returns configured bytes. `ReservedSpaceCalculatorPercentage` returns `(DF.capacity * pct) / 100`. `ReservedSpaceCalculatorConservative` returns the larger of absolute and percentage values. `ReservedSpaceCalculatorAggressive` returns the smaller. The calculator has no persistence; it reads configuration and live filesystem capacity through `DF`.

## Dependencies, Integration, Risks, and Tests

Dependencies include `Configuration`, `DF`, `StorageType`, `StringUtils`, and DFS reserved-space config keys. It is used by `FsVolumeImpl` capacity/available accounting.

Risks include reflection failures wrapped as `IllegalStateException`, raw constructor usage, integer overflow in `total * percentage`, and surprising configuration precedence for per-directory/per-storage keys. Tests should cover each policy, precedence ordering, custom calculator construction, storage-type lowercase keys, and large-capacity percentage arithmetic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/ReservedSpaceCalculator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/VolumeFailureInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/VolumeFailureInfo.java

## Purpose

`VolumeFailureInfo` is an immutable value object describing a failed DataNode storage volume. It records the failed `StorageLocation`, failure timestamp, and estimated lost capacity.

## Important APIs, Control Flow, and State

The constructors allow callers to omit capacity, in which case lost capacity defaults to zero for failures discovered before capacity can be queried. Getters expose `getFailedStorageLocation`, `getFailureDate`, and `getEstimatedCapacityLost`.

There is no control flow beyond construction and getters, and no persistence in this class. Instances are held by dataset/volume-list code and surfaced through metrics/JMX such as failed storage locations, last failure time, and capacity lost.

## Dependencies, Integration, Risks, and Tests

The only non-JDK dependency is `StorageLocation`. Integration points are failure tracking in `FsVolumeList`/dataset metrics and `FSDatasetMBean`.

Risks are low, but callers must use consistent epoch-millisecond timestamps and understand that zero capacity can mean unknown rather than no loss. Tests should cover both constructors and metric aggregation consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/VolumeFailureInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/DataNodeDiskMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/DataNodeDiskMetrics.java

## Purpose

`DataNodeDiskMetrics` periodically detects slow DataNode disks by applying `OutlierDetector` to per-volume metadata, read, and write latency means. It records slow-disk latency by operation and optionally derives a bounded list of slow disks to exclude.

## Important APIs, Control Flow, and State

The constructor reads detection thresholds from configuration, creates `OutlierDetector`, marks the service running, and starts a daemon. The daemon loops while `shouldRun`, obtains `FsVolumeReferences` from the DataNode dataset, collects each volume's `DataNodeVolumeMetrics` means keyed by base URI path, closes references, calls `detectAndUpdateDiskOutliers`, sorts outlier disks by maximum recorded latency, and stores up to `maxSlowDisksToExclude`.

State includes volatile detection thresholds, volatile `diskOutliersStats`, mutable `slowDisksToExclude`, and a test-only `overrideStatus` flag that prevents daemon updates after `addSlowDiskForTesting`. Runtime persistence is absent; slow-disk reports are in-memory observations. `shutdownAndWait` flips `shouldRun`, interrupts the daemon, and joins it.

## Dependencies, Integration, Risks, and Tests

Dependencies include `DataNode`, `FsDatasetSpi`, `FsVolumeSpi`, `DataNodeVolumeMetrics`, `SlowDiskReports.DiskOp`, and `OutlierDetector`. It integrates with DataNode slow-disk reporting and volume exclusion logic.

Risks include stale `slowDisksToExclude` when no current outliers exist, daemon interruption still logging an error during normal shutdown, mutable maps exposed by getter, empty stats loops that immediately continue without sleeping, and test override state suppressing real updates. Tests should cover threshold setters, outlier detection per operation, max exclusion ordering, reference closing on exceptions, shutdown, and manual slow-disk injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/DataNodeDiskMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/DataNodeMetricHelper.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/DataNodeMetricHelper.java

## Purpose

`DataNodeMetricHelper` adapts an `FSDatasetMBean` into Hadoop metrics2 records. It centralizes the gauge/tag population used when the dataset exposes itself as a `MetricsSource`.

## Important APIs, Control Flow, and State

The sole API is static `getMetrics(MetricsCollector, FSDatasetMBean, String)`. It rejects null beans, uses the bean class name as the record name, sets the metrics context, and adds capacity, DFS-used, remaining, storage info, failed volume counts/times/capacity lost, cache usage/capacity, cached block counts, failed cache/uncache counts, last directory scanner finish time, and pending async deletion count.

There is no retained state or persistence. The control flow is a single builder-style chain against the collector, and bean getter `IOException`s propagate to the caller.

## Dependencies, Integration, Risks, and Tests

Dependencies include `MetricsCollector`, `MetricsTag`, `Interns`, and `FSDatasetMBean`. It integrates with `FsDatasetImpl` metrics publication.

Risks include metric-name compatibility, exceptions from bean getters aborting the whole snapshot, and typos/descriptions becoming externally visible metrics contract. Tests should verify null handling, all expected metric names/tags, and propagation of bean exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/DataNodeMetricHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/DataNodeMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/DataNodeMetrics.java

## Purpose

`DataNodeMetrics` is the main Hadoop metrics2 source for DataNode activity. It owns counters, gauges, rates, quantiles, and usage-report helpers for block IO, client locality, RPCs to NameNodes, RAM disk activity, erasure coding, xceiver counts, packet latency, dataset lock timing, and local dataset operations.

## Important APIs, Control Flow, and State

The constructor tags the registry with the session id, creates `DataNodeUsageReportUtil`, and creates interval-specific quantile arrays for packet ACK RTT, flush/fsync, network blocking, packet transfer, RAM_DISK eviction/lazy-persist windows, and read transfer rate. `create(Configuration, String)` registers an instance with the default metrics system and creates JVM metrics. The many `incr...`, `decr...`, `set...`, and `add...` methods update the annotated `MutableCounterLong`, `MutableGauge*`, `MutableRate`, `MutableRatesWithAggregation`, and quantile fields.

State is in metrics objects registered with `DefaultMetricsSystem`; it is not persisted by this class. `getDNUsageReport` snapshots cumulative bytes/time/block counters into a `DataNodeUsageReport`. `shutdown` shuts down the default metrics system. RPC-latency helpers add both generic operation rates and per-NameNode suffix rates when a suffix is supplied.

## Dependencies, Integration, Risks, and Tests

Dependencies include Hadoop metrics2 annotations/libs, `JvmMetrics`, `DFSConfigKeys`, `DataNodeUsageReportUtil`, and `ThreadLocalRandom`. Integration spans nearly every DataNode subsystem: block sender/receiver, BP service actors, cache manager, RAM_DISK lazy persist, EC reconstruction worker, FsDataset local operations, and network/xceiver tracking.

Risks include metric-name compatibility, counters that can diverge from subsystem state if callers miss increments/decrements, global `DefaultMetricsSystem.shutdown()` affecting other registered sources, quantile overhead when many intervals are configured, and using `int` deltas for byte counters in some APIs. Tests should validate registration names, quantile creation, usage report values, gauge increment/decrement balance, per-RPC suffix metrics, and representative subsystem update methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/DataNodeMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/DataNodePeerMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/DataNodePeerMetrics.java

## Purpose

`DataNodePeerMetrics` records downstream packet-send latency by peer DataNode and identifies slow peers using rolling averages and `OutlierDetector`. It supports DataNode slow-peer reporting.

## Important APIs, Control Flow, and State

The constructor reads minimum samples, low threshold, and minimum node count from configuration, creates an `OutlierDetector`, and initializes a `MutableRollingAverages` named `Time`. `create` builds a metrics source name from the DataNode name. `addSendPacketDownstream` records elapsed time for a peer address. `dumpSendPacketDownstreamAvgInfoAsJson` snapshots rolling averages into metrics JSON. `collectThreadLocalStates` flushes thread-local rolling-average state.

`getOutliers` either returns test-injected outlier metrics or obtains aggregate latency stats requiring `minOutlierDetectionSamples` and passes them to `OutlierDetector.getOutlierMetrics`. Setters update both local volatile thresholds and detector thresholds. No state is persisted beyond metrics rolling windows.

## Dependencies, Integration, Risks, and Tests

Dependencies include `MutableRollingAverages`, `MetricsJsonBuilder`, `OutlierDetector`, `OutlierMetrics`, and DFS slow-peer config keys. It integrates with DataNode packet responder / write pipeline reporting.

Risks include caller-provided peer address formatting becoming metric names, thread-local state not being collected before outlier checks, stale test overrides, and threshold tuning producing false positives/negatives. Tests should cover minimum sample filtering, JSON dump format, outlier detection thresholds, setter validation, thread-local collection, and direct test outlier injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/DataNodePeerMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/FSDatasetMBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/FSDatasetMBean.java

## Purpose

`FSDatasetMBean` defines the stable JMX/metrics view of DataNode dataset storage state. It exposes capacity, usage, failure, cache, scanner, and async deletion metrics and extends `MetricsSource`.

## Important APIs, Control Flow, and State

The interface declares getters for block-pool used, total DFS used, capacity, remaining, storage info, failed volume count and locations, last failure date, estimated lost capacity, cache used/capacity, cached and failed cache/uncache block counts, last directory scanner finish time, and pending async deletions. Implementations provide the actual state; this interface has no control flow.

The persistence behavior is indirect: values reflect live dataset state, volume failure records, cache manager counters, and scanner timestamps. Because this is a published MBean-style interface, method names are part of the observable management contract.

## Dependencies, Integration, Risks, and Tests

Dependencies are minimal: `MetricsSource` and `IOException`. Integration is through `FsDatasetImpl` and `DataNodeMetricHelper`.

Risks include incompatible method changes breaking JMX/metrics consumers and expensive implementations blocking metrics collection. Tests should verify implementing classes publish all gauges/tags and maintain expected values through volume failure, cache, scanner, and async deletion events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/FSDatasetMBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/OutlierDetector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/OutlierDetector.java

## Purpose

`OutlierDetector` is a reusable latency outlier detector for DataNode resources such as disks and peer nodes. It applies median absolute deviation with conservative low-threshold and median-multiplier safeguards.

## Important APIs, Control Flow, and State

`getOutliers` returns a simple resource-to-latency map, while `getOutlierMetrics` returns `OutlierMetrics` containing median, MAD, computed upper limit, and actual latency. The detector skips analysis when the resource count is below `minNumResources`. Otherwise it sorts latency values, computes median, computes MAD as median absolute deviation multiplied by `1.4826`, and sets the outlier limit to the maximum of `lowThresholdMs`, `median * 3`, and `median + 3 * mad`. Entries above that limit are flagged.

State consists of volatile `minNumResources` and `lowThresholdMs`, updated by setters. Static helpers `computeMedian` and `computeMad` require non-empty sorted input and throw `IllegalArgumentException` otherwise. There is no persistence.

## Dependencies, Integration, Risks, and Tests

Dependencies include `OutlierMetrics`, Guava `ImmutableMap`, and SLF4J. It is used by `DataNodeDiskMetrics` and `DataNodePeerMetrics`.

Risks include handling NaN/Infinity latencies, requiring callers to provide comparable aggregate metrics, sorting overhead for large maps, and threshold choices that can mask uniformly bad resources. Tests should cover odd/even median, MAD computation, insufficient sample count, low-threshold floor, median-multiplier floor, exact boundary comparisons, and returned `OutlierMetrics` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/OutlierDetector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/DatanodeHttpServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/DatanodeHttpServer.java

## Purpose

`DatanodeHttpServer` starts and owns the DataNode HTTP/HTTPS surface. It runs a small Jetty `HttpServer2` for UI/servlets behind an internal proxy port and Netty front-end listeners that dispatch WebHDFS requests directly or proxy other requests to Jetty.

## Important APIs, Control Flow, and State

The constructor configures Jetty thread counts, admin ACL, SPNEGO host, x-frame settings, servlet/context attributes, the block scanner report servlet, and `DataNodeUGIProvider`. It creates a `confForCreate` with umask `000` for WebHDFS create semantics, starts Netty boss/worker groups, determines HTTP policy, reflectively creates configured filter handlers, and builds HTTP and/or HTTPS `ServerBootstrap` pipelines. HTTP pipelines add request decoder, response encoder, optional filters, `ChunkedWriteHandler`, and `URLDispatcher`. HTTPS additionally installs `SslHandler`.

`start` binds enabled Netty servers, updates the configuration with actual HTTP/HTTPS addresses, and logs endpoints. `close` gracefully shuts down event loops, destroys SSL state, closes any externally supplied JSVC channel, and stops Jetty. `getFilterHandlers` loads classes from configured/default handler keys, invokes static `initializeState(Configuration)`, and constructs handlers using the returned state type. `MapBasedFilterConfig` provides just enough servlet `FilterConfig` for Netty-backed security filters.

## Dependencies, Integration, Risks, and Tests

Dependencies include Netty, Jetty `HttpServer2`, `SSLFactory`, `DFSUtil` HTTP policy, `DataNode`, `BlockScanner.Servlet`, `DataNodeUGIProvider`, and filter handler classes. Integration points are WebHDFS, DataNode web UI, CSRF/host restriction filters, SPNEGO configuration, and privileged external socket binding.

Risks include reflection misconfiguration aborting startup, security filters missing if configuration resolves null, lifecycle leaks on partial constructor failure, external channel bind no-op semantics, SSL initialization failures, and proxy/WebHDFS dispatch depending on URI prefixes. Tests should cover HTTP-only, HTTPS-only, dual policy, external channel, filter initialization, address updates, close cleanup, and WebHDFS/proxy pipeline behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/DatanodeHttpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/HostRestrictingAuthorizationFilterHandler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/HostRestrictingAuthorizationFilterHandler.java

## Purpose

`HostRestrictingAuthorizationFilterHandler` adapts servlet-oriented `HostRestrictingAuthorizationFilter` authorization checks into the DataNode Netty HTTP pipeline. It either forwards allowed requests or sends an error response and closes the connection.

## Important APIs, Control Flow, and State

`initializeState(Configuration)` reads the HDFS host restriction config, builds a `MapBasedFilterConfig`, initializes a reusable filter instance, and returns it for reflective construction by `DatanodeHttpServer`. `channelRead0` calls `handleInteraction` with `NettyHttpInteraction`. That interaction exposes remote address, query string, request URI without query, remote user parsed from `user.name`, method, `proceed`, and `sendError`.

The handler is marked `@Sharable` and holds a stateless initialized filter. `proceed` retains the Netty request before firing it to the next handler; error paths write a `DefaultHttpResponse` with `Connection: close`. There is no persistence.

## Dependencies, Integration, Risks, and Tests

Dependencies include Netty HTTP types, `HostRestrictingAuthorizationFilter`, `UserParam`, `DatanodeHttpServer.MapBasedFilterConfig`, and servlet exceptions. It integrates as an optional security filter in DataNode HTTP/HTTPS pipelines.

Risks include URI parsing returning null query on invalid URIs, request reference-count mistakes, remote user extraction from the first query value only, and filter initialization with blank restrictions potentially allowing more than intended. Tests should cover allowed and denied requests, malformed URI handling, proxy user parsing, response close headers, exception path, and sharable filter reuse across channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/HostRestrictingAuthorizationFilterHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/RestCsrfPreventionFilterHandler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/RestCsrfPreventionFilterHandler.java

## Purpose

`RestCsrfPreventionFilterHandler` adapts Hadoop's `RestCsrfPreventionFilter` to DataNode's Netty WebHDFS/front-end pipeline. It blocks or forwards requests based on configured CSRF rules.

## Important APIs, Control Flow, and State

`initializeState(Configuration)` returns null if WebHDFS REST CSRF protection is disabled; otherwise it extracts `dfs.webhdfs.rest-csrf.*` parameters, initializes a servlet filter through `MapBasedFilterConfig`, and returns it. `channelRead0` delegates to `handleHttpInteraction` if the filter is present or forwards directly if null. The Netty interaction exposes headers, method, `proceed`, and `sendError`.

State is the initialized filter reference, which may be null. The handler is sharable, retains requests before forwarding, and closes connections on error responses or handler exceptions. No state is persisted.

## Dependencies, Integration, Risks, and Tests

Dependencies include Netty, `RestCsrfPreventionFilter`, WebHDFS CSRF config keys, and `DatanodeHttpServer.MapBasedFilterConfig`. It integrates with `DatanodeHttpServer.getFilterHandlers`.

Risks include disabled/null filter accidentally bypassing protection, reference-count leaks, filter init failure aborting startup, and response status message construction exposing arbitrary filter messages. Tests should cover disabled mode pass-through, enabled allowed/blocked requests, configured custom headers/methods, exception handling, and close semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/RestCsrfPreventionFilterHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/SimpleHttpProxyHandler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/SimpleHttpProxyHandler.java

## Purpose

`SimpleHttpProxyHandler` is a small Netty session-layer proxy from the external DataNode HTTP listener to the internal Jetty info server. It handles non-WebHDFS requests and rewrites HTTP redirect locations to HTTPS when the external listener is secure.

## Important APIs, Control Flow, and State

`channelRead0` stores the request URI, creates a client `Bootstrap` on the same event loop, connects to the Jetty host, and on success removes the inbound `HttpResponseEncoder`, copies headers into a new full request, sets `Connection: close`, and writes it to the proxied channel. `Forwarder` writes proxied server responses back to the client and reads the next response chunk only after successful flush. In secure mode, the outbound pipeline decodes HTTP responses, runs `SslRedirectRewriter` to replace leading `http://` `Location` values with `https://`, and adds a response encoder to the client pipeline.

State includes the current URI and proxied channel. `channelInactive` and `exceptionCaught` close the proxied channel. No data is persisted, and the handler assumes upper layers restrict malicious requests and that proxied responses are modest.

## Dependencies, Integration, Risks, and Tests

Dependencies include Netty bootstrap/channel/HTTP codecs and `DatanodeHttpServer.LOG`. It integrates with `URLDispatcher` as the fallback path for UI and servlet requests.

Risks include request body loss because a new empty `DefaultFullHttpRequest` is created, pipeline encoder removal/addition ordering, redirect rewriting only for lowercase `http://` prefix, proxy buffering/backpressure assumptions, and connection-close-only behavior. Tests should cover successful proxying, connection failure response, secure redirect rewriting, client/proxy channel close interactions, and non-WebHDFS URI dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/SimpleHttpProxyHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/URLDispatcher.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/URLDispatcher.java

## Purpose

`URLDispatcher` is the one-request Netty dispatcher that chooses between the in-process WebHDFS handler and the internal Jetty proxy for DataNode HTTP requests.

## Important APIs, Control Flow, and State

`channelRead0` checks whether the request URI starts with `WebHdfsHandler.WEBHDFS_PREFIX`. WebHDFS requests replace the dispatcher in the pipeline with a new `WebHdfsHandler(conf, confForCreate)` and immediately delegate the request. All other requests replace it with `SimpleHttpProxyHandler(proxyHost, isSecure)` and delegate. Constructor state is the Jetty proxy address, normal/create configurations, and secure flag.

There is no persistence. The handler is intentionally replaced after the first request so the rest of the connection is handled by the selected protocol path.

## Dependencies, Integration, Risks, and Tests

Dependencies include Netty pipeline APIs, `Configuration`, `WebHdfsHandler`, and `SimpleHttpProxyHandler`. It integrates directly into `DatanodeHttpServer` pipelines after filters and chunked write support.

Risks include simple prefix matching accepting unexpected paths, handler-construction exceptions closing the request, and mixed-protocol keepalive connections being pinned to the first selected handler. Tests should cover WebHDFS prefix dispatch, proxy fallback, secure flag propagation, and pipeline replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/URLDispatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/package-info.java

## Purpose

This package-info file provides package documentation for `org.apache.hadoop.hdfs.server.datanode.web`, the DataNode HTTP classes package.

## Important APIs, Control Flow, and State

There are no runtime APIs, classes, fields, or control flow. The file contains only the Apache license header, a short Javadoc package description, and the package declaration.

There is no state or persistence. Its effect is limited to generated Javadocs and package-level source organization.

## Dependencies, Integration, Risks, and Tests

The file has no dependencies beyond Java package documentation syntax. It integrates with documentation generation for DataNode web classes.

Risks are limited to stale or misleading package documentation. Test signal is compilation/Javadoc generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/DataNodeUGIProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/DataNodeUGIProvider.java

## Purpose

`DataNodeUGIProvider` builds and caches `UserGroupInformation` instances for DataNode WebHDFS requests. The DataNode uses these UGIs to execute DFSClient operations, while NameNode-side operations still perform authoritative authentication/authorization.

## Important APIs, Control Flow, and State

`init(Configuration)` creates a static Guava cache expiring entries after configured access time. `ugi()` first parses a delegation token. In secure mode with a token, it caches by token cache key and builds a token UGI by decoding `DelegationTokenIdentifier`, obtaining its user, and adding the token. Otherwise it builds a non-token UGI from `user.name` or the configured default web user, optionally wraps it as a proxy user from `doas`, and caches by `{remoteUser}` or `{remoteUser}:{doAs}`. `clearCache` clears the decoded delegation token identifier cache in secure test scenarios.

State is the static UGI cache and the per-request `ParameterParser`. There is no disk persistence, but cached UGIs can retain tokens and proxy-user identity until expiration.

## Dependencies, Integration, Risks, and Tests

Dependencies include `ParameterParser`, `JspHelper`, `UserGroupInformation`, delegation tokens, Guava cache, and DFS WebHDFS UGI cache config. It integrates with `WebHdfsHandler.channelRead0` before executing request operations under `ugi.doAs`.

Risks include static cache lifetime across DataNode reconfiguration/tests, cache key collisions if token/user representations change, proxy-user authorization being deferred, and insecure NameNode access to secure DataNode data being intentionally allowed when no token is present. Tests should cover secure token UGI, insecure/default web user UGI, proxy user creation, cache reuse/expiration, username validation, and logical URI token service handling through `ParameterParser`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/DataNodeUGIProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/ExceptionHandler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/ExceptionHandler.java

## Purpose

`ExceptionHandler` converts exceptions thrown by the Netty WebHDFS handlers into JSON HTTP responses compatible with WebHDFS clients.

## Important APIs, Control Flow, and State

`exceptionCaught(Throwable)` normalizes non-`Exception` throwables, traces debug details, converts Jersey `ParamException` into an `IllegalArgumentException`, unwraps `ContainerException`, selected `SecurityException` causes, and Hadoop `RemoteException`, maps exception classes to HTTP statuses, serializes the exception via `JsonUtil.toJsonString`, and returns a `DefaultFullHttpResponse` with JSON content type and length.

`toCause` has special handling for `SecurityException` caused by invalid delegation tokens whose cause is `StandbyException`, returning the standby exception so HA standby errors are not masked. There is no retained state or persistence.

## Dependencies, Integration, Risks, and Tests

Dependencies include Netty response buffers, Jersey exceptions, Hadoop `RemoteException`, `StandbyException`, `AuthorizationException`, token `InvalidToken`, and `JsonUtil`. It integrates with `WebHdfsHandler.exceptionCaught` and `HdfsWriter.exceptionCaught`.

Risks include mapping all `IOException` to `FORBIDDEN`, exposing exception messages in JSON, losing cause details during normalization, and status choices diverging from WebHDFS servlet behavior. Tests should cover parameter errors, file-not-found, authorization/security errors, remote exception unwrap, invalid-token standby conversion, unsupported operations, and unknown exception 500 responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/ExceptionHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/HdfsWriter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/HdfsWriter.java

## Purpose

`HdfsWriter` streams HTTP request body chunks into a DFSClient output stream for WebHDFS CREATE and APPEND operations, then emits the prebuilt success response.

## Important APIs, Control Flow, and State

The handler stores a `DFSClient`, target `OutputStream`, and response. `channelRead0` writes each `HttpContent` buffer into the output stream. When it sees `LastHttpContent`, it closes the stream and client through `releaseDfsResourcesAndThrow`, sets `Connection: close`, writes the success response, and closes the channel. `channelInactive` closes resources if the client disconnects. `exceptionCaught` closes resources, converts the error through `ExceptionHandler`, writes a close response, and logs debug details.

State is per upload request: open DFSClient/output stream until completion or failure. The persisted result is the HDFS file data written by DFSClient; cleanup behavior after partial writes depends on DFSClient/HDFS semantics.

## Dependencies, Integration, Risks, and Tests

Dependencies include Netty `HttpContent`, `DFSClient`, `IOUtils`, and `ExceptionHandler`. It is installed by `WebHdfsHandler.onCreate` and `onAppend` after sending `100 Continue`.

Risks include blocking stream writes on Netty event-loop threads, partial HDFS files after client disconnect, exceptions during close being converted after data was written, and not explicitly flushing before success response beyond Netty flush callbacks. Tests should cover chunked upload, append, close on last chunk, client disconnect cleanup, output stream failure, and success/error response headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/HdfsWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/ParameterParser.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/ParameterParser.java

## Purpose

`ParameterParser` wraps Netty `QueryStringDecoder` output and converts WebHDFS request parameters into typed Hadoop resource parameter objects. It centralizes path extraction, operation lookup, create/open options, delegation token decoding, and NameNode identity handling for DataNode WebHDFS.

## Important APIs, Control Flow, and State

The constructor strips the WebHDFS prefix from the decoded path and stores the parameter map. Methods parse `op`, `offset`, `length`, NameNode address, `doas`, `user.name`, buffer size, block size, replication, permissions, overwrite, noredirect, create-parent, and create flags. `delegationToken` decodes a URL token, builds `hdfs://namenodeId`, and sets the token service to the logical HA service or concrete NameNode address as appropriate. `createFlag` decodes the createflag parameter with UTF-8 `QueryStringDecoder` to preserve comma/list parsing.

State is per request and immutable after construction. There is no persistence. The private `param` helper returns only the first value for each key, matching common WebHDFS parameter semantics. `decodeHexNibble` is a private helper currently unused in this file.

## Dependencies, Integration, Risks, and Tests

Dependencies include WebHDFS parameter classes, `HAUtilClient`, `SecurityUtil`, `Token`, `DelegationTokenIdentifier`, and `Configuration`. It integrates with `WebHdfsHandler` and `DataNodeUGIProvider`.

Risks include first-value-only handling, invalid parameter exceptions bubbling to `ExceptionHandler`, token service misassignment for HA logical URIs, path substring assumptions if prefix validation is bypassed, and unused helper drift. Tests should cover every parsed parameter, missing/default values, create flag/overwrite interaction, logical and physical delegation token service, invalid parameter conversion, and URL-encoded create flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/ParameterParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/WebHdfsHandler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/WebHdfsHandler.java

## Purpose

`WebHdfsHandler` is the Netty implementation of the DataNode side of WebHDFS data operations. It handles CREATE, APPEND, OPEN, GETFILECHECKSUM, and CORS preflight for CREATE by building a request UGI, creating DFSClients to the requested NameNode, and streaming data through Netty.

## Important APIs, Control Flow, and State

`channelRead0` validates the `/webhdfs/v1` prefix, parses parameters, obtains a UGI from `DataNodeUGIProvider`, records the HDFS path, injects a delegation token into the UGI when secure, and runs `handle` inside `ugi.doAs` with request logging in a finally block. `handle` dispatches by HTTP method plus `op`. `onCreate` sends `100 Continue`, resolves permission/unmasked permission, create flags, replication, block size, and create-parent, creates a DFSClient with `confForCreate`, opens an HDFS output stream, prepares `201 Created` with `Location` and CORS headers, and replaces itself with `HdfsWriter`. `onAppend` is similar but opens append and returns `200 OK`.

`onOpen` creates a DFSClient input stream, seeks to offset, computes visible content length bounded by optional length, sets octet-stream/CORS/close headers, and writes a `ChunkedStream` that closes the DFSClient when complete. `onGetFileChecksum` gets the checksum, serializes it as JSON, and closes. `allowCORSOnCreate` handles OPTIONS. State is request-local fields (`path`, `params`, `ugi`, `resp`), and persistence is the HDFS data/checksum state accessed through DFSClient.

## Dependencies, Integration, Risks, and Tests

Dependencies include Netty HTTP/streaming, `DFSClient`, WebHDFS parameter enums, HDFS security tokens, UGI, `JsonUtil`, `LimitInputStream`, and WebHDFS client config patterns. It integrates with `URLDispatcher`, `HdfsWriter`, `ExceptionHandler`, and the NameNode/DataNode WebHDFS redirect flow.

Risks include blocking DFSClient operations on Netty event-loop threads, response code logging defaulting to 500 if failure occurs before `resp`, unrestricted CORS headers, careful resource closing for open/checksum paths, create umask semantics via `confForCreate`, token injection duplication, and invalid operation mapping. Tests should cover each supported operation, method/op mismatch, secure and insecure UGI paths, create flags and permissions, ranged open lengths, checksum JSON, upload failure cleanup, CORS preflight, and request logging status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/WebHdfsHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/DiskBalancerConstants.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/DiskBalancerConstants.java

## Purpose

`DiskBalancerConstants` holds shared constants for HDFS disk balancer plan handling and per-volume settings.

## Important APIs, Control Flow, and State

The class defines `DISKBALANCER_BANDWIDTH`, `DISKBALANCER_VOLUME_NAME`, `DISKBALANCER_MIN_VERSION`, and `DISKBALANCER_MAX_VERSION`. The private constructor prevents instantiation. There is no runtime control flow or mutable state.

The version constants define the accepted plan-file version range, currently only version 1. The string constants are used as stable keys for disk-balancer attributes/configuration.

## Dependencies, Integration, Risks, and Tests

Dependencies are only Hadoop classification annotations. Integration points are disk balancer planning, command, and DataNode RPC validation code that relies on version and key names.

Risks include version constants drifting from parser/RPC support and string-key changes breaking compatibility. Tests should cover plan-version validation and any code that reads/writes these key names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/DiskBalancerConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/DiskBalancerException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/DiskBalancerException.java

## Purpose

`DiskBalancerException` is the typed IOException used by disk balancer RPC and command code. It carries a structured `Result` enum in addition to the normal exception message/cause.

## Important APIs, Control Flow, and State

`Result` enumerates disk-balancer failure categories such as not enabled, invalid plan/version/hash, old plan, DataNode mismatch, malformed plan, plan already in progress, invalid volume/move/node, internal error, no such plan, unknown key, non-regular DataNode status, and invalid host file path. Constructors support message+result, message+cause+result, and cause+result. `getResult` exposes the enum.

State is immutable per exception: the inherited IOException state plus final `result`. There is no persistence, but result names can cross RPC boundaries and appear in CLI/log output.

## Dependencies, Integration, Risks, and Tests

Dependencies are JDK `IOException`. The exception integrates with `ClientDatanodeProtocol`, DataNode disk balancer service, and CLI commands such as cancel/query/execute.

Risks include adding/removing enum values without updating clients, logs, or protobuf/RPC mapping, and commands relying on result text. Tests should verify constructors preserve message/cause/result and that command/RPC paths propagate meaningful result codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/DiskBalancerException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/CancelCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/CancelCommand.java

## Purpose

`CancelCommand` implements `hdfs diskbalancer -cancel`. It cancels an active disk-balancer plan either from a plan file, whose node address and hash can be derived, or from an explicit plan ID/hash plus `-node` address.

## Important APIs, Control Flow, and State

The constructor registers valid `-cancel` and `-node` options. `execute` verifies the command, then branches: with `-node`, it treats the cancel argument as the plan hash and calls `cancelPlanUsingHash`; without `-node`, it treats the cancel argument as a plan file, reads it as UTF-8 through `open`, and calls `cancelPlan`. `cancelPlan` parses `NodePlan` JSON, builds `host:port`, obtains a `ClientDatanodeProtocol` proxy, computes the SHA-1 hex hash of the full plan data, and calls `cancelDiskBalancePlan`. `cancelPlanUsingHash` obtains the proxy for the provided address and calls the same RPC.

The command has no persistent state beyond the inherited command configuration and any filesystem reads. It logs `DiskBalancerException` result/message and rethrows so CLI exit handling can report failure. `printHelp` documents both cancellation modes.

## Dependencies, Integration, Risks, and Tests

Dependencies include Commons CLI, Commons Codec SHA-1, Commons IO, `FSDataInputStream`, `NodePlan`, `ClientDatanodeProtocol`, `DiskBalancerException`, and `DiskBalancerCLI`. It integrates with plan execution/query commands because users can cancel by the query-reported plan ID/hash.

Risks include help text mentioning plan ID while implementation accepts whatever string is passed as hash, comment drift saying SHA-512 while code uses SHA-1, plan-file parsing failure, stale node address in plan files, and hash calculation depending on exact plan file bytes. Tests should cover cancel by file, cancel by node/hash, missing/invalid options, malformed plan JSON, RPC `DiskBalancerException` propagation, and hash consistency with execute command.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/CancelCommand.java -->
