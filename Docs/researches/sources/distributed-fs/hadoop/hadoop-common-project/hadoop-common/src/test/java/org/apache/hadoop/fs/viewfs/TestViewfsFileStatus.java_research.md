# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewfsFileStatus.java

Purpose: tests `ViewFsFileStatus`/`FileStatus` behavior for viewfs, covering serialization, erasure-coding flag retention, ACL/permission propagation for mount links, and checksum delegation path translation.

Important APIs and types: `FileSystem.get(FsConstants.VIEWFS_URI, conf)`, `ConfigUtil.addLink`, `FileStatus.write/readFields`, `DataOutputBuffer`, `DataInputBuffer`, `ContractTestUtils.assertNotErasureCoded`, `FsPermission`, Mockito, `InodeTree.ResolveResult`, and `ViewFileSystem.getFileChecksum`.

Control flow: `testFileStatusSerialziation` creates a local file under a mounted directory, reads status through viewfs, serializes/deserializes it, and asserts length and erasure-coding state. `testListStatusACL` mounts a file and directory, disables mount-links-as-symlinks, verifies permissions and type flags before/after local permission changes. `testGetFileChecksum` injects a mocked `InodeTree` result and verifies checksum is called with `remainingPath`, not the original viewfs path.

State and persistence: uses a temporary local test directory cleaned after each/all tests.

Dependencies and integration: protects MapReduce serialization compatibility, viewfs status overlay behavior, and checksum delegation.

Risks and test signals: regressions include lost erasure-coding fields, stale permission mapping, mount links reported with wrong type, and checksum calls against unresolved viewfs paths.
