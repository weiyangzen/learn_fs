# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSRemove.java

Purpose: This integration test checks that deleting files releases DataNode disk usage after block deletion has propagated.

Important APIs/types/functions: `MiniDFSCluster`, `FileSystem.delete`, `DataNodeTestUtils.getFSDataset`, `FsDatasetSpi.getDfsUsed`, and helper methods `createFile` and `getTotalDfsUsed`.

Control flow: The test starts a two-DataNode cluster, creates `/test/remove/`, records aggregate DFS used, creates 100 small files, records peak usage, deletes all files non-recursively, sleeps for three default heartbeat intervals to allow block deletion, then asserts final aggregate usage equals the starting value.

State and persistence behavior: It writes and deletes real block files on DataNode storage. The observed state is physical dataset usage across all DataNodes, not only NameNode namespace state.

Dependencies and integration points: It depends on DataNode storage accounting, block invalidation/deletion after namespace delete, and heartbeat-driven cleanup timing.

Risks and test signals: The main signal is equality of aggregate DataNode DFS-used before and after the create/delete cycle. The test is timing-sensitive because it uses a fixed sleep based on heartbeat interval rather than an explicit wait-for-condition loop. Small-file metadata or storage accounting changes could affect exact equality.
