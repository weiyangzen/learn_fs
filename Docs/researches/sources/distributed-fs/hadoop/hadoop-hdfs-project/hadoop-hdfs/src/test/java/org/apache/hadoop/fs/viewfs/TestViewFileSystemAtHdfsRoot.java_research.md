# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemAtHdfsRoot.java

## Purpose

`TestViewFileSystemAtHdfsRoot` runs the `ViewFileSystemBaseTest` contract when the HDFS root directory itself is the target test root. It verifies ViewFileSystem behavior when mount points resolve to `/`, which is a special case because setup must not delete the root path.

## Important APIs, types, and functions

The class extends `ViewFileSystemBaseTest` and overrides `createFileSystemHelper`, `setUp`, `initializeTargetTestRoot`, `getExpectedDelegationTokenCount`, and `getExpectedDelegationTokenCountWithCredentials`. It uses `MiniDFSCluster`, `FileSystem`, `FileStatus`, `DFS_NAMENODE_DELEGATION_TOKEN_ALWAYS_USE_KEY`, and `FileSystemTestHelper`.

## Control flow, state, and persistence

`@BeforeAll` starts a two-DN HDFS cluster with delegation tokens always enabled and stores `fHdfs`. Each test assigns `fsTarget = fHdfs` before invoking the base setup. The custom root initializer qualifies `/` and deletes only existing children, leaving the root intact. The inherited base test then creates and exercises ViewFS mounts.

## Dependencies and integration points

This integrates ViewFileSystem mount-table setup with an HDFS root target, HDFS delegation-token behavior, block support flags, and the reusable base contract for path creation/listing/rename/status/token behavior.

## Risks and test signals

Key risks are destructive root deletion during setup, incorrect path qualification for root-mounted targets, and duplicate delegation tokens for one underlying filesystem. Expected token count is one because all mount paths point to the same HDFS instance.
