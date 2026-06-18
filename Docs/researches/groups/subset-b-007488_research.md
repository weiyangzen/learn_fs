# subset-b-007488 Research

Grouped research report for the requested Hadoop HDFS DataNode files. Each file section preserves the original source path in its title and is bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataNode.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataNode.java

Purpose: implements the HDFS DataNode daemon. It owns local block storage, talks to NameNodes through block-pool offer services, serves client and peer DataNode data-transfer traffic, exposes administrative RPC/JMX surfaces, and coordinates scanners, metrics, disk balancing, security, short-circuit reads, and runtime reconfiguration.

Important APIs and types: `DataNode` extends `ReconfigurableBase` and implements `InterDatanodeProtocol`, `ClientDatanodeProtocol`, `DataNodeMXBean`, and `ReconfigurationProtocol`. Key fields are `DataStorage storage`, `FsDatasetSpi data`, `BlockPoolManager blockPoolManager`, `DataXceiverServer xserver`, `DataNodeMetrics metrics`, `DataNodePeerMetrics peerMetrics`, `DataNodeDiskMetrics diskMetrics`, `BlockScanner`, `DirectoryScanner`, `DiskBalancer`, `BlockPoolTokenSecretManager`, and `DataSetLockManager`. Static entry points include `instantiateDataNode`, `createDataNode`, `makeInstance`, `secureMain`, `main`, `getStorageLocations`, and argument/startup-option parsing helpers. Runtime APIs cover volume refresh/removal, block-pool initialization, block transfer, short-circuit file descriptor requests, replica recovery, disk error handling, NameNode reports, and disk-balancer management.

Control flow: construction initializes configuration-derived policy, lock manager, block scanner, transfer throttlers, host identity, and then calls `startDataNode`. `startDataNode` validates secure mode and volume-failure tolerance, creates `DataStorage`, registers the MXBean, starts the data-transfer listener and HTTP server, initializes pause monitor, block token manager, IPC server, metrics, EC/recovery workers, and `BlockPoolManager`, then refreshes NameNode connections. A block pool handshake calls `initBlockPool`, which validates cluster ID, registers the `BPOfferService`, calls `initStorage`, adds the block pool to the dataset, runs disk checks, and starts scanners/balancer. `runDatanodeDaemon` starts the data-transfer daemon, optional domain-socket server, IPC server, plugins, and records `startTime`. `join` waits while `shouldRun` is true and block-pool services remain alive. Shutdown stops metrics logging/plugins, sends out-of-band restart messages when needed, kills transfer servers, stops scanners/balancer/HTTP/checkers/pause monitor/reconfiguration, waits for transfer threads, stops IPC late, shuts down EC/block-pool/storage/dataset/metrics/MBean/short-circuit registry, closes tracing, and runs `dataSetLockManager.lockLeakCheck`.

Runtime reconfiguration: `RECONFIGURABLE_PROPERTIES` supports data directories, balancer concurrency, block/cache report timings, xceiver limits and throttles, peer/disk outlier settings, DFS usage settings, disk balancer settings, and slow I/O thresholds. `reconfigurePropertyImpl` dispatches to specialized helpers. Data-dir refresh parses changed volumes, validates storage-type changes and same-disk tiering conflicts, concurrently adds new volumes through the dataset, removes deactivated volumes from `FsDatasetSpi` and `DataStorage`, rewrites effective `dfs.datanode.data.dir`, and then triggers a full block report.

State and persistence: persistent identity and layout state live in `DataStorage` VERSION files and block-pool slice storage. `checkDatanodeUuid` generates and writes a UUID if storage was freshly formatted. Runtime state includes the volatile `shouldRun`/`shutdownForUpgrade`, xmit counters, NameNode/block-pool registrations, token secret managers, transfer throttlers, disk/peer metrics caches, scanner state, and the effective data-dir configuration. Disk failure handling removes failed volumes, updates dataset/storage, reports `DISK_ERROR` or `FATAL_DISK_ERROR` to every NameNode, and either schedules a block report or stops the daemon.

Dependencies and integration points: integrates with NameNode protocols through `BPOfferService`, `BPServiceActor`, `DatanodeProtocolClientSideTranslatorPB`, and lifeline clients; with clients and peer DataNodes through `DataTransferProtocol`, `DataXceiverServer`, `BlockSender`, SASL, block tokens, and optional domain sockets; with on-disk storage through `DataStorage`, `FsDatasetSpi`, `StorageLocationChecker`, and `DatasetVolumeChecker`; with observability through JMX, Hadoop metrics, slow peer/disk metrics, and metrics logging; and with administration through `ClientDatanodeProtocol`, `ReconfigurationProtocol`, disk balancer RPCs, and service plugins.

Risks: the class is a high-concurrency lifecycle hub, so shutdown order, block-pool initialization order, and volume refresh/removal have large blast radius. Several admin paths are destructive or disruptive (`deleteBlockPool`, volume removal, disk balancer, shutdown, writer eviction) and rely on `checkSuperuserPrivilege`. Reconfiguration can partially add/remove volumes before surfacing an aggregated error. Security depends on consistent block-token configuration across all block pools and either privileged ports or SASL/HTTPS in secure mode. Short-circuit reads depend on domain socket/native support and correct access-token/local-path authorization. Transfer recovery and replication report local corruption differently depending on exception type and scanner state, so regressions can either hide corruption or over-report bad blocks.

Test signals: many methods are marked `@VisibleForTesting`, including constructors, volume parsing, transfer, storage access, scanner access, disk-error handling, startup factories, and metrics timers. Fault-injection hooks are called for missing registration. Good regression coverage should exercise secure/insecure startup, block-pool registration, UUID persistence, volume hotswap and failed-volume removal, token validation, short-circuit reads, pipeline recovery transfer, block-report triggering, disk balancer RPC authorization, and shutdown-for-upgrade behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataNode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataNodeFaultInjector.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataNodeFaultInjector.java

Purpose: provides a test-only singleton hook surface for injecting failures, delays, and observations into DataNode, data-transfer, block-report, directory-scanner, and erasure-coding paths. Production behavior is intentionally no-op.

Important APIs and functions: `get()` returns the global injector and `set(DataNodeFaultInjector)` replaces it for tests. Hook methods include data-transfer write/flush and ack hooks (`writeBlockAfterFlush`, `stopSendingPacketDownstream`, `delaySendingAckToUpstream`, `delayAckLastPacket`, `delayWriteToDisk`, `delayWriteToOsCache`), heartbeat/report hooks (`dropHeartbeatPacket`, `startOfferService`, `endOfferService`, `blockUtilSendFullBlockReport`, `noRegistration`), pipeline/failure hooks (`failMirrorConnection`, `failPipeline`, `throwTooManyOpenFiles`), erasure-coding reconstruction hooks (`stripedBlockReconstruction`, `stripedBlockWriterInit`, `stripedBlockChecksumReconstruction`, `delayBlockReader`, `badDecoding`), and scanner/dataset timing hooks (`delayDeleteReplica`, `delayDiffRecord`, `delayGetMetaDataInputStream`, `waitUntilStorageRemoved`).

Control flow: callers in `BlockReceiver`, `DataXceiver`, `BPServiceActor`, `BPOfferService`, `BlockSender`, EC reconstructors/readers/writers, `DirectoryScanner`, and dataset classes synchronously invoke `DataNodeFaultInjector.get()` at selected fault boundaries. Unless a test has replaced the singleton, the method returns normally, returns `false`, or does nothing. Tests subclass or override methods to throw checked exceptions, sleep, mutate buffers, drop packets, or record timing.

State and persistence: the only state is the static process-wide `instance`; there is no persistence. Because the singleton is mutable and global, tests must restore it to the default injector to avoid cross-test contamination.

Dependencies and integration points: depends on DataNode-adjacent types such as `ReplicaInPipeline`, `DirectoryScanner`, and `ByteBuffer`. It is annotated `@VisibleForTesting` and `@InterfaceAudience.Private`, signaling that production code may call it but external users should not depend on it.

Risks: global mutable fault state can make parallel tests flaky if not reset. Hook placement affects production hot paths, so adding blocking or allocation-heavy default behavior would be dangerous. Hook methods that throw checked exceptions must match caller expectations; changing a no-op hook to throw in production would alter core write/read/report semantics.

Test signals: this file is itself test infrastructure. Useful tests are the downstream tests that install custom injectors to simulate packet drops, slow acks, short-circuit response errors, EC decode corruption, stale directory-scanner diffs, too many open files, or missing DataNode registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataNodeFaultInjector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataNodeLayoutSubLockStrategy.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataNodeLayoutSubLockStrategy.java

Purpose: implements `DataSetSubLockStrategy` using the DataNode block-ID-based directory layout. It maps a block ID to the subdirectory suffix that should guard that block in the dataset lock hierarchy.

Important APIs and functions: `blockIdToSubLock(long blockid)` delegates to `DatanodeUtil.idToBlockDirSuffix(blockid)`. `getAllSubLockNames()` delegates to `DatanodeUtil.getAllSubDirNameForDataSetLock()`.

Control flow: callers provide a block ID when they need a directory-level dataset sub-lock. The strategy computes the same 32-by-32 layout suffix used by on-disk block placement, allowing lock partitioning to align with actual finalized block directories. The all-names method returns the complete set of subdirectory lock names needed to pre-create or iterate all directory-level locks.

State and persistence: stateless. It has no fields and persists nothing. Its correctness is tied to the deterministic `DatanodeUtil` block directory mapping and the DataNode layout version that uses block-ID-based directories.

Dependencies and integration points: implements `DataSetSubLockStrategy` and integrates with lock managers or dataset code that need to convert block IDs into lock-resource names. It depends on `DatanodeUtil`, which is also used by storage layout code, so it avoids divergent lock names.

Risks: if `DatanodeUtil` layout mapping changes without a corresponding migration or lock strategy update, directory-level locking could protect the wrong partition. Returning all names must remain consistent with `blockIdToSubLock`; otherwise pre-created locks can miss active block directories.

Test signals: targeted tests should compare representative block IDs, boundary IDs, and the complete name list against the actual DataNode directory layout and `DataStorage` block-ID layout upgrade output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataNodeLayoutSubLockStrategy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataNodeLayoutVersion.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataNodeLayoutVersion.java

Purpose: defines the DataNode-specific layout version feature matrix and current DataNode layout version. It layers DataNode storage features on top of the shared HDFS `LayoutVersion` features.

Important APIs and types: `FEATURES` maps layout versions to sorted feature sets. `getCurrentLayoutVersion()` returns the current DataNode layout version derived from the enum. `setCurrentLayoutVersionForTesting(int)` overrides it for rolling-upgrade tests. `getFeatures(int)` and `supports(LayoutFeature, int)` query the matrix. The nested `Feature` enum implements `LayoutFeature` and currently defines `FIRST_LAYOUT`, `BLOCKID_BASED_LAYOUT`, and `BLOCKID_BASED_LAYOUT_32_by_32`.

Control flow: static initialization first loads common `LayoutVersion.Feature` values into `FEATURES`, then overlays DataNode-specific features. The current layout version is computed from `Feature.values()`. Storage code calls `supports` to decide how to parse VERSION files, whether federation or UUID features are present, whether legacy RBW/detach layouts apply, and whether block-ID directory upgrades are required.

State and persistence: the class itself only holds in-memory static metadata. Its values directly control persistent storage transitions in `DataStorage`, including VERSION file layout, upgrade checks, rollback compatibility, and hard-link migration from old layouts to the 32-by-32 block-ID-based directory tree.

Dependencies and integration points: depends on `org.apache.hadoop.hdfs.protocol.LayoutVersion`, `FeatureInfo`, and `LayoutFeature`. `DataStorage` calls `getCurrentLayoutVersion` during format/upgrade, `supports` during property read/write and layout transitions, and references `Feature.BLOCKID_BASED_LAYOUT_32_by_32` when upgrading finalized block directories.

Risks: layout version mistakes are persistent and hard to recover from. Adding a new feature with an incorrect ancestor, reserved flag, or version number can make upgrades/rollbacks reject valid disks or accept incompatible disks. The testing override is package-private but static; tests must restore it after use.

Test signals: storage upgrade, rollback, rolling-upgrade, and layout-version matrix tests should verify `supports` across old and current versions, validate current layout version expectations, and exercise DataStorage transitions for pre-federation, federation, UUID, and block-ID-layout cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataNodeLayoutVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataNodeMXBean.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataNodeMXBean.java

Purpose: declares the JMX management interface for DataNode observability. It is intended for access through JMX rather than user implementation.

Important APIs: version and endpoint methods include `getVersion`, `getSoftwareVersion`, `getRpcPort`, `getHttpPort`, and `getDataPort`. Topology and identity methods include `getNamenodeAddresses`, `getDatanodeHostname`, `getBPServiceActorInfo`, and `getClusterId`. Storage and activity methods include `getVolumeInfo`, `getXceiverCount`, `getActiveTransferThreadCount`, `getXmitsInProgress`, and `getDNStartedTimeInMillis`. Health and diagnostics methods include `getDatanodeNetworkCounts`, `getDiskBalancerStatus`, `getSendPacketDownstreamAvgInfo`, `getSlowDisks`, and `isSecurityEnabled`.

Control flow: `DataNode.registerMXBean` registers the running DataNode instance under the `DataNode:DataNodeInfo` MBean name. JMX clients invoke this interface, and the implementation serializes several complex values as JSON strings. The interface has no logic, but it fixes the public management contract implemented in `DataNode`.

State and persistence: no local state or persistence. It exposes live process state from DataNode, metrics objects, block-pool service actors, disk balancer, dataset volume maps, peer metrics, disk metrics, and security state.

Dependencies and integration points: annotated `@InterfaceAudience.Private` and `@InterfaceStability.Stable`, so it is internal but expected to remain stable for Hadoop management tooling. It returns Java `Map` for network counts and strings for JSON-formatted details to keep the JMX surface simple.

Risks: changing method names or return types breaks JMX clients and monitoring dashboards. JSON string formats are documented only by implementations/comments, so consumers may depend on de facto shapes. Implementations must tolerate partially initialized DataNodes; for example `getVolumeInfo` returns an empty string before storage is initialized.

Test signals: tests should verify MBean registration/unregistration, non-null/empty behavior before and after storage initialization, JSON parseability for addresses/actor/volume/disk-balancer/slow-disk outputs, and metric counter consistency for xceivers and transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataNodeMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataSetLockManager.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataSetLockManager.java

Purpose: manages hierarchical read/write locks for `FsDatasetImpl`-style DataNode dataset operations. Locks are organized by block pool, volume, and directory/subdirectory, with optional tracing for leak diagnostics and metrics for lock acquisition latency.

Important APIs and types: implements `DataNodeLockManager<AutoCloseDataSetLock>`. Public methods are `readLock`, `writeLock`, `addLock`, `removeLock`, `hook`, `lockLeakCheck`, and `getLastException`. The nested `LockMap` stores `AutoCloseDataSetLock` wrappers for read/write sides of `ReentrantReadWriteLock`. The nested `TrackLog` records per-thread lock acquisition stack traces and counts when tracing is enabled. `generateLockName` builds resource keys from `LockLevel.BLOCK_POOl`, `VOLUME`, and `DIR`.

Control flow: `readLock` and `writeLock` acquire the requested level and attach parent locks to enforce hierarchical close/unlock behavior. A volume lock takes a block-pool read lock as parent; a directory lock takes a block-pool read lock, then a volume read lock, then the requested directory lock. Missing locks are lazily created with a warning, which is tolerated during DataNode restart. Acquisition records tracing data and updates DataNode metrics (`addAcquireDataSetReadLock`/`addAcquireDataSetWriteLock`). `addLock` pre-creates parent and child locks as needed. `removeLock` acquires the write lock for the resource before removing its lock entry. `hook` is invoked by `AutoCloseDataSetLock` on unlock to decrement tracing counters.

State and persistence: all state is in-memory. `lockMap` holds named lock wrappers, `threadCountMap` holds trace stacks by thread-name-plus-id, `isFair` is configured from `dfs.datanode.lock.fair`, `openLockTrace` from the lock-manager trace setting, and `lastException` records leak-check failures. There is no persistence, but lock state protects persistent dataset and block files.

Dependencies and integration points: depends on Hadoop `DataNodeLockManager.LockLevel`, `AutoCloseDataSetLock`, `DFSConfigKeys`, `Time`, DataNode metrics, and Java `ReentrantReadWriteLock`. `DataNode.transferReplicaForPipelineRecovery` demonstrates block-pool read locking around stored-block state inspection; dataset implementations can use finer volume/dir locks.

Risks: lock-name generation concatenates resource strings without separators, so ambiguous resource names would collide if upstream resource names are not naturally delimited. `LockLevel.BLOCK_POOl` appears with a lowercase `l` typo inherited from the enum name, so callers must use the exact enum. Lazy lock creation masks missing lifecycle calls and can hide bugs. `TrackLog.showLockMessage` pops and empties stack traces, making leak-check output destructive. `removeLock` removes a lock while holding its wrapper; callers must ensure no future users race on the removed resource.

Test signals: useful tests should cover null-resource rejection, resource-count/level mismatch errors, parent lock ordering, read/write latency metric increments, trace `hook` decrement behavior, leak detection, fairness configuration, lazy creation warnings, and add/remove behavior across block-pool, volume, and directory levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataSetLockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataSetSubLockStrategy.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataSetSubLockStrategy.java

Purpose: defines the strategy interface for mapping a block ID to a dataset sub-lock name and for enumerating all possible sub-lock names.

Important APIs: `blockIdToSubLock(long blockid)` returns the lock-resource name for a block. `getAllSubLockNames()` returns every sub-lock name supported by the strategy, enabling preallocation or bulk lock management.

Control flow: callers choose an implementation based on the storage layout, then call `blockIdToSubLock` before acquiring a directory-level dataset lock. Implementations such as `DataNodeLayoutSubLockStrategy` keep the mapping aligned with actual DataNode block directories.

State and persistence: the interface has no state. Implementations may be stateless. The returned names indirectly guard persistent block files by determining lock partitioning.

Dependencies and integration points: depends only on `java.util.List`. It is part of the DataNode dataset locking layer and complements `DataSetLockManager`, which operates on concrete lock-resource names.

Risks: the interface does not specify uniqueness, ordering, immutability, or whether all names must include names returned by `blockIdToSubLock`; implementations must enforce those invariants themselves. A bad mapping can serialize too much work or, worse, permit concurrent conflicting writes to the same on-disk directory.

Test signals: interface-level tests should be implementation contract tests: deterministic mapping, complete all-name enumeration, no null/empty names, and consistency with on-disk layout helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataSetSubLockStrategy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataStorage.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataStorage.java

Purpose: manages DataNode storage metadata, VERSION files, storage UUIDs, block-pool slice storage, volume add/remove, formatting, upgrade, rollback, finalization, rolling-upgrade trash, and hard-link migration of block files across layout versions.

Important APIs and types: extends `Storage` for `NodeType.DATA_NODE`. Constants define DataNode directories such as `finalized`, `rbw`, `lazypersist`, `tmp`, `detach`, and `subdir`. Core state includes `datanodeUuid`, `trashEnabledBpids`, and synchronized `bpStorageMap`. Public/package methods include `getBPStorage`, `createStorageID`, `enableTrash`, `clearTrash`, `trashEnabled`, rolling-upgrade marker methods, `getTrashDirectoryForReplica`, `prepareVolume`, `addStorageLocations`, `removeVolumes`, `recoverTransitionRead`, `format`, `readProperties`, `doRollback`, `doFinalize`, `finalizeUpgrade`, `getBlockPoolSliceStorage`, and `removeBlockPoolStorage`. `VolumeBuilder` stages hot-added volume metadata before committing it to active storage.

Control flow: normal startup calls `recoverTransitionRead`, which uses `addStorageLocations`. DataNode-level directories are first analyzed with `StorageDirectory.analyzeStorage`; missing directories fail, unformatted directories are formatted, recoverable states run `doRecover`, and `doTransition` handles rollback, regular startup, or upgrade. Successfully loaded DataNode directories are then used to load block-pool slice storage through `BlockPoolSliceStorage.recoverTransitionRead`. Both levels can return asynchronous upgrade callables that are executed by a fixed thread pool. Hot-add uses `prepareVolume` to load a DataNode directory and every known namespace's block-pool directories into a `VolumeBuilder`; `build` later adds those directories to `DataStorage`.

State and persistence: writes DataNode VERSION properties including `storageType`, `clusterID`, `cTime`, `layoutVersion`, `storageID`, optional `datanodeUuid`, and pre-federation `namespaceID`. Reads validate layout version, storage type, cluster ID, namespace ID, storage UUID consistency, and DataNode UUID consistency across directories. `createStorageID` generates or repairs per-volume storage UUIDs, with special handling for `StorageType.PROVIDED`. `format` clears a directory, sets current DataNode layout, namespace/cluster data, DataNode UUID, storage UUID, and writes properties.

Upgrade and rollback behavior: `doTransition` rejects incompatible namespace/cluster state, updates properties for already-federated old layouts, and performs pre-federation upgrades by moving `current` to `previous.tmp`, formatting the block-pool root, hard-linking blocks into the new block-pool `current`, writing upgraded VERSION properties, and renaming `previous.tmp` to `previous`. `doRollback` restores `previous` to `current` after validating layout version and cTime, or performs a simple layout-version rollback for post-federation layouts without a previous directory. `doFinalize` renames `previous` to `finalized.tmp` and deletes it asynchronously; `finalizeUpgrade` finalizes either DataNode-level or block-pool-level snapshots.

Block layout migration: `linkAllBlocks` hard-links finalized and RBW blocks from old layouts into the new tree. `linkBlocks` detects when an upgrade to the 32-by-32 block-ID layout is needed, recursively scans old subdirectories, computes destination directories via `DatanodeUtil.idToBlockDir`, batches hard links across worker threads, detects duplicate block/meta entries, and removes duplicates by preferring highest generation stamp and then longest block file. Legacy `blocksBeingWritten` content is migrated into `rbw` for pre-RBW layouts.

Dependencies and integration points: integrates tightly with `DataNode`, `Storage`, `StorageDirectory`, `StorageLocation`, `BlockPoolSliceStorage`, `NamespaceInfo`, `DatanodeStorage`, `DataNodeLayoutVersion`, `LayoutVersion`, `DatanodeUtil`, `HardLink`, `FileUtil`, and configuration keys for parallel volume load and block-ID layout upgrade threads. `FsDatasetSpi` consumes the loaded `DataStorage` when building active volumes.

Risks: storage transitions are destructive if interrupted in unexpected phases, so temp-directory naming and recovery behavior are critical. VERSION validation must reject mismatched DataNode UUIDs, cluster IDs, namespace IDs, and storage IDs without blocking legitimate upgrades. Parallel upgrade and hard-link workers increase throughput but surface partial-failure complexity. Duplicate block resolution is heuristic and logs discarded lower-priority entries. `removeVolumes` removes block-pool storage and unlocks directories even if some unlocks fail, aggregating errors afterward. Rolling-upgrade trash is bypassed during layout upgrade when a `previous` directory exists, which must remain consistent with rollback expectations.

Test signals: strong tests should cover fresh format, UUID generation/repair, provided storage UUID behavior, pre-federation upgrade, post-federation property upgrade, rollback with and without `previous`, finalization cleanup, rolling-upgrade trash markers, hot-add `VolumeBuilder`, failed volume removal, duplicate block entry resolution, block-ID layout hard-link paths, legacy `blocksBeingWritten` migration, parallel task interruption, and VERSION incompatibility errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataStorage.java -->
