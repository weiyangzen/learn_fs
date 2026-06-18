# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestNodeCount.java

## Purpose
`TestNodeCount` verifies that `BlockManager.countNodes` reports live and excess replica counts correctly as datanodes fail, rejoin, and cause over-replication. The namenode uses these counts to decide under- and over-replication actions.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `FSNamesystem`, `BlockManager`, `HeartbeatManager`, `NumberReplicas`, `BlockManagerTestUtil.noticeDeadDatanode`, and helper methods `initializeTimeout`, `checkTimeout`, and `countNodes`.

## Control Flow
The test starts two datanodes, creates a one-block replicated file, records descriptors, starts two additional datanodes, stops one original datanode, forces the namenode to notice the dead node, and waits for replication to return to the target factor. It restarts the failed node, waits for at least one excess replica, chooses a non-excess datanode holding the block, stops that node, waits for live replicas to equal the factor, restarts it, and waits for excess replicas to reach two.

## State and Persistence Behavior
State includes live datanode membership, block replica locations, excess replica tracking, and block-manager counts under the block-manager read lock. The test delays startup block deletion to avoid invalidation races.

## Dependencies and Integration Points
This is a MiniDFSCluster integration test for the block manager, heartbeat manager, dead-node detection, replication monitor, and excess-replica bookkeeping.

## Risks and Edge Cases
It covers races between dead-node detection, replication, datanode rejoin, and excess marking. The timeout helpers include last observed count data to diagnose stuck count transitions.

## Test Signals
Signals are successful replication waits, non-null selection of a non-excess datanode, live replica count equaling the replication factor after a stop, and excess replica count becoming one and then two after datanode restarts.
