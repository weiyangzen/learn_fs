# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMissingBlocksAlert.java

## Purpose
This file tests NameNode accounting and alerting for missing blocks, including JMX attributes backing the NameNode UI, and verifies replication progress when rack topology changes under `AvailableSpaceBlockPlacementPolicy`.

## Important APIs, Types, And Functions
`testMissingBlocksAlert` creates files, corrupts replicas with `MiniDFSCluster.corruptReplica`, forces checksum reporting by reading through `FSDataInputStream`, checks `DistributedFileSystem` missing/low-redundancy counters, inspects `BlockManager.getUnderReplicatedNotMissingBlocks`, and reads `NameNodeInfo` MBean attributes. `testMissReplicatedBlockwithTwoRack` creates a one-rack cluster, adds another rack, raises replication, and waits for replication.

## Control Flow
The missing-block test starts a single-DataNode cluster with small blocks and fast redundancy checks, creates a normal under-replicated file and a corrupt file, corrupts the first block, reads it to trigger a checksum failure report, waits for missing block count, and validates DFS and JMX counters. It deletes the corrupt file to ensure counters return to zero for missing blocks, then repeats with replication factor one to validate the special missing-repl-one counter.

## State And Persistence
State under test is in-memory NameNode block health accounting: missing blocks, missing replication-one blocks, low-redundancy blocks, and under-replicated-but-not-missing blocks. No restart persistence is tested. The second test exercises rack-aware replication state after adding DataNodes on a new rack.

## Dependencies And Integration Points
Dependencies include `MiniDFSCluster`, `DFSTestUtil`, `ChecksumException`, `ExtendedBlock`, `BlockManager`, JMX `MBeanServer`, `ObjectName` for `Hadoop:service=NameNode,name=NameNodeInfo`, and `AvailableSpaceBlockPlacementPolicy`.

## Risks
The first test polls with sleeps instead of bounded `waitFor` in places, so a counter bug can hang until the test framework timeout. Corruption only occurs on one DataNode, making behavior tightly coupled to single-replica/missing logic. JMX attribute names are externally visible contracts and failures may indicate either NameNode accounting or MXBean exposure regressions.

## Test Signals
Signals are missing block count reaching one, low-redundancy/under-replicated counts matching expected normal-plus-corrupt files, JMX `NumberOfMissingBlocks` and `NumberOfMissingBlocksWithReplicationFactorOne` matching DFS counters, counters returning after delete, and successful replication to factor three after adding a second rack.
