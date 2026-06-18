# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemLinkMergeSlash.java

## Purpose

`TestViewFileSystemLinkMergeSlash` verifies ViewFileSystem mount tables that use `linkMergeSlash`, where the mount-table root is merged directly with a target filesystem root. It checks basic file access, invalid mixed configuration, invalid sub-mount syntax, and child filesystem reporting.

## Important APIs, types, and functions

The class extends `ViewFileSystemBaseTest` and uses `ConfigUtil.addLinkMergeSlash`, `ConfigUtil.addLink`, `MiniDFSCluster`, `DistributedFileSystem`, `FileSystem`, `FileStatus`, `FsConstants.VIEWFS_SCHEME`, and `ViewFileSystem`. The key tests are `testConfLinkMergeSlash`, `testConfLinkMergeSlashWithRegularLinks`, `testConfLinkMergeSlashWithMountPoint`, and `testChildFileSystems`.

## Control flow, state, and persistence

Setup creates a three-namespace MiniDFSCluster, picks namespace 0, clears root children before each test, and configures two named merge-slash mount tables in inherited setup. The tests also use a local `TEST_DIR` fixture to write a file, then mount that directory as merge slash and resolve it through `viewfs://ClusterMerge/`.

## Dependencies and integration points

This integrates ViewFS mount-table parsing, merge-slash exclusivity rules, child filesystem tracking, local filesystem targets, and HDFS target reporting. It protects the invariant that a mount table cannot combine merge slash with regular links and that merge slash must be rooted, not path-qualified.

## Risks and test signals

Regression signals are successful initialization for invalid mixed mount tables, acceptance of `linkMergeSlash./user`, wrong target child count, or non-`DistributedFileSystem` child type for the HDFS-backed setup. The basic access test signals that root path merging still resolves target files.
