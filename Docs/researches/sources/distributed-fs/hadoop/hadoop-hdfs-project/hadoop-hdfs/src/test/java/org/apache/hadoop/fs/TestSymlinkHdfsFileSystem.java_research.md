<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfsFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfsFileSystem.java

Purpose: Runs HDFS symlink tests through a FileSystem wrapper and adds DFS-only symlink operation coverage.
Important APIs/types/functions: `TestSymlinkHdfsFileSystem` extends `TestSymlinkHdfs`; disables two inherited tests; adds `testRecoverLease()`, `testIsFileClosed()`, `testConcat()`, and `testSnapshot()`.
Control flow: Setup installs `FileSystemTestWrapper`. Added tests create symlinks to files or directories, then call DFS-only APIs through link paths: lease recovery, file-closed status, concat target/srcs, and snapshot allow/create/rename/delete.
State and persistence behavior: Uses shared HDFS cluster and DFS handle. Snapshot and concat tests mutate namespace under symlinked directories.
Dependencies and integration points: Integrates symlink resolution with `DistributedFileSystem` lease, concat, and snapshot APIs.
Risks and edge cases: Two inherited tests are disabled because FileSystem fills URI authority and creates parents differently. DFS-only operations must resolve links consistently without changing link status.
Test signals: Signals are true lease/file-closed results and no exception during concat and snapshot operations through link paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfsFileSystem.java -->
