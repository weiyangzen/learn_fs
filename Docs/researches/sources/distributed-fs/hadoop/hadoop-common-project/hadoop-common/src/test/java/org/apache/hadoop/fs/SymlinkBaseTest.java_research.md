# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/SymlinkBaseTest.java

## Purpose
`SymlinkBaseTest` is the broad abstract symlink contract suite shared by `FileSystemTestWrapper` and `FileContextTestWrapper` implementations. It validates symlink creation, link-status versus resolved-status behavior, dangling and recursive links, relative/absolute/qualified targets, intermediate symlink traversal, rename semantics involving links, and metadata operations through links.

## Important APIs, Types, And Functions
The suite uses static `FSTestWrapper wrapper`, abstract `getScheme()`, `testBaseDir1()`, `testBaseDir2()`, and `testURI()`, and overrideable `unwrapException()`. It re-enables symlinks via `FileSystem.enableSymlinks()`. Helpers `createAndWriteFile()`, `readFile()`, `appendToFile()`, and `checkLink()` centralize deterministic file and link validation. Tests use `CreateOpts`, `Options.Rename`, `FsPermission`, `RemoteIterator`, `FileStatus`, and many Hadoop filesystem exceptions.

## Control Flow
`setUp()` creates two base directories; `tearDown()` deletes them. Early tests cover root status, working directory behavior, dangling links, invalid targets, parent creation, mkdir/create failures over links, deletion, open resolution, file/dir/dangling/non-link statuses, recursive links, and target qualification. Mid-suite tests cover relative, absolute, fully qualified, and partially qualified targets, plus local versus non-local differences. Later tests create files/directories/links through symlinked parents, list through links, prevent duplicate links, rename files/directories/symlinks through intermediate symlinks, rename onto symlink destinations, rename symlinks themselves, rename targets, access file operations via intermediate symlink paths, and set times through links.

## State And Persistence Behavior
The suite creates deterministic 16 KiB files with 8 KiB blocks and replication/block options. It mutates only `testBaseDir1()` and `testBaseDir2()` and removes both at teardown. Symlink targets are intentionally persisted in relative, absolute, fully qualified, and partially qualified forms to verify stored target behavior.

## Dependencies And Integration Points
Concrete local filesystem and HDFS-style tests supply the wrapper, URI, scheme, and base directories. The suite integrates with both `FileSystem` and `FileContext` wrappers, local filesystem special cases, and cross-filesystem access from a local wrapper.

## Risks
The suite contains explicit localfs exceptions because Java local filesystem APIs handle dangling symlinks and fully qualified paths differently. Some rename operations are not atomic, and comments document gaps where localfs cannot represent dangling link states reliably. The static wrapper requires careful subclass setup and is not isolated for parallel execution.

## Test Signals
Passing this suite is a strong signal that a filesystem handles symlink resolution and non-resolution boundaries correctly: `getFileStatus()` resolves, `getFileLinkStatus()` preserves link identity, `getLinkTarget()` returns expected targets, intermediate links work for file operations, and rename/setTimes semantics affect the intended object.
