# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemLinkFallback.java

## Purpose

`TestViewFileSystemLinkFallback` is a broad `ViewFileSystem` test suite for `linkFallback` mount-table entries. It verifies that unresolved paths fall through to a configured target filesystem while explicit mount links and internal directories still shadow fallback entries correctly.

## Important APIs, types, and functions

The class extends `ViewFileSystemBaseTest` and uses `ConfigUtil.addLinkFallback`, `ConfigUtil.addLink`, `ViewFileSystem`, `MiniDFSCluster` with three federated namespaces, `FileSystem`, `FileStatus`, `FSDataOutputStream`, `FsPermission`, `FileAlreadyExistsException`, `NotInMountpointException`, and `LambdaTestUtils.intercept`. Key tests cover listing, mkdirs, create, unavailable fallback FS, root operations, mount-path conflicts, and symlink-style mount listing.

## Control flow, state, and persistence

Setup starts a three-namespace cluster, uses namespace 0 as root, and clears `/` children before each test. `setupMountPoints` installs inherited base mounts plus a default fallback. Individual tests build fresh configurations to model specific fallback trees, create real HDFS directories/files under `fallbackDir`, instantiate `viewfs://default` or named mount tables, and assert that list/create/mkdir operations either route to fallback or are blocked by mount/internal directory semantics.

## Dependencies and integration points

This file integrates ViewFS inode-tree resolution, link fallback, regular mount links, mount-link-as-symlink display, HDFS permissions, create/mkdir/listStatus routing, and failure handling when NameNodes are stopped. It also exercises `Path.mergePaths` expectations between view paths and fallback targets.

## Risks and test signals

Risks include leaking fallback entries that should be shadowed by explicit mounts, using link permissions instead of target permissions, failing to create parent structures in fallback, creating files over internal directories, or hiding fallback roots from listings. Test signals are exact listed path sets, `FileAlreadyExistsException`, `NotInMountpointException`, fallback HDFS existence checks, and failure/recovery when fallback NameNodes are stopped and restarted.
