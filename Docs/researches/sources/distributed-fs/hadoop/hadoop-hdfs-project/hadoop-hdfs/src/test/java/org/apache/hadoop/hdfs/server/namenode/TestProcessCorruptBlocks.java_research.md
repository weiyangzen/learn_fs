# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestProcessCorruptBlocks.java

Purpose: Tests NameNode/block manager processing of corrupt replicas, ensuring corrupt replicas are removed only when enough good replicas exist and are retained when all replicas are corrupt.

Important APIs and functions: Tests create files with `DFSTestUtil.createFile`, get the first `ExtendedBlock`, corrupt replicas through `corruptBlock`, and inspect `BlockManager.countNodes` via `countReplicas`. They use `FSNamesystem.setReplication`, `DFSTestUtil.waitReplication`, `MiniDFSCluster.stopDataNode/restartDataNode`, materialized replica truncation, and `DataNodeTestUtils.runDirectoryScanner`.

Control flow: Decreasing-replication tests corrupt one replica, wait until two good replicas remain, then lower replication to two or one and assert corrupt replicas are removed. Extra-DataNode test starts with four DataNodes, stops one, corrupts a replica among the three active nodes, then restarts the fourth to create a new good replica and remove the corrupt one. All-corrupt test corrupts all replicas, lowers replication, and asserts corrupt replicas remain because no good copy exists.

State and persistence behavior: Block replica state is persisted on DataNode storage files and reported to the NameNode through scans, restarts, and block reports. NameNode block maps track live and corrupt replica counts.

Dependencies and integration points: Integrates DataNode directory scanner, block reports, MiniDFSCluster materialized replicas, block manager replica accounting, reconstruction timeout configuration, and replication changes.

Risks: `corruptBlock` always truncates the materialized replica at DataNode index 0 before using `dnIndex` for log cleanup, so the comments note index changes after restarts. Tests rely on sleeps and short block report intervals. Corrupt replica removal timing can vary with block report processing.

Test signals: Passing means corrupt replica counts remain while good replicas are below replication, drop to zero once good replicas meet replication, new DataNode replication cleans corruption, and all-corrupt blocks are preserved.
