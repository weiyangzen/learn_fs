# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestNNStartupWhenViewFSOverloadSchemeEnabled.java

## Purpose

This test ensures NameNode startup still succeeds when the `hdfs` scheme is overloaded to `ViewFileSystemOverloadScheme`. It covers both HA and non-HA `MiniDFSCluster` startup, including a nonzero trash interval to trigger TrashEmptier initialization during NameNode service startup.

## Important APIs, types, and functions

Important pieces are `ViewFileSystemOverloadScheme`, `DistributedFileSystem`, `MiniDFSCluster`, `MiniDFSNNTopology.simpleHATopology`, `FsConstants.FS_VIEWFS_OVERLOAD_SCHEME_TARGET_FS_IMPL_PATTERN`, `fs.%s.impl`, and HDFS/IPC/trash configuration keys. Tests are `testHANameNodeAndDataNodeStartup` and `testNameNodeAndDataNodeStartup`.

## Control flow, state, and persistence

`@BeforeAll` mutates a static configuration so `fs.hdfs.impl` resolves to the overload scheme and the target implementation resolves to `DistributedFileSystem`. Each test builds a zero-DN cluster with safe mode waiting disabled, waits active, and in the HA case transitions NameNode 0 active. `@AfterEach` shuts down the cluster. There is no persistent state beyond cluster process state.

## Dependencies and integration points

The test integrates the FileSystem implementation registry, ViewFS overload-scheme target lookup, NameNode/HA startup code, IPC retry behavior, and TrashEmptier initialization. It protects against startup code that assumes `hdfs` always maps directly to `DistributedFileSystem`.

## Risks and test signals

The main regression signal is startup failure, hang, or HA transition failure when scheme overloading is enabled. The test is intentionally coarse: it does not perform file operations, so it isolates initialization compatibility rather than runtime ViewFS routing.
