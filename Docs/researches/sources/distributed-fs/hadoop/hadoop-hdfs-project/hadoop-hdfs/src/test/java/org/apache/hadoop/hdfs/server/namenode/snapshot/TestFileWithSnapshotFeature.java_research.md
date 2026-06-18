# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestFileWithSnapshotFeature.java

Purpose: Unit-tests `FileWithSnapshotFeature.updateQuotaAndCollectBlocks` quota/block accounting without running a cluster.

Important APIs/types/functions: uses `FileDiffList`, `FileWithSnapshotFeature`, `FileDiff`, `INodeFile`, `INode.ReclaimContext`, `QuotaCounts`, `BlockInfoContiguous`, `BlockStoragePolicySuite`, `BlockStoragePolicy`, Mockito spies/mocks, and `Whitebox.setInternalState` to set replication encoded in inode headers.

Control flow: `testUpdateQuotaAndCollectBlocks` first checks a no-snapshot case where quota delta remains zero. It then injects a snapshot inode with replication 3 while the live file prefers replication 1 and mocks storage policy choices of SSD vs DISK; updating quota should account for the replication/storage-type delta. `testUpdateQuotaDistinctBlocks` tests whether removed file-diff blocks are charged only when distinct from current file blocks and remaining diffs.

State and persistence behavior: purely in-memory; state is mocked or constructed. No fsimage/edit-log path is involved.

Dependencies and integration points: targets block management, storage policy selection, namespace quota delta accumulation, and snapshot file-diff internals.

Risks and test signals: precise for quota arithmetic and duplicate-block avoidance. Mocking internal headers/storage policies can diverge from production construction paths, so this complements but does not replace integration tests.
