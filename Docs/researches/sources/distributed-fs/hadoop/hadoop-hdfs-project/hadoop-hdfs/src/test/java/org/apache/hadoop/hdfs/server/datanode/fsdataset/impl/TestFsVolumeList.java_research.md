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
