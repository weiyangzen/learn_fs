# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsAtHdfsRoot.java

## Purpose

`TestViewFsAtHdfsRoot` runs the `ViewFsBaseTest` FileContext contract when the target HDFS root `/` is mounted into ViewFs. It is the FileContext counterpart to `TestViewFileSystemAtHdfsRoot`.

## Important APIs, types, and functions

The class extends `ViewFsBaseTest` and uses `MiniDFSCluster`, `HdfsConfiguration`, `FileContext`, `FileContextTestHelper`, `RemoteIterator<FileStatus>`, `DFS_NAMENODE_DELEGATION_TOKEN_ALWAYS_USE_KEY`, and inherited ViewFs base tests. It overrides `createFileContextHelper`, `setUp`, `initializeTargetTestRoot`, and `getExpectedDelegationTokenCount`.

## Control flow, state, and persistence

`@BeforeAll` enables always-use delegation tokens, starts a two-DN HDFS cluster, and gets a `FileContext` for the cluster URI. Per test, it assigns `fcTarget = fc` and runs base setup. The root initializer qualifies `/` and deletes only child paths through a `RemoteIterator`, preserving the root directory itself.

## Dependencies and integration points

This integrates FileContext/ViewFs mount-table behavior, HDFS root handling, delegation-token collection, and the base ViewFs operation contract.

## Risks and test signals

Risks are deleting the root during setup, mishandling root-qualified paths, or changing delegation-token expectations. The expected token count is eight under the inherited base mount layout with HDFS tokens enabled.
