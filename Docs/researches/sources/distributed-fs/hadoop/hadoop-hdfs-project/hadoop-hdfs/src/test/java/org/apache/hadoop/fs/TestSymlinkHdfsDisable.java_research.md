<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfsDisable.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfsDisable.java

Purpose: Verifies that disabling remote symlink resolution blocks both FileContext and DistributedFileSystem link opens.
Important APIs/types/functions: `TestSymlinkHdfsDisable.testSymlinkHdfsDisable()`.
Control flow: The test disables `FS_CLIENT_RESOLVE_REMOTE_SYMLINKS_KEY`, starts a MiniDFSCluster, creates a target file and HDFS symlink, then attempts `fc.open(link)` and `dfs.open(link)` expecting errors.
State and persistence behavior: State is a single cluster, one target file, and one symlink; the cluster is not shut down in a finally block in the visible code.
Dependencies and integration points: Depends on HDFS symlink resolution configuration, `DFSTestUtil`, FileContext, and DistributedFileSystem.
Risks and edge cases: Missing `finally` cleanup is a resource leak risk if assertions fail. The expected error is matched by substring `resolution is disabled`.
Test signals: Signals are IOException failures for both FileContext and DFS open paths when symlink resolution is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfsDisable.java -->
