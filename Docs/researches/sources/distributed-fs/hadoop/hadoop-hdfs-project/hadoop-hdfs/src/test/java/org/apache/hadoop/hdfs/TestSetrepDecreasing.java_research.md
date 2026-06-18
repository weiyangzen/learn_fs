# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSetrepDecreasing.java

Purpose: Minimal wrapper test for decreasing HDFS file replication through the shared `TestSetrepIncreasing.setrep` helper.

Important APIs and types: JUnit `@Test`, `@Timeout`, and `TestSetrepIncreasing.setrep`.

Control flow: The sole test method `testSetrepDecreasing` calls `setrep(5, 3, false)`, which creates a MiniDFSCluster, writes a file, runs `FsShell -setrep -w`, and validates resulting block-location host counts.

State and persistence behavior: All state is delegated to the helper: a temporary MiniDFSCluster, HDFS test path `/test/setrep5-3`, and a file whose replication factor is changed from 5 to 3.

Dependencies and integration points: Depends directly on the increasing test helper and indirectly on FsShell replication command handling, NameNode replication tracking, block reports, and `DistributedFileSystem.getFileBlockLocations`.

Risks and test signals: Because this class is only a wrapper, any failure points to helper behavior or setrep semantics rather than local code. Passing signals that reducing replication through `-setrep -w` converges to the requested replica count within the timeout.
