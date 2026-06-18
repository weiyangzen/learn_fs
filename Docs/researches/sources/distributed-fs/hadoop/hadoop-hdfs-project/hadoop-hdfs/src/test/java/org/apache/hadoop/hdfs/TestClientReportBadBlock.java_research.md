<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestClientReportBadBlock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestClientReportBadBlock.java

Purpose: Tests when a DFS client should report corrupt block replicas to the NameNode: always for a single replica, only for partial corruption when some replicas remain good, and not when all replicas of a multi-replica block are corrupt from the client's perspective.

Important APIs, types, and functions: `DFSTestUtil.createFile/waitReplication`, `MiniDFSCluster.corruptReplica`, `DFSInputStream.read`, positioned `read`, `ChecksumException`, `BlockMissingException`, `getBlockLocations`, `LocatedBlock.isCorrupt`, `NamenodeFsck`, `DFSck`, and `ToolRunner`.

Control flow: Each test creates a one-block file and corrupts selected replicas. `testOneBlockReplica` corrupts the only replica and exercises sequential and positioned reads, expecting the block to be marked corrupt and fsck to report corruption. `testCorruptAllOfThreeReplicas` corrupts all replicas and expects the client not to report them as corrupt to the NameNode, leaving fsck healthy. `testCorruptTwoOutOfThreeReplicas` corrupts two replicas, rereads until only the good replica remains in block locations, then checks fsck reports under-replication but not corrupt-file listing. Helpers verify replica counts, corrupt flags, read behavior, and fsck output/error codes.

State and persistence behavior: DataNode replica files are corrupted on disk via cluster test hooks. NameNode corrupt-replica state changes only when the client reports bad replicas during reads. The tests disable the block scanner so client reporting is the primary signal.

Dependencies and integration points: Integrates client checksum verification and bad-block reporting, NameNode located-block filtering, fsck health/corrupt-file reporting, DataNode replica corruption, and retry timing.

Risks: The partial-corruption test loops because MiniDFSCluster block-location ordering is pseudo-random by network distance; this can be slow if the good replica is not tried promptly. The expected policy is subtle: all-corrupt multi-replica reads should not report, while one-replica all-corrupt should.

Test signals: Success means located-block corrupt flags, returned replica counts, fsck health strings, and fsck error codes match the reporting policy after client read attempts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestClientReportBadBlock.java -->
