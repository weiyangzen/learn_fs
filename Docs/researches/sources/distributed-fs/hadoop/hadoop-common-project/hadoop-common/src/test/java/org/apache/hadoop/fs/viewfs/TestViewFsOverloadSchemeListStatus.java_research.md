# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsOverloadSchemeListStatus.java

Purpose: tests `listStatus` behavior under `ViewFileSystemOverloadScheme`, including permission/type propagation and fallback behavior when no explicit mount links are configured.

Important APIs and types: `ViewFileSystemOverloadScheme`, `FileSystem.get`, `ConfigUtil.addLink`, `FsPermission`, `FileStatus`, `FileUtil`, `GenericTestUtils.getTestDir`, `LocalFileSystem`, and `FsConstants.FS_VIEWFS_OVERLOAD_SCHEME_TARGET_FS_IMPL_PATTERN`.

Control flow: setup overloads the `file` scheme and creates a clean test directory. `testListStatusACL` creates a file and directory, mounts them at `/file` and `/dir`, verifies listed permissions match local FS, changes local permissions, and verifies updated status including `isDirectory`. `testViewFSOverloadSchemeWithoutAnyMountLinks` opens a `file:` URI with no mount links, asserts no mount points, creates through fallback, and checks the raw local FS view is rooted correctly.

State and persistence: uses temporary local files and directories and cleans them after each/all tests.

Dependencies and integration: validates overload scheme status mapping, mount-link-as-status behavior, fallback chroot semantics, and raw target FS lookup.

Risks and test signals: likely regressions are stale permissions, wrong directory flags, fallback rooted at initialization path instead of raw root, or hangs during fallback listing.
