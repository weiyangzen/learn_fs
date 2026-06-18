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
