# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FileContextTestWrapper.java

## Purpose
`FileContextTestWrapper` adapts a `FileContext` to the shared `FSTestWrapper` abstraction used by symlink and filesystem contract tests. It lets tests written against a common wrapper exercise FileContext semantics without duplicating FileContext-specific call sites.

## Important APIs, Types, And Functions
The wrapper holds a final `FileContext fc` and extends `FSTestWrapper`. It implements helper methods for deterministic file creation, append, existence/type checks, file read/write, status assertions, and path containment. It overrides filesystem operations such as `makeQualified`, `mkdir`, `delete`, `getFileLinkStatus`, `createSymlink`, `setWorkingDirectory`, `getFileStatus`, `create`, `open`, `setReplication`, `getLinkTarget`, `rename`, `getFileBlockLocations`, `getFileChecksum`, `listStatusIterator`, `setPermission`, `setOwner`, `setTimes`, `listStatus`, and `globStatus`.

## Control Flow
Most overrides directly delegate to the underlying `FileContext`. File creation resolves optional block size from `CreateOpts`, uses `fc.create()` with the requested flags/options, writes deterministic bytes, and returns written length. `getLocalFSWrapper()` creates another `FileContextTestWrapper` around `FileContext.getLocalFSFileContext()` for tests that cross from a non-local context to local resolution.

## State And Persistence Behavior
The wrapper has no mutable state beyond the inherited root path and the held `FileContext`. All persistent changes occur in the target filesystem through delegated operations. It inherits deterministic root and data behavior from `FSTestWrapper`.

## Dependencies And Integration Points
It is a key bridge for `SymlinkBaseTest` and other wrapper-based contract tests. It depends on `FileContext`, Hadoop exception types, `Options.CreateOpts`, `Options.Rename`, `FsPermission`, `IOUtils`, and `AccessControlException`.

## Risks
Because delegation is thin, any `FileContext` behavior differences are exposed directly. Some helper predicates collapse `FileNotFoundException` to false, but other exceptions propagate. Tests using this wrapper can observe FileContext semantics that differ from `FileSystemTestWrapper`, especially around create flag handling, link resolution, and missing-authority URI behavior.

## Test Signals
When wrapper-based tests pass through this class, they demonstrate that the concrete `FileContext` implementation supports the common wrapper contract for symlink, metadata, create/open/read/write, rename, permission, and listing operations.
