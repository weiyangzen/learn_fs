# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestViewDistributedFileSystemContract.java

Purpose: Runs the HDFS filesystem contract against `ViewDistributedFileSystem`, with mount-table setup that maps `/user` and fallback to the underlying MiniDFSCluster.

Important APIs and types: `TestHDFSFileSystemContract`, `MiniDFSCluster`, `FileSystemContractBaseTest.TEST_UMASK`, `ConfigUtil.addLink`, `ConfigUtil.addLinkFallback`, `ViewDistributedFileSystem`, `UserGroupInformation`, and `LambdaTestUtils.intercept`.

Control flow: Static `init` creates a randomized-base MiniDFSCluster with two datanodes and records the expected default working directory. `setUp` installs `fs.hdfs.impl` as ViewDFS, extracts the default HDFS URI from config, maps `/user` to that URI, adds fallback, and opens `fs`. `getDefaultWorkingDirectory` returns the recorded `/user/<shortname>`. `testRenameRootDirForbidden` delegates to the superclass root rename test but expects `AccessControlException` because ViewFS internal directories are read-only.

State and persistence behavior: Contract tests mutate HDFS namespace through the ViewDFS wrapper. The mount table is in-memory configuration. Static cluster persists for the class and shuts down in `@AfterAll`.

Dependencies and integration points: Integrates HDFS contract tests, ViewDFS mount-table routing, default working-directory semantics, permissions umask, and special ViewFS internal-dir protection.

Risks and test signals: Most behavior is inherited, so failures can arise from superclass assumptions about root handling. Passing signals ViewDFS satisfies HDFS contract expectations except for intentionally forbidden root internal-dir rename.
