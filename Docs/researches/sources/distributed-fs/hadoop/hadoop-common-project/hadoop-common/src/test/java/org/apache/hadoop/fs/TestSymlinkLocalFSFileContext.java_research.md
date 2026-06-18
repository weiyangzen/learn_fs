# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestSymlinkLocalFSFileContext.java

Purpose: runs the local symlink test suite through the `FileContext` API.

Important APIs/types/functions: `FileContext.getLocalFSFileContext`, `FileContextTestWrapper`, inherited `TestSymlinkLocalFS` tests, and `testRenameFileWithDestParentSymlink`.

Control flow/state/persistence: `@BeforeAll` installs a `FileContextTestWrapper` over local FileContext into the inherited static wrapper. It only overrides destination-parent symlink rename to skip on Windows before delegating to the base implementation.

Dependencies/integration points: validates symlink behavior through FileContext rather than FileSystem. Inherits all local symlink filesystem state and cleanup from the base hierarchy.

Risks/test signals: catches FileContext wrapper deviations in local symlink resolution, rename semantics, and platform assumptions.
