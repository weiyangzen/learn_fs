# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestViewDistributedFileSystem.java

Purpose: Extends the normal `TestDistributedFileSystem` suite while substituting `ViewDistributedFileSystem`, and adds ViewDFS-specific tests for path handles, delegation tokens, rename options, quotas, path capabilities, and safe mode APIs.

Important APIs and types: `ViewDistributedFileSystem`, `ConfigUtil.addLinkFallback`, `ConfigUtil.addLink`, `PathHandle`, `Options.Rename`, `CommonPathCapabilities.FS_TRUNCATE`, `LEASE_RECOVERABLE`, `LeaseRecoverable`, `SafeMode`, `SafeModeAction`, and deprecated `HdfsConstants.SafeModeAction`.

Control flow: `getTestConfiguration` maps `fs.hdfs.impl` to ViewDFS. `testStatistics` resets ViewDFS statistics thread-local state before invoking the superclass test. Other tests start MiniDFSClusters, configure fallback/mount links, and validate opening by path handle, empty delegation token handling, rename with options through fallback and mount entries, quota setting through ViewDFS reflected in real DFS, path capabilities/interfaces, and safe mode transitions through both new and deprecated APIs.

State and persistence behavior: State is temporary HDFS namespace data, mount-table configuration, statistics thread-local data, quota metadata, and NameNode safe-mode state. Each cluster is closed inside tests.

Dependencies and integration points: Integrates ViewDFS overload of the HDFS scheme, fallback links, mount entries, DFS admin APIs routed through ViewDFS, inherited DFS contract behavior, and compatibility APIs.

Risks and test signals: The statistics test uses Whitebox reflection on internal thread-local state. Passing signals ViewDFS preserves expected DistributedFileSystem behavior while exposing HDFS-specific capabilities and administrative operations through viewfs routing.
