# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemOverloadSchemeLocalFileSystem.java

Purpose: tests `ViewFileSystemOverloadScheme` when the normal `file` scheme is overloaded to route through viewfs while delegating actual storage to `LocalFileSystem`.

Important APIs and types: `ViewFileSystemOverloadScheme`, `FsConstants.FS_VIEWFS_OVERLOAD_SCHEME_TARGET_FS_IMPL_PATTERN`, `ViewFsTestSetup.addMountLinksToConf`, `ConfigUtil` link constants, `FileSystemTestHelper`, `FSDataOutputStream`, `FSDataInputStream`, and `LocalFileSystem`.

Control flow: setup configures `fs.file.impl` to the overload class, configures the target implementation pattern to `LocalFileSystem`, initializes a local target FS, and creates a clean root. Tests add mount links, open `FileSystem.get(file:/// or file://mt/)`, then verify write/read, create/delete, root-level `linkMergeSlash`, and rejection when merge-slash is combined with other mount links.

State and persistence: local filesystem test root is created, mutated, and deleted in teardown.

Dependencies and integration: protects compatibility for deployments that use existing scheme URIs while internally applying viewfs mount tables.

Risks and test signals: high-risk behavior is scheme recursion, wrong target implementation lookup, merge-slash allowing ambiguous mounts, and authority-specific mount-table loading failures.
