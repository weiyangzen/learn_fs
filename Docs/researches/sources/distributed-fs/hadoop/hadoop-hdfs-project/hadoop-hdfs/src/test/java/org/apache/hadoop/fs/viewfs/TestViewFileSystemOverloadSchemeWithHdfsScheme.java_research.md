# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemOverloadSchemeWithHdfsScheme.java

## Purpose

`TestViewFileSystemOverloadSchemeWithHdfsScheme` is the main test suite for replacing the `hdfs` scheme implementation with `ViewFileSystemOverloadScheme`. It verifies mount links to HDFS and local filesystems, nonexistent targets, root listing and root create semantics, fallback links, authority-free `viewfs:/` access, target implementation validation, inner-cache behavior, Nfly rename/read/repair, and port-insensitive mount-table names.

## Important APIs, types, and functions

Important types and APIs include `MiniDFSCluster`, `ViewFileSystemOverloadScheme`, `DistributedFileSystem`, `RawLocalFileSystem`, `ConfigUtil`/`ViewFsTestSetup`, `Constants.CONFIG_VIEWFS_*`, `FsConstants.FS_VIEWFS_OVERLOAD_SCHEME_TARGET_FS_IMPL_PATTERN`, `NflyFSystem.NflyKey`, `ViewFileSystemOverloadScheme.ChildFsGetter`, `FSDataInputStream`, and `FSDataOutputStream`. Helpers include `addMountLinks`, `testMountLinkWithNonExistentLink`, `testCreateOnRoot`, `writeString`, and `readString`.

## Control flow, state, and persistence

`@BeforeAll` starts a two-DN cluster. `setUp` derives a cluster configuration, sets `fs.hdfs.impl` to the overload scheme, ignores port in mount-table name by default, and creates a local target directory. Each test adds mount links under the HDFS authority, opens `FileSystem.get(conf)` or `FileSystem.get(defaultFSURI, conf)`, performs operations through overloaded `hdfs://...` paths, and then `cleanUp` deletes all HDFS root children and closes filesystem caches.

## Dependencies and integration points

This suite touches FileSystem implementation registration, mount-table naming from HDFS authorities, HDFS/local target routing, fallback routing, ViewFS inner-cache and Hadoop FileSystem cache interaction, Nfly replicated writes and repair-on-read, and HDFS client initialization through the overloaded scheme.

## Risks and test signals

Risks include routing local paths to HDFS, accepting nonexistent target filesystems too early or too late, listing wrong root entries, creating root files without fallback, missing target implementation failures, incorrect child filesystem counts with caching disabled, Nfly not replicating or repairing, and mount-table lookup failures when URI ports differ. Signals are exact existence checks in target filesystems, expected exceptions, child count assertions, and successful Nfly reads after deleting one replica.
