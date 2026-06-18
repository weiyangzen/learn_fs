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
