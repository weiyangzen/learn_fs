# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestRBWBlockInvalidation.java

## Purpose
`TestRBWBlockInvalidation` covers NameNode and DataNode behavior for replicas in RBW/RWR states when local files disappear, generation stamps diverge, or a DataNode restarts with an outdated replica. It protects against corrupt RBW replicas blocking re-replication and against deletion of good replicas when old-genstamp RWR replicas reappear.

## Important APIs, types, and functions
The tests use `MiniDFSCluster`, `FSDataOutputStream`, `DFSTestUtil`, `MaterializedReplica`, `FSNamesystem`, `BlockManager.countNodes`, `NumberReplicas`, `ExtendedBlock`, and HA helper `HATestUtil.waitForDNDeletions`. `RandomDeleterPolicy` is configured as the block placement policy in one regression test to avoid deterministic free-space ordering hiding bad deletion choices. `waitForNumTotalBlocks` repeatedly triggers block reports until the NameNode block total matches an expected value.

## Control flow
`testBlockInvalidationWhenRBWReplicaMissedInDN` skips Windows because file locking prevents deleting replica files. It starts a two-DataNode cluster, writes and hsyncs a replication-2 file, starts a third DataNode, deletes one DataNode's materialized RBW data and metadata files, closes the stream, then waits for live replicas to drop to one, rise back to two after re-replication, and finally for corrupt replica count to reach zero.

`testRWRInvalidation` opens ten replication-2 files, writes and flushes initial data, stops one pipeline DataNode, writes and flushes new data to the remaining node, lowers replication to one, and closes the files. After restarting the NameNode and DataNodes in an order that exposes old-genstamp replicas first, it computes invalidation work, triggers heartbeats and deletion reports, then verifies block totals and reads every file. `testRWRShouldNotAddedOnDNRestart` disables replacement on write failure, restarts a stopped DataNode after additional writes, and asserts the restarted old-generation node is absent from current block locations.

## State and persistence behavior
The file exercises on-disk DataNode replica files, replica states, generation stamps, block reports, corrupt replica tracking, invalidation queues, and replication counts. It indirectly tests persistence across NameNode restart in the RWR invalidation scenario. The crucial invariant is that older generation stamp replicas are invalidated without losing the only current data copy.

## Dependencies and integration points
These are MiniDFSCluster integration tests involving client write pipelines, DataNode replica storage, NameNode block reports, heartbeat-driven invalidation, and block placement policy. The first test depends on filesystem semantics that permit deleting replica files while the cluster is running.

## Risks and test signals
The strongest signals are live replica counts, corrupt replica counts, successful reads after invalidation, and block location membership. Risks include timing sensitivity from sleeps, block-report intervals, and platform-specific file locking. The tests catch regressions in RBW/RWR cleanup, corrupt replica accounting, generation-stamp comparison, and re-replication scheduling after partial replica loss.
