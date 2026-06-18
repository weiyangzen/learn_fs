# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestQuotaByStorageType.java

Purpose: Exercises HDFS directory quota accounting by heterogeneous storage type, especially SSD/DISK accounting under storage policies. It validates create, append, delete, rename, truncate, snapshot retention, traditional disk-space quota interaction, content summary reporting, and persistence of per-storage-type quota through edit logs and fsimage checkpoints.

Important APIs and functions: `setUp()` builds a 3 DataNode `MiniDFSCluster` with SSD and default storage per node and caches `FSDirectory`, `DistributedFileSystem`, and `FSNamesystem`. Test helpers call `dfs.setStoragePolicy`, `dfs.setQuotaByStorageType`, `dfs.setQuota`, `DFSTestUtil.createFile`, `DFSTestUtil.appendFile`, `dfs.truncate`, `dfs.saveNamespace`, and `cluster.restartNameNode`. Assertions read `INodeDirectory.getDirectoryWithQuotaFeature().getSpaceConsumed()`, `QuotaCounts`, `computeQuotaUsage`, and `ContentSummary.getTypeConsumed`.

Control flow: Each test creates a directory under `/TestQuotaByStorageType`, applies a storage policy such as `ONESSD`, `ALLSSD`, `HOT`, or `WARM`, sets quota limits, then mutates files and checks live NameNode quota counters. Exception tests deliberately exceed SSD or traditional storage-space limits and verify counters remain at the last valid usage. Persistence tests write quotas and files, restart from edits or save an fsimage in safemode, then refresh NameNode handles and re-read quota limits and consumed type-space.

State and persistence behavior: The tested state lives in `DirectoryWithQuotaFeature` quota and consumption counters attached to INodes, storage-policy-derived block placement, fsimage serialization, and edit-log replay. Snapshot tests ensure deleted file blocks remain counted until the snapshot is removed. Clearing one storage-type quota must reset only that storage type while leaving other type quotas intact.

Dependencies and integration points: Integrates `FSDirectory`, `FSNamesystem`, `BlockStoragePolicySuite`, `ContentSummary`, HDFS client quota RPCs, `SnapshotTestHelper`, and block placement/storage policy accounting. It is a NameNode integration suite rather than an isolated unit test.

Risks: Storage-type accounting can diverge from traditional storage-space accounting when replication, policy fallback, rename rollback, or partial create failure paths are wrong. Assertions that catch broad `Throwable` can hide the exact exception type in some cases. Tests depend on MiniDFSCluster block placement honoring the intended SSD/DISK split.

Test signals: Useful regression signals include exact SSD/DISK consumed bytes after create/append/delete/truncate, expected `QuotaByStorageTypeExceededException` or `DSQuotaExceededException`, content summary type consumption, quota persistence after restart/checkpoint, snapshot retention/reclamation, and per-type quota clear semantics.
