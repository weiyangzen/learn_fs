# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestUnderReplicatedBlocks.java

Purpose: this test class exercises NameNode block-replication scheduling edge cases around under-replicated blocks and per-DataNode replication work limits.

Important APIs and types: `MiniDFSCluster`, `BlockManager`, `BlockManagerTestUtil`, `DFSTestUtil`, `FsShell`, `DatanodeDescriptor`, `DatanodeStorageInfo`, `DataNodeTestUtils`, and `Whitebox`. It uses direct block-map manipulation, invalidate scheduling, heartbeat triggering, and shell `-setrep`.

Control flow: `testSetRepIncWithUnderReplicatedBlocks` creates a replicated file, schedules invalidation for one replica, triggers DataNode heartbeat so deletion occurs, removes the same DataNode from `blocksMap`, and then runs `hdfs dfs -setrep -w` to increase replication. The test verifies client stats after each internal state mutation, ensuring a block that is under-replicated but not queued still tolerates replication-factor changes. `testNumberOfBlocksToBeReplicated` creates ten tiny blocks on two DataNodes, starts a third node, removes one source DataNode, computes replication work, and asserts the remaining source DataNode's queued replication count does not exceed the hard stream limit.

State and persistence: both tests use real MiniDFSCluster storage and NameNode metadata, then intentionally mutate in-memory NameNode `blocksMap`, invalidation queues, and DataNode descriptors. Heartbeat interval and replication-work multiplier are adjusted to keep pending work observable during the assertion window.

Dependencies and integration points: these tests are tightly coupled to `BlockManager` internals, DataNode heartbeat behavior, replication queues, and shell-facing replication changes. They are not pure black-box tests; they validate consistency under internal state that can occur during race windows.

Risks: direct use of `bm.blocksMap`, `removeNode`, `Whitebox.getInternalState`, fixed sleep, and DataNode lookup by IPC port makes the tests sensitive to implementation changes. The first test deletes metadata from the block map after a real invalidation flow, which is useful but nonstandard state.

Test signals: passing tests indicate robust handling of stale under-replicated accounting and enforcement of replication scheduling backpressure. Failures suggest NameNode replication work queues may over-assign, lose under-replication, or mishandle `setrep` after replica invalidation.
