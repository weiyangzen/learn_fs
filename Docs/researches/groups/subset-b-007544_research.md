<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestCacheByPmemMappableBlockLoader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestCacheByPmemMappableBlockLoader.java

Purpose: JUnit 5 coverage for HDFS DataNode persistent-memory caching through `PmemMappableBlockLoader`, using two temporary PMEM directories as bogus persistent memory volumes. It verifies PMEM volume accounting, round-robin volume selection, cache-path construction, capacity exhaustion, and uncache cleanup.

Important APIs/types/functions: `MiniDFSCluster`, `DistributedFileSystem`, `FsDatasetCache`, `PmemVolumeManager`, `ExtendedBlockId`, `CacheDirectiveInfo`, `CachePoolInfo`, `MetricsAsserts`, `DataNodeFaultInjector`, `NativeIO.POSIX.CacheManipulator`, `setUpClass`, `setUp`, `tearDown`, `testPmemVolumeManager`, `getExtendedBlockId`, and `testCacheAndUncache`.

Control flow: class setup skips unless PMDK is available, installs a `DataNodeFaultInjector` that gates BPServiceActor offer-service work behind a read/write lock, and enables verbose cache logging. Per-test setup configures short NameNode cache refresh and DataNode cache-report intervals, block size, PMEM directories, PMEM capacity split across two volumes, and a `NoMlockCacheManipulator`; then it starts a one-DataNode cluster and grabs `FsDatasetImpl.cacheManager`. `testPmemVolumeManager` checks aggregate capacity and that ten volume choices split evenly between the two real PMEM directories. `testCacheAndUncache` creates a file that exactly fills the PMEM cache, adds a cache directive, waits for `BlocksCached`, checks `cacheUsed`, `memCacheUsed`, `blockKeyToVolume`, and per-block cache paths, attempts a second one-block cache that should not increase cached blocks, removes directives, and waits for `BlocksUncached`.

State and persistence behavior: state under test is in-memory `PmemVolumeManager` volume maps plus PMEM cache files under `<pmem>/<blockPoolId>/<blockId>`. DRAM cache is expected to remain at zero. Uncache must delete PMEM accounting entries and return cache usage to zero.

Dependencies and integration points: integrates NameNode cache directives, DataNode heartbeats/cache reports, HDFS block locations, DataNode metrics, PMDK native availability, and the `FsDatasetCache` PMEM loader path.

Risks: tests depend on PMDK and timing-sensitive metric polling. `PmemVolumeManager.setMaxBytes(CACHE_CAPACITY * 0.5)` assumes two configured volumes. The path checks compare against the configured PMEM directory prefix as well as `getRealPmemDir`, so symlink or normalization changes could affect failures.

Test signals: successful run proves PMEM cache capacity is enforced, block-to-volume mappings match HDFS block IDs, another cache directive cannot overfill PMEM, and uncache clears both bytes and mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestCacheByPmemMappableBlockLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestDatanodeRestart.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestDatanodeRestart.java

Purpose: restart-focused DataNode tests for replica persistence and registration waits. It checks finalized replicas survive DataNode restarts, RBW replicas are recovered as RWR with correct length after restart, and client operations wait for DataNode registration state instead of failing immediately on missing saved registration.

Important APIs/types/functions: `MiniDFSCluster`, `DFSTestUtil`, `FSDataOutputStream`, `DataNodeTestUtils`, `FsDatasetImpl`, `ReplicaMap`, `ReplicaInfo`, `ReplicaState.RWR`, `DataNodeFaultInjector.noRegistration`, `testFinalizedReplicas`, `testRbwReplicas`, private `testRbwReplicas`, `dataset`, and `testWaitForRegistrationOnRestart`.

Control flow: `testFinalizedReplicas` starts three DataNodes, writes two files at replication 3, verifies contents and replication, restarts DataNodes, and checks file readability again. The RBW helper writes and `hflush`es an unclosed file, optionally truncates on-disk block files by one byte to simulate corruption, restarts DataNodes, and inspects the restarted DataNode `volumeMap`; the replica should become `RWR`, with corrupt length rounded down to checksum packet boundary. It invalidates the recovered replica afterward. `testWaitForRegistrationOnRestart` installs a fault injector whose `noRegistration` throws, creates a one-DataNode cluster, verifies write and read paths wait roughly the configured five-second BP-ready timeout, restores the injector to prove operations succeed, then repeats for `getReplicaVisibleLength` via append/open.

State and persistence behavior: finalized files persist across local volume restart. RBW disk state transitions to RWR in memory on restart, preserving or truncating byte length based on corruption. Registration state is intentionally unavailable through the fault injector, exercising timeout behavior rather than disk state.

Dependencies and integration points: uses NameNode/DataNode MiniDFSCluster lifecycle, DataNode local `rbw` directories, `ReplicaMap`, client socket timeout, BP-ready timeout, and HDFS append/read RPCs.

Risks: `testRbwReplicas` lacks `@Test` annotation in this file, so only direct framework discovery would miss it unless invoked elsewhere or intentionally disabled. Timing assertions allow 5-10 seconds and can be sensitive to slow test hosts.

Test signals: failures indicate replica state regression on restart, corrupt RBW length recovery mistakes, or DataNode RPCs bypassing registration wait semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestDatanodeRestart.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestFsDatasetCache.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestFsDatasetCache.java

Purpose: slow, non-thread-safe tests for the normal locked-memory `FsDatasetCache` path. The file validates cache/uncache commands, retry behavior, page-size accounting, capacity failures, cancellation, unknown uncache handling, quiescence, and recaching after space is freed.

Important APIs/types/functions: `FsDatasetSpi`, `FsDatasetCache`, `CacheStats.PageRounder`, `DatanodeProtocolClientSideTranslatorPB`, `BlockIdCommand`, `DatanodeProtocol.DNA_CACHE`, `DNA_UNCACHE`, `NativeIO.POSIX.CacheManipulator`, `NoMlockCacheManipulator`, helper methods `setHeartbeatResponse`, `cacheBlocks`, `uncacheBlocks`, `getResponse`, `getBlockSizes`, and `testCacheAndUncacheBlock`.

Control flow: setup creates a one-DataNode cluster with cache capacity equal to typical locked-memory limits, page-sized block size, fast cache reports, and a spied NameNode protocol translator. The fault injector pauses BPServiceActor heartbeat work while tests replace heartbeat responses with synthetic cache/uncache commands. `testCacheAndUncacheBlock` writes five blocks, sends one cache command at a time, waits for expected used bytes and cached block count, then uncache commands each block. Other tests replace `mlock` to fail once then succeed, fill capacity with multiple files and assert failure log/metrics, uncache while `mlock` sleeps, uncache a never-cached block, verify small blocks round up to OS page size, ensure directive removal emits no extra cache operations, and verify a small directive gets cached after a full-cache file is uncached.

State and persistence behavior: state is volatile locked-memory accounting in `FsDatasetSpi`/`FsDatasetCache`, DataNode metrics counters, and NameNode cache directive stats. No PMEM or durable cache state is expected. Cleanup asserts cache usage returns to zero to avoid descriptor leaks.

Dependencies and integration points: integrates DataNode heartbeats, cache directives, DFS block readers, file-channel block size inspection, root log capture, NameNode FSImage transaction ID for heartbeat responses, and native cache manipulator abstraction.

Risks: timing-heavy waits and injected sleeping `mlock` can be flaky on overloaded hosts. Root logger appender matching a message substring couples the test to error text. Tests assume page rounding and configured cache capacity align with file layout.

Test signals: failures catch regressions in cache command idempotence, cache space reservation rollback, retry semantics, cancellation cleanup, metrics counters, and NameNode directive recache behavior after HDFS-6107-style pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestFsDatasetCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestFsDatasetImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestFsDatasetImpl.java

Purpose: broad `FsDatasetImpl` regression suite covering DataNode volume lifecycle, storage UUID validation, same-disk tiering, block movement, duplicate replica handling, directory scanning, bad-block reporting, invalidation, async deletion, cached `dfsUsed`, metadata sizing, append accounting, and reference/lock cleanup.

Important APIs/types/functions: `FsDatasetImpl`, `FsVolumeImpl`, `FsVolumeList`, `MountVolumeMap`, `ReplicaMap`, `ReplicaInfo`, `FinalizedReplica`, `ReplicaHandler`, `DataStorage.VolumeBuilder`, `StorageLocation`, `NamespaceInfo`, `DirectoryScanner`, `BlockScanner`, `DataSetLockManager`, helpers `createStorageDirs`, `createStorageWithStorageType`, `createStorageWithCapacityRatioConfig`, `createNewReplicaObj`, `createNewReplicaObjWithLink`, `getDestinationVolume`, `createTestFile`, and `validateFileLen`.

Control flow: most unit-style tests use mocked `DataNode`/`DataStorage` plus real `FsDatasetImpl`; cluster-style tests start `MiniDFSCluster` for behavior requiring NameNode, client, DataXceiver, metrics, block reports, or disk scanning. Volume tests add/remove storage directories, verify storage maps and async services, and assert duplicate UUIDs prevent DataNode registration. Same-disk tiering tests configure DISK/ARCHIVE ratios, reject duplicate storage type on a mount, and verify hard-link block movement when same-mount tiering is enabled. Block movement tests copy or hard-link replicas, finalize new replicas, handle generation-stamp races after append, validate restart cleanup of temporary/finalized hard links, and read through a `BlockReader` while the block is moved. Invalidation tests check pending async deletion memory retention, missing-block notification/recovery, and volume-reference release on exceptions.

State and persistence behavior: exercises volume maps, storage maps, mount capacity-ratio maps, block pool directories, `DU_CACHE_FILE`, replica cache root files, temporary/finalized replica files, hard links, metadata-file length cache, DataNode JMX `PendingAsyncDeletions`, NameNode low-redundancy/corrupt block counters, and DataNode metrics. `@AfterEach` calls `DataSetLockManager.lockLeakCheck` to catch leaked dataset locks.

Dependencies and integration points: integrates HDFS client writes/appends/reads, MiniDFSCluster, block reports, DirectoryScanner, BlockManager, DataNode fault injection, MBeans, per-volume metrics, native copy metrics, async disk services, and storage-type placement.

Risks: very broad blast radius and several slow/timing-sensitive waits. Some helper paths manually close `FsVolumeReferences`; future API changes around references can introduce leaks. Several tests depend on filesystem permissions, hard-link semantics, mount detection through `DF`, and platform behavior around file deletion/open readers.

Test signals: failures identify regressions in volume add/remove consistency, replica-map correctness under concurrency, block movement safety, DataNode restart cleanup, missing/corrupt block reporting, async deletion visibility, lock/reference cleanup, and append `dfsUsed` accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestFsDatasetImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestFsVolumeList.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestFsVolumeList.java

Purpose: tests `FsVolumeList` and `FsVolumeImpl` volume-selection/accounting behavior, including closed-volume exclusion, reference release when no block scanner exists, reserved-space configuration by storage type, capacity caching, same-disk archival mapping, slow-disk exclusion, and replica-map loading thread pools.

Important APIs/types/functions: `FsVolumeList`, `FsVolumeImplBuilder`, `FsVolumeImpl`, `RoundRobinVolumeChoosingPolicy`, `MountVolumeMap`, `ReservedSpaceCalculator`, `BlockPoolSlice`, `ForkJoinPool`, `SlowDiskReports`, `MiniDFSCluster`, tests `testGetNextVolumeWithClosedVolume`, `testDfsReservedForDifferentStorageTypes`, `testDfsReservedPercentageForDifferentStorageTypes`, `testAddRplicaProcessorForAddingReplicaInMap`, `testGetVolumeWithSameDiskArchival`, and `testExcludeSlowDiskWhenChoosingVolume`.

Control flow: setup builds a mocked dataset, disabled block scanner, and base temp directory. Unit tests construct volumes with different storage-type prefixes and mocked `DF` usage to assert reserved bytes, capacity, available bytes, and non-DFS-used calculations. Volume-list tests add references, mark one closed, and repeatedly choose next volumes to ensure closed volumes are skipped; a no-block-scanner case asserts `addVolume` releases the incoming reference. Replica-map tests create many files concurrently in a one-DataNode cluster, then call `getVolumeMap` and verify `BlockPoolSlice` uses the configured add-replica fork pool size and shares a pool across federated block pools. Same-disk archival tests add DISK and ARCHIVE volumes on one mount and verify map lookup/removal and split capacity/non-DFS-used math. Slow-disk tests inject outlier reports and assert new blocks avoid excluded volumes.

State and persistence behavior: state includes volume reference lifecycle, per-volume reserved/capacity cached values, `MountVolumeMap` by mount/storage type, block-pool replica maps loaded from disk, static `BlockPoolSlice` add-replica pool, and DataNode disk metrics slow-disk exclusion lists.

Dependencies and integration points: integrates storage location parsing, block scanner registration, `DF` disk stats, DataNode disk metrics, MiniDFSCluster storage capacities, federated NameNode topology, and HDFS file creation/block placement.

Risks: mount equality depends on local filesystem layout, especially same-disk archival. Slow-disk exclusion has asynchronous collector timing. Static add-replica thread-pool state can leak across tests if not reinitialized.

Test signals: failures flag volume chooser regressions, reference leaks, reserved-space miscalculation, incorrect same-mount capacity partitioning, slow-disk placement failures, or parallel replica-map loading issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestFsVolumeList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestInterDatanodeProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestInterDatanodeProtocol.java

Purpose: tests Inter-DataNode protocol behavior for block metadata, replica recovery initialization/update, hostname-based DataNode communication, recovery error cases, and RPC timeout behavior.

Important APIs/types/functions: `InterDatanodeProtocol`, `DataNodeTestUtils.createInterDatanodeProtocolProxy`, `FsDatasetImpl.initReplicaRecovery`, `FsDatasetSpi.updateReplicaUnderRecovery`, `ReplicaRecoveryInfo`, `ReplicaUnderRecovery`, `RecoveringBlock`, `RecoveryInProgressException`, nested `TestServer`, helpers `checkMetaInfo`, `getLastLocatedBlock`, `createReplicaInfo`, `assertReplicaEquals`, and tests `testBlockMetaDataInfo`, `testBlockMetaDataInfoWithHostname`, `testInitReplicaRecovery`, `testUpdateReplicaUnderRecovery`, `testInterDNProtocolTimeout`.

Control flow: metadata tests build a three-DataNode cluster, write a replicated file, get its last block, connect to one DataNode through an inter-DN proxy, stop block scanners, verify stored block metadata, call `initReplicaRecovery`, then `updateReplicaUnderRecovery` with a shorter length and incremented generation stamp. They also verify missing block recovery returns null. Hostname mode advertises `localhost` and is Linux-only. Static recovery tests build a `ReplicaMap` with finalized external-volume replicas, transition one to `ReplicaUnderRecovery`, update recovery IDs, assert stale recovery IDs throw `RecoveryInProgressException`, assert missing replicas return null, and assert invalid generation-stamp combinations fail. Update tests use a real cluster, initialize recovery, verify RUR state and disk replica, reject mismatched length, then update successfully. Timeout test starts a sleeping RPC `Server` and expects `SocketTimeoutException`.

State and persistence behavior: mutates `ReplicaMap` entries from finalized to under-recovery, updates recovery IDs and replica lengths/generation stamps, and validates stored block metadata on DataNode disk. It also checks `DataSetLockManager` leak state after static recovery tests.

Dependencies and integration points: covers DFSClient NameNode block lookup, DataNode IPC addresses/hostnames, Hadoop RPC, MiniDFSCluster, external volume stubs, and recovery protocol contracts shared by NameNode-initiated lease recovery.

Risks: uses deprecated reflection-style `newInstance` in the test RPC server. Hostname variant is platform-gated. Recovery assertions rely on exact exception semantics and on `DFS_DATANODE_XCEIVER_STOP_TIMEOUT_MILLIS_DEFAULT`.

Test signals: failures indicate inter-DN block metadata mismatch, replica recovery state-machine regressions, recovery concurrency guard failures, or RPC timeout configuration breakage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestInterDatanodeProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistFiles.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistFiles.java

Purpose: functional tests for lazy-persist files on RAM_DISK, focusing on disallowed file operations, corrupt-file scrubbing, NameNode restart behavior, concurrent reads/writes, and volume-reference release when lazy persistence scheduling fails.

Important APIs/types/functions: extends `LazyPersistTestCase`; uses `getClusterBuilder`, `makeTestFile`, `makeRandomTestFile`, `ensureFileReplicasOnStorageType`, `waitForRedundancyMonitorCycle`, `waitForScrubberCycle`, `waitForFile`, `waitForLowRedundancyCount`, `waitForCorruptBlock`, `triggerBlockReport`, `WriterRunnable`, `DataNodeTestUtils`, `FsDatasetImpl.asyncLazyPersistService`, and `FsDatasetSpi.FsVolumeReferences`.

Control flow: operation-denial tests create lazy-persist files and expect `append` or `truncate` to fail. Scrubber tests create a RAM_DISK lazy file, stop DataNodes, wait for NameNode corruption detection, and verify the lazy-persist scrubber either deletes the file or leaves it when disabled; a NameNode restart variant verifies the file is not discarded merely because the NameNode restarted. Concurrent read creates a seeded random RAM_DISK file and spawns multiple reader threads verifying contents. Concurrent write starts four writer tasks, each writing several lazy-persist files while eviction/lazy writer activity may run, then waits for completion. The reference-release test shuts down `asyncLazyPersistService`, records per-volume reference counts, writes a lazy file, waits through lazy-writer retries, and asserts reference counts do not grow unbounded.

State and persistence behavior: tests transient RAM_DISK replicas, lazy persisted disk copies, NameNode corrupt/low-redundancy state, scrubber deletion state, and `FsVolumeImpl` reference counts. Lazy persisted files should be discarded differently from normal corrupt files when replicas are lost.

Dependencies and integration points: depends on `LazyPersistTestCase` cluster configuration, DataNode lazy writer, NameNode redundancy monitor and scrubber, HDFS client append/truncate/create APIs, and block reports.

Risks: concurrency and timing are central; lazy-writer interval sleeps and scrubber cycles can be sensitive to runtime load. The reference-count assertion allows one extra reference because the lazy writer can keep retrying.

Test signals: failures catch illegal lazy-persist mutation acceptance, scrubber policy regressions, data corruption under concurrent RAM_DISK reads/writes, and leaked volume references on async service failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistFiles.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistLockedMemory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistLockedMemory.java

Purpose: verifies locked-memory accounting for lazy-persist RAM_DISK replicas, including fallback when no locked memory is available, reservation on write, release on delete/eviction, page rounding for short blocks, and cleanup after client pipeline failure.

Important APIs/types/functions: extends `LazyPersistTestCase`; uses `FsDatasetSpi.getCacheUsed`, `FsDatasetImpl.evictLazyPersistBlocks`, `DataNodeTestUtils.triggerBlockReport`, `BlockManagerTestUtil.waitForMarkedDeleteQueueIsEmpty`, `DFSTestUtil.abortStream`, `DFSOutputStream`, helper `waitForLockedBytesUsed`, and storage types `RAM_DISK` and `DEFAULT`.

Control flow: `testWithNoLockedMemory` builds one DataNode with max locked memory zero, creates a lazy file, and expects DEFAULT storage. `testReservation` writes one block with max locked memory equal to block size and expects RAM_DISK plus `cacheUsed == BLOCK_SIZE`. Delete and eviction tests first reserve memory, then delete the file or lazy-persist and evict it, waiting for locked bytes to drop to zero. Short-block test writes one byte and expects OS page-size locked accounting. Pipeline failure test creates a lazy file stream, writes and syncs one byte, aborts the DFS output stream, waits for page-sized locked memory, deletes the file, drains marked-delete queue, triggers a block report, and waits for zero.

State and persistence behavior: locked memory is surfaced through `FsDatasetSpi.getCacheUsed`, the same metric used by cache code. RAM_DISK replicas consume locked bytes until deleted or evicted after persistent copy. Failed writes still reserve a rounded page until namespace/deletion cleanup releases it.

Dependencies and integration points: integrates client create flags `CREATE` and `LAZY_PERSIST`, DataNode RAM_DISK placement, block reports, NameNode delete queues, lazy writer metrics, and OS page-size behavior inherited from the test case.

Risks: `cacheUsed` doubles as locked-memory signal for lazy persist and can be affected by unrelated cache features if cluster setup changes. The pipeline failure path is timing-sensitive around aborted streams and block report/delete processing.

Test signals: failures indicate memory leaks, incorrect fallback to RAM_DISK without lock budget, bad page rounding, or missing release after deletion, eviction, or aborted writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistLockedMemory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistPolicy.java

Purpose: compact tests for HDFS lazy-persist storage-policy metadata propagation and persistence. It verifies the policy is absent by default, present when creating a lazy-persist file, and survives both edit-log replay and FsImage checkpoint/restart.

Important APIs/types/functions: extends `LazyPersistTestCase`; uses `getClusterBuilder`, `makeTestFile`, HDFS client `getFileInfo`, `HdfsFileStatus.getStoragePolicy`, `LAZY_PERSIST_POLICY_ID`, `cluster.restartNameNode`, `SafeModeAction.ENTER/LEAVE`, and `fs.saveNamespace`.

Control flow: each test starts the shared lazy-persist cluster builder, creates a zero-length test file either with or without lazy-persist enabled, then stats the file through the client. The default case asserts the storage policy ID differs from `LAZY_PERSIST_POLICY_ID`. The propagation case asserts equality immediately after creation. The edit-log case restarts the NameNode with edits replay and checks the policy remains. The FsImage case enters safe mode, saves namespace, leaves safe mode, restarts the NameNode, and checks the stored policy again.

State and persistence behavior: state under test is NameNode inode storage policy metadata, not DataNode replica placement. The policy must be serialized in edit logs and FsImage and exposed through `HdfsFileStatus`.

Dependencies and integration points: integrates the lazy-persist file-creation helper, HDFS client protocol file status, NameNode restart, safe mode, and namespace checkpoint persistence.

Risks: because files are zero-length, the tests isolate metadata but do not validate RAM_DISK placement or lazy writer behavior. They depend on `LazyPersistTestCase` constants matching the cluster's configured policy IDs.

Test signals: failures identify storage-policy propagation bugs, edit-log serialization regressions, FsImage serialization regressions, or accidental defaulting of normal files to lazy persist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistReplicaPlacement.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistReplicaPlacement.java

Purpose: tests initial placement and fallback rules for lazy-persist replicas, including RAM_DISK success, no-transient-storage fallback, synchronous eviction, full/partial memory-budget fallback, and ensuring RAM_DISK is not used by normal files.

Important APIs/types/functions: extends `LazyPersistTestCase`; uses `getClusterBuilder`, `makeTestFile`, `ensureFileReplicasOnStorageType`, `verifyRamDiskJMXMetric`, `waitForMetric`, `triggerBlockReport`, client `getLocatedBlocks`, `LocatedBlock.getStorageTypes`, storage types `RAM_DISK`, `DEFAULT`, and custom `StorageType[]` cluster setup.

Control flow: basic placement creates a lazy-persist file and expects RAM_DISK. Size-limited RAM_DISK capacity still admits two files when capacity is set to three replicas. No transient storage builds a cluster without RAM_DISK and expects DEFAULT placement without error. Synchronous eviction writes one RAM_DISK block, waits for lazy persistence, writes another block with limited locked memory, and expects `RamDiskBlocksEvictedWithoutRead`. Full fallback sets max locked memory below block size and expects DEFAULT plus write-fallback metric. Partial fallback writes a five-block file with room for two RAM_DISK blocks, waits for lazy writer/block report, then counts two RAM_DISK and three DEFAULT blocks. The final test configures only RAM_DISK storage but creates a non-lazy file and expects placement failure.

State and persistence behavior: state includes block placement storage types in located blocks, RAM_DISK eviction/fallback JMX metrics, transient locked-memory budget, and persistent copies created by the lazy writer before eviction.

Dependencies and integration points: integrates NameNode block placement policy, DataNode RAM_DISK volumes, locked-memory limits, lazy writer timing, block reports, and HDFS located-block storage-type reporting.

Risks: partial fallback depends on asynchronous eviction timing but asserts exact 2/3 distribution after sleeping. Metrics are global to the test cluster and require clean setup per test.

Test signals: failures catch incorrect lazy-persist placement, accidental RAM_DISK use for normal writes, eviction/fallback metric regressions, or storage-type reporting mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistReplicaPlacement.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistReplicaRecovery.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistReplicaRecovery.java

Purpose: verifies DataNode restart behavior for lazy-persist replicas depending on whether the RAM_DISK block had already been saved to persistent storage.

Important APIs/types/functions: extends `LazyPersistTestCase`; uses `FSNamesystem`, `NameNodeAdapter.getDatanode`, `DatanodeDescriptor`, `DatanodeStorageInfo`, `DataNode.triggerBlockReport`, `BlockReportOptions`, `FsDatasetImpl.getNonPersistentReplicas`, `FsDatasetTestUtil.stopLazyWriter`, helper `waitForBlockReport`, and storage types `RAM_DISK` and `DEFAULT`.

Control flow: `testDnRestartWithSavedReplicas` creates a lazy RAM_DISK file, waits until `FsDatasetImpl.getNonPersistentReplicas()` reaches zero, confirming the lazy writer saved the block while it remains on RAM_DISK, restarts the DataNode, triggers and waits for a block report count change, then expects the block to be reported on DEFAULT persistent storage. `testDnRestartWithUnsavedReplicas` stops the lazy writer before creating the file, verifies the block is on RAM_DISK, restarts the DataNode, waits for cluster activity, and expects storage type to remain RAM_DISK because there is no saved persistent copy to promote.

State and persistence behavior: distinguishes non-persistent RAM_DISK replica state from saved persistent replica state. Restart should recover saved replicas as persistent storage, while unsaved replicas remain transient in block-location reporting.

Dependencies and integration points: integrates DataNode restart, lazy writer, block reports, NameNode `DatanodeDescriptor` storage report counters, and located-block storage type verification from the shared test case.

Risks: assumes block report count changes on the first storage info after trigger. Timing depends on lazy writer interval and DataNode restart speed.

Test signals: failures indicate DataNode restart incorrectly loses saved lazy-persist replicas, incorrectly promotes unsaved transient replicas, or fails to update NameNode storage-type state after restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistReplicaRecovery.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyWriter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyWriter.java

Purpose: tests the DataNode lazy writer and RAM_DISK eviction lifecycle: saving lazy-persist blocks to disk, synchronous and LRU eviction, protecting unsaved blocks from eviction, delete-before/after-persist cleanup, and HDFS used-space accounting.

Important APIs/types/functions: extends `LazyPersistTestCase`; uses `makeTestFile`, `makeRandomTestFile`, `ensureFileReplicasOnStorageType`, `ensureLazyPersistBlocksAreSaved`, `waitForMetric`, `verifyRamDiskJMXMetric`, `verifyDeletedBlocks`, `verifyReadRandomFile`, `FsDatasetTestUtil.stopLazyWriter`, `DFSTestUtil.readFile`, and storage types `RAM_DISK` and `DEFAULT`.

Control flow: `testLazyPersistBlocksAreSaved` writes a ten-block lazy file, verifies RAM_DISK placement, waits for `RamDiskBlocksLazyPersisted`, and checks saved disk copies. Synchronous eviction writes one block, waits for persistence, writes another under one-block memory, and expects eviction metrics. Unsaved-block protection stops lazy writer, writes a RAM_DISK file, writes a second file, and verifies the first stays on RAM_DISK while the second falls back to DEFAULT. LRU eviction writes several files, waits for persistence, reads them in shuffled order to establish access order, then writes replacements and verifies each touched file moves to DEFAULT in LRU order while later ones remain RAM_DISK. Delete tests remove files before and after lazy persistence and verify corresponding block deletion and metrics. DFS usage test checks `fs.getUsed()` increases by one block on create, does not double-count after lazy persistence, and returns to the pre-create value after delete.

State and persistence behavior: covers transient RAM_DISK replicas, persistent lazy copies, eviction LRU metadata, RAM_DISK JMX counters, deleted block state, read-hit tracking, and NameNode used-space accounting.

Dependencies and integration points: integrates lazy writer background thread, RAM_DISK eviction policy, HDFS read path for access-order updates, client delete, NameNode block deletion, and located-block storage-type reporting.

Risks: LRU ordering depends on reads updating RAM_DISK replica access state deterministically. Tests rely on metric counters being reset with each cluster and on lazy writer timing.

Test signals: failures catch unsaved replica eviction, missing lazy-persist disk copies, broken eviction metrics/order, block deletion leaks, or namespace usage double-counting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestPmemCacheRecovery.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestPmemCacheRecovery.java

Purpose: PMEM cache restart-recovery test for `PmemMappableBlockLoader`. It verifies cached PMEM block files and `PmemVolumeManager` mappings are reconstructed after cluster shutdown/restart when PMEM cache recovery is enabled.

Important APIs/types/functions: `MiniDFSCluster`, `DistributedFileSystem`, `FsDatasetCache`, `PmemVolumeManager`, `FsDatasetImpl.setBlockPoolId`, `ExtendedBlockId`, `CacheDirectiveInfo`, `CachePoolInfo`, `DataNodeFaultInjector`, `NativeIO.POSIX.NoMlockCacheManipulator`, helpers `restartCluster`, `shutdownCluster`, `getExtendedBlockId`, and test `testCacheRecovery`.

Control flow: class setup requires PMDK, installs the same BPServiceActor read/write-lock fault injector used by PMEM cache tests, and configures cache debug logging. Per-test setup enables `DFS_DATANODE_PMEM_CACHE_RECOVERY_KEY`, short cache-refresh/report intervals, two PMEM directories, and a no-op mlock manipulator, then starts a one-DataNode cluster. `testCacheRecovery` creates a file that fills the configured cache amount, adds a cache pool/directive, waits for all blocks cached, verifies cache usage, mappings, block pool ID, and per-block PMEM paths. It then shuts the cluster down, resets only the cluster while preserving PMEM files and using `FsDatasetImpl.setBlockPoolId(blockPoolId)`, restarts, and re-verifies cache bytes, mappings, and cache paths. Finally it uncaches each block directly through `cacheManager.uncacheBlock`, waits for `BlocksUncached`, and expects zero used bytes and no mappings.

State and persistence behavior: PMEM cache files survive process restart under the configured PMEM directories. `PmemVolumeManager.reset()` is called only in `shutdownCluster`, and restart reconstructs in-memory block-to-volume mappings from persisted PMEM cache files.

Dependencies and integration points: depends on PMDK native availability, PMEM directory layout, DataNode cache metrics, HDFS cache directives, DataNode restart lifecycle, and `FsDatasetImpl` block-pool recovery hook.

Risks: uses static `blockPoolId` and direct `FsDatasetImpl.setBlockPoolId`, so parallel execution or API changes could interfere. The uncache assertion checks the old `blockKeyToVolume` reference after reassignment; correctness relies on it reflecting the singleton map.

Test signals: failures identify lost PMEM cache state across restart, wrong PMEM path reconstruction, incorrect cache byte accounting after recovery, or uncache cleanup regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestPmemCacheRecovery.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestProvidedImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestProvidedImpl.java

Purpose: tests HDFS provided-storage integration inside `FsDatasetImpl`, including provided volume construction, alias-map block loading, block reads, iterators, path containment/suffix handling, DirectoryScanner behavior, and provided replicas backed by path handles.

Important APIs/types/functions: `ProvidedVolumeImpl`, `ProvidedReplica`, `FinalizedProvidedReplica`, `BlockAliasMap<FileRegion>`, `FileRegion`, nested `TestFileRegionIterator`, nested `TestFileRegionBlockAliasMap`, `createStorageDirs`, `getBlocksInProvidedVolumes`, `ProvidedVolumeImpl.containsBlock`, `ProvidedVolumeImpl.getSuffix`, `DirectoryScanner`, `PathHandle`, and tests `testReserved`, `testProvidedVolumeImpl`, `testBlockLoad`, `testProvidedBlockRead`, `testProvidedBlockIterator`, `testProvidedVolumeContents`, `testProvidedReplicaWithPathHandle`.

Control flow: setup mocks a `DataNode` and `DataStorage`, configures one local and one `[PROVIDED]` storage directory, registers `TestFileRegionBlockAliasMap` as the provided alias map, creates `FsDatasetImpl`, collects provided volumes, and adds two block pools. The iterator lazily creates backing files with deterministic content, records block ID to path, and yields `FileRegion` entries for one selected block pool. Tests assert provided volumes have zero reserved space, expected storage UUID/type, used bytes, and block counts; load volume maps and verify only the selected block pool has replicas; read each provided block through `dataset.getBlockInputStream`; exercise block iterators and rewind; test whether provided volume base paths include or exclude candidate block URIs; validate URI/path suffix extraction for file and object-store schemes; verify `ProvidedReplica` prefixes; confirm disabled directory scanning reports no provided blocks; and check `FinalizedProvidedReplica` can keep reading via `PathHandle` after file rename but fails without the handle.

State and persistence behavior: backing files are created under the provided base path and represented in memory as provided replicas sourced from alias-map regions. Provided volumes report usage from alias-map regions rather than normal DataNode-local block files. Path handles persist access across rename for provided replicas.

Dependencies and integration points: integrates `DFS_PROVIDED_ALIASMAP_CLASS`, storage-location parsing with `[PROVIDED]`, block alias map readers, dataset block input streams, DirectoryScanner reports, MiniDFSCluster for path-handle validation, and filesystem handle options.

Risks: only one provided volume is supported by the test constants. The alias-map reader's `resolve` is unimplemented, so lookup coverage is iterator-oriented. `TestFileRegionIterator.hasNext` uses `currentCount < numBlocks`, making nonzero `minId` semantics depend on caller expectations.

Test signals: failures catch provided-volume accounting errors, alias-map load/read regressions, path filtering mistakes across URI schemes, scanner over-reporting, and provided replica read instability after path movement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestProvidedImpl.java -->
