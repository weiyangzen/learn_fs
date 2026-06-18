# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemOverloadSchemeHdfsFileSystemContract.java

## Purpose

This class runs the HDFS filesystem contract tests through `ViewFileSystemOverloadScheme` after registering it as the implementation for the `hdfs` scheme. It ensures common HDFS contract behavior still works when HDFS paths are mediated by ViewFS mount-table resolution.

## Important APIs, types, and functions

The class extends `TestHDFSFileSystemContract` and uses `MiniDFSCluster`, `HdfsConfiguration`, `ConfigUtil.addLink`, `ViewFileSystemOverloadScheme`, `DistributedFileSystem`, `AppendTestUtil`, `FileSystemContractBaseTest.TEST_UMASK`, `CONFIG_VIEWFS_IGNORE_PORT_IN_MOUNT_TABLE_NAME`, and `getRawFileSystem`.

## Control flow, state, and persistence

`@BeforeAll` starts a two-DN HDFS cluster and records the expected working directory. `setUp` maps `fs.hdfs.impl` to the overload scheme, maps the target implementation back to `DistributedFileSystem`, adds `/user`, `/append`, and `/FileSystemContractBaseTest/` links under the default FS authority, then obtains `fs = FileSystem.get(conf)`. Overrides adapt append, root rename, root listing, and disable duplicate LS-root coverage.

## Dependencies and integration points

This integrates the generic HDFS FileSystem contract with ViewFS overload mounting, default FS authority lookup, append support, root access protection, and raw filesystem escape for preparing root-listing fixtures.

## Risks and test signals

Risks include contract regressions hidden by scheme overloading, wrong mount-table authority when ports are present, append path misrouting, and root operations returning different exception types. Signals are inherited contract pass/fail plus explicit `AccessControlException` for root rename and successful root listing of `/FileSystemContractBaseTest`.
