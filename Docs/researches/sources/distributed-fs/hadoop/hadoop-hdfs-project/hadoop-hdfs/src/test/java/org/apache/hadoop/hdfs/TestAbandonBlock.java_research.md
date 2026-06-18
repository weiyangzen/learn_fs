# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestAbandonBlock.java

## Purpose
`TestAbandonBlock` verifies NameNode block-abandon behavior used when DFS clients fail pipeline creation or lose a DataNode while writing. It checks both idempotent abandon semantics and quota accounting.

## Important APIs, Types, and Functions
- `setUp()` creates a two-DataNode MiniDFSCluster and obtains a `DistributedFileSystem`.
- `tearDown()` closes the filesystem and shuts down the cluster.
- `testAbandonBlock()` writes an unclosed file, flushes it, obtains the file ID from `DFSOutputStream`, calls `ClientProtocol.abandonBlock` twice for the last block, closes the file, restarts the NameNode, and checks the block count dropped by one.
- `testQuotaUpdatedWhenBlockAbandoned()` sets a disk-space quota, writes with replication two, shuts down one DataNode, and ensures close does not throw `QuotaExceededException` when abandonment reallocates space.

## Control Flow
Each test starts from a fresh cluster. The first test creates a partial block, flushes it so the NameNode knows about it, fetches located blocks, abandons the last located block twice to prove idempotence, then closes and restarts the NameNode to verify the abandoned block is not persisted in namespace state. The quota test forces a write pipeline disruption by shutting down a DN, then closes the stream and fails if quota accounting still includes abandoned pending space.

## State and Persistence Behavior
The tests mutate HDFS namespace and block state. `testAbandonBlock` explicitly checks persistence by restarting the NameNode before re-reading block locations. `testQuotaUpdatedWhenBlockAbandoned` mutates root quota and live DN state. Local test cluster state is cleaned up in `tearDown`.

## Dependencies and Integration Points
Dependencies include MiniDFSCluster, `DistributedFileSystem`, `DFSClientAdapter`, `DFSOutputStream`, NameNode `ClientProtocol`, `LocatedBlocks`, `LocatedBlock`, HDFS quota constants, and JUnit lifecycle/assertions.

## Risks and Edge Cases
- The first test keeps using the original `DFSClient` after restarting the NameNode; cached RPC behavior must reconnect correctly.
- The assertion compares original block count to post-restart count plus one, so it is sensitive to additional block allocation during close.
- Quota behavior depends on pipeline failure induced by direct `DataNode.shutdown`, not `cluster.stopDataNode`, so MiniDFSCluster's bookkeeping still includes the DN.

## Test Signals
Passing signals: duplicate `abandonBlock` calls are harmless; abandoned blocks disappear after NameNode restart; quota is decremented for abandoned pending blocks and does not fail stream close.
