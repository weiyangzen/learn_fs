<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestHDFSFileContextMainOperations.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestHDFSFileContextMainOperations.java

Purpose: Runs HDFS-specific FileContext main-operation tests beyond the generic base suite.
Important APIs/types/functions: `TestHDFSFileContextMainOperations` extends `FileContextMainOperationsBaseTest`; key tests cover truncate, quota-sensitive old/new rename, root rename errors, edits-log replay, invalid names, corrupted-block support, and cross-filesystem rename.
Control flow: Class setup starts a two-Datanode cluster and HDFS FileContext. Tests create files/directories via helper methods, manipulate quotas through `DistributedFileSystem`, execute `FileContext.rename` or legacy `FileSystem.rename`, restart the cluster without formatting to replay edits, and assert final namespace state.
State and persistence behavior: Static cluster and FileContext are shared; `restartCluster()` preserves storage with `format(false)` to validate edit-log persistence. Namespace and quota state are per-test helper roots where possible.
Dependencies and integration points: Integrates FileContext APIs with HDFS quota accounting, truncate, append verification, edit-log loading, `RemoteException` unwrapping, and URI scheme validation.
Risks and edge cases: Quota tests depend on exact namespace counts and overwrite semantics. Restarting the shared cluster can affect following tests if cleanup is incomplete. Root rename expectations rely on remote exception wrapping.
Test signals: Signals include file length/content after truncate, space consumed equals new length times replication, quota exceptions, src/dst existence after rename, successful edit-log replay after restart, invalid-name rejection, and IOException for cross-filesystem rename.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestHDFSFileContextMainOperations.java -->
