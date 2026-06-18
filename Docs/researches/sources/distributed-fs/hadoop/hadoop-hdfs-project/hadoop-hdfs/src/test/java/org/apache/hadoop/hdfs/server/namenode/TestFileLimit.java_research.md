<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileLimit.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileLimit.java

Purpose: `TestFileLimit` verifies NameNode filesystem object limits, maximum blocks per file, and minimum block size enforcement in real mini clusters, including a simulated storage variant for the object-limit test.

Important APIs, types, and functions: it uses `DFS_NAMENODE_MAX_OBJECTS_KEY`, `DFS_BLOCKREPORT_INTERVAL_MSEC_KEY`, `DFS_HEARTBEAT_INTERVAL_KEY`, `DFS_NAMENODE_MAX_BLOCKS_PER_FILE_KEY`, `DFS_NAMENODE_MIN_BLOCK_SIZE_KEY`, `MiniDFSCluster`, `FSNamesystem.getBlocksTotal`, `FSDirectory.totalInodes`, `DFSTestUtil.createFile`, `SimulatedFSDataset.setFactory`, and `HdfsDataOutputStream.hflush`. `waitForLimit` polls until block plus inode counts reach the expected total.

Control flow: `testFileLimit` configures a low object limit, creates enough files to consume root inode plus file/block objects, asserts another file creation fails, deletes a file and waits for counts to drop, recreates it, deletes again, creates two directories in its place, and asserts a further mkdir fails. `testFileLimitSimulated` toggles `simulatedStorage` and reruns the same flow. `testMaxBlocksPerFileLimit` writes exactly the configured block count, flushes, then writes one more byte and expects an IOException containing the max-blocks message. `testMinBlockSizeLimit` creates with the minimum allowed block size, then expects failure for one byte below minimum.

State and persistence behavior: state is live NameNode inode/block accounting and cluster block reports/heartbeats. The tests do not restart the cluster; they wait for asynchronous block count changes after deletion.

Dependencies and integration points: depends on mini cluster block reporting, FSNamesystem quota/object accounting, DataNode simulated dataset factory, HDFS create/write/flush APIs, and exception message text.

Risks and edge cases: `waitForLimit` is an unbounded polling loop with `Thread.sleep`, so a count regression can hang until the test framework kills it. `simulatedStorage` is an instance field toggled around a direct method call; a failure before reset can affect later state in the same instance. The file-limit test catches broad `IOException` and only checks that an exception happened, not the specific limit type.

Test signals: successful creation up to limit, failure past limit, count drop after delete, success after freeing capacity, max-blocks exception after extra write/flush, and minimum-block-size exception text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileLimit.java -->
