# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeXAttr.java

Purpose: Extends the common HDFS xattr base test suite with a NameNode symlink-specific xattr scenario, ensuring xattr operations through symlink paths affect the target inode as expected.

Important APIs and functions: Inherits cluster and xattr fixtures such as `fs`, `name1`, `name2`, `name3`, `value1`, and `value2` from `FSXAttrBaseTest`. The local test uses `DistributedFileSystem` methods `mkdirs`, `createSymlink`, `setXAttr`, `getXAttrs`, `removeXAttr`, and `delete`.

Control flow: The test creates separate link and target parent directories, creates a target file, creates a symlink to it, sets two xattrs on the target, reads them through the symlink, adds a third empty xattr through the symlink, verifies target-side visibility, removes xattrs through link and target paths, and finally deletes both parent directories.

State and persistence behavior: Xattrs are persisted on the target inode, not on the symlink path. Empty xattr values are represented as zero-length byte arrays. The test mutates namespace xattr state and then cleans up.

Dependencies and integration points: Depends on HDFS symlink resolution, NameNode xattr storage, `DFSTestUtil.createFile`, inherited xattr cluster setup, and Java map/byte-array assertions. It specifically tests interaction between symlink resolution and xattr APIs.

Risks: The test assumes all xattr operations follow symlinks. Any future API mode that supports no-follow xattr operations would need separate coverage. Byte array assertions are necessary because map equality would not compare array contents safely.

Test signals: Passing means xattrs set on target are visible through the link, xattrs set or removed through the link mutate the target, empty xattr values round-trip as `new byte[0]`, and cleanup succeeds.
