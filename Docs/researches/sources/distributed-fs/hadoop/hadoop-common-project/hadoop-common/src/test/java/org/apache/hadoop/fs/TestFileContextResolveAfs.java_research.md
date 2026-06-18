## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileContextResolveAfs.java

Purpose: tests `FileContext.resolveAbstractFileSystems` when resolving a symlink to a local path. It ensures symlink traversal returns the expected abstract filesystem set.

Important APIs/types/functions: `FileSystem.enableSymlinks`, `FileContext.getFileContext`, `FileSystem.get`, `FileSystem.makeQualified`, `FileContext.createSymlink`, `FileContext.resolveAbstractFileSystems`, and `AbstractFileSystem`.

Control flow: a static block enables symlinks globally. Setup creates a default FileContext. The test creates a local source path and qualified link path, ensures the test root exists, creates the target file, creates a symlink, resolves AFS instances for the link, expects a singleton set, then deletes link and target and closes the local filesystem.

State and persistence: mutates global symlink enablement and creates local files/symlinks under `GenericTestUtils.getTestDir`. Cleanup is performed inline rather than through teardown.

Dependencies/integration points: local symlink support, FileContext symlink creation, `FileSystem`/`AbstractFileSystem` resolution bridge, and default configuration.

Risks and test signals: symlink permissions or platform limitations can affect the test. The 30-second timeout protects against recursive symlink resolution hangs. A result size other than one indicates incorrect AFS deduplication or symlink target resolution.
