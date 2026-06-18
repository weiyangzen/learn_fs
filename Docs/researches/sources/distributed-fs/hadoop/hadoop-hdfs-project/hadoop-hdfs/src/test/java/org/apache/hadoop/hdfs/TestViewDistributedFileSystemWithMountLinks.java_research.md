# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestViewDistributedFileSystemWithMountLinks.java

Purpose: Extends ViewFS overload-scheme tests with HDFS-scheme `ViewDistributedFileSystem` and explicit mount-link/fallback rename scenarios.

Important APIs and types: `TestViewFileSystemOverloadSchemeWithHdfsScheme`, `ViewDistributedFileSystem`, `ConfigUtil.addLinkFallback`, `ViewFsTestSetup.addMountLinksToConf`, `CONFIG_VIEWFS_IGNORE_PORT_IN_MOUNT_TABLE_NAME`, `DistributedFileSystem.initialize`, and `FileSystem.rename`.

Control flow: `setUp` calls the superclass setup, forces delegation tokens, short IPC retry count, HDFS implementation to ViewDFS, default ignore-port setting, and fallback link for the default HDFS authority. It reuses superclass helpers for create-on-root and nonexistent-link tests. `testRenameOnInternalDirWithFallback` creates mount links and matching fallback directories, then verifies renames among root fallback paths, internal mount parents, and mount targets. `testRenameWhenDstOnInternalDirWithFallback` validates successful destination handling when fallback structure exists and a false result when an internal destination has no corresponding fallback directory.

State and persistence behavior: Mount-link config is in memory; target directories and files are created in the MiniDFSCluster namespace. `verifyRename` checks source removal and destination existence.

Dependencies and integration points: Integrates viewfs mount-table resolution, fallback routing, HDFS-scheme overloading, delegation-token behavior, and rename implementation across internal dirs and real DFS paths.

Risks and test signals: Rename expectations depend on fallback namespace mirroring internal mount structure. Passing signals ViewDFS correctly falls back for root/internal-dir renames and fails cleanly when fallback cannot resolve the destination.
