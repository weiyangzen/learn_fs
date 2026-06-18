# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestOverReplicatedBlocks.java

## Purpose
`TestOverReplicatedBlocks` validates over-replication handling: corrupt replicas must not be treated as valid deletion candidates, stale-heartbeat datanodes should be preferred for deletion scheduling, and partial blocks should be invalidated when replication is lowered.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `DFSTestUtil`, `BlockManager`, `HeartbeatManager`, `NameNodeAdapter.setReplication`, `InternalDataNodeTestUtils`, `BlockManager.countNodes`, `getExcessSize4Testing`, and datanode storage utilization test hooks.

## Control Flow
`testProcesOverReplicateBlock` creates a three-replica file, corrupts one replica, restarts the datanode to detect corruption, lowers replication to one, and checks a live valid replica remains. `testChooseReplicaToDelete` creates a four-replica file, adds a datanode with rare heartbeats, waits beyond the tolerable heartbeat interval, lowers replication, and verifies all excess deletions are scheduled on the stale datanode without actual deletion. `testInvalidateOverReplicatedBlock` writes and syncs a partial block at replication two, lowers replication to one before close, and verifies one live replica remains.

## State and Persistence Behavior
State includes corrupt replica metadata, storage utilization values, stale heartbeat timestamps, excess replica queues, and live replica counts. Cluster block data is temporary.

## Dependencies and Integration Points
The file integrates block scanning/corrupt detection, over-replication deletion choice, heartbeat freshness, replication-factor changes, partial-block finalization, and excess replica tracking.

## Risks and Edge Cases
Risks include deleting valid replicas while keeping corrupt ones, deleting from healthy datanodes instead of stale ones, or failing to invalidate excess replicas for a block still open or partially written.

## Test Signals
Assertions check live replica counts after corrupt over-replication processing, excess queue size for the stale datanode, unchanged block-location replica counts before stale heartbeat deletion can occur, and one live replica after partial-block replication reduction.
