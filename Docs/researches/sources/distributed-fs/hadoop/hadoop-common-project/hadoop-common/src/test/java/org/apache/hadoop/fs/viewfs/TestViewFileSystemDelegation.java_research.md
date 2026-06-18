# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemDelegation.java

Purpose: verifies selected `ViewFileSystem` calls delegate to the correct child `FileSystem` after path translation. It includes sanity checks for fake scheme registration and comprehensive ACL delegation checks using mocked child filesystems.

Important APIs and types: `ViewFileSystemTestSetup.createConfig`, `FileSystem.get(FsConstants.VIEWFS_URI, conf)`, `ConfigUtil.addLink`, `TestChRootedFileSystem.getChildFileSystem`, `MockFileSystem`, ACL methods such as `modifyAclEntries`, `removeAcl`, `setAcl`, and `getAclStatus`, plus `FakeFileSystem` extending `LocalFileSystem`.

Control flow: static setup registers `fs1` and `fs2` schemes, mounts them under `/mounts/<scheme>`, opens a viewfs instance, and retrieves children. `testAclMethods` creates two mock mounts, performs each ACL operation through viewfs paths, and verifies the underlying mocks receive paths with the mount prefix stripped.

State and persistence: scheme bindings and mount links live in `Configuration`; `FakeFileSystem` records its URI and checksum flag.

Dependencies and integration: exercises `ViewFileSystem` delegation, chroot path mapping, ACL API coverage, and filesystem implementation lookup by scheme.

Risks and test signals: path translation errors can silently apply ACLs to the wrong target. Missing delegation will show as Mockito verification failures, while scheme setup regressions show as wrong child URI identity.
