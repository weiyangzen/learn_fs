<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfs.java

Purpose: Base class for HDFS symlink behavior tests shared by FileSystem and FileContext wrappers.
Important APIs/types/functions: `TestSymlinkHdfs` extends `SymlinkBaseTest`; overrides scheme/base dirs/URI/exception unwrapping and defines tests for cross-FS links, rename across FS, slash links, target-affecting metadata operations, partial URI rejection, replication through links, max path length, WebHDFS symlink creation, owner, and quota.
Control flow: Class setup starts HDFS with umask 000 and disabled max-component length, opens WebHDFS and DFS handles, and subclasses set the wrapper. Tests create files/links through wrapper APIs and verify reads/status/metadata. Quota and WebHDFS cases call HDFS-specific APIs directly.
State and persistence behavior: Static MiniDFSCluster, WebHDFS FS, and DFS handles persist across subclasses. Namespace changes occur under `/test1` and `/test2`; base class cleanup behavior is inherited.
Dependencies and integration points: Integrates HDFS symlink implementation, `SymlinkBaseTest`, FileSystem/FileContext wrappers, WebHDFS, quota enforcement, path-length limits, and RemoteException unwrapping.
Risks and edge cases: Subclass wrapper selection changes behavior; FileSystem disables some inherited tests. Cross-filesystem rename expects different exception classes by wrapper type. Shared static cluster can leak namespace/quota state if base cleanup misses a path.
Test signals: Signals include successful reads through symlinks, failed cross-FS renames, unchanged link metadata when target permissions/owner change, replication target updates, path too long failure, WebHDFS link behavior, and quota exception on excess symlink creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfs.java -->
