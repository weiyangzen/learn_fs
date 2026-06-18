<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/HDFSContract.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/HDFSContract.java

Purpose: Defines the HDFS filesystem contract used by Hadoop's generic contract test suite.
Important APIs/types/functions: `HDFSContract`, `CONTRACT_HDFS_XML`, `BLOCK_SIZE`, static `createCluster()`, `destroyCluster()`, `getCluster()`, and overrides `init()`, `getTestFileSystem()`, `getScheme()`, `getTestPath()`.
Control flow: The contract loads `contract/hdfs.xml`, starts a two-Datanode MiniDFSCluster with block size equal to the abstract test file length, asserts contract options loaded, and returns the cluster FileSystem for tests.
State and persistence behavior: A static MiniDFSCluster is shared by contract test classes and destroyed after each class. Test path root is `/test`.
Dependencies and integration points: Integrates contract option XML, `AbstractFSContract`, MiniDFSCluster, and HDFS FileSystem.
Risks and edge cases: Static cluster lifecycle requires every contract test class to pair create/destroy. Block-size override affects tests that assume normal HDFS defaults.
Test signals: Signals are inherited contract tests creating the cluster, loading case-sensitivity options, and operating against `hdfs` scheme.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/HDFSContract.java -->
