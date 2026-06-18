# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FileSystemTestWrapper.java

## Purpose
`FileSystemTestWrapper` adapts a `FileSystem` to the shared `FSTestWrapper` abstraction. It lets wrapper-based tests exercise legacy `FileSystem` implementations using the same operation surface used for `FileContext`.

## Important APIs, Types, And Functions
The wrapper holds a final `FileSystem fs`. It implements file creation, append, existence/type checks, read/write, status assertions, and `FSTestWrapper` overrides for qualification, mkdir, delete, link status, symlink creation, working directory, status, create, open, link target, replication, rename, block locations, checksum, iterated listing, permission, ownership, times, array listing, and glob status.

## Control Flow
Most operations delegate to `fs`. `mkdir()` uses deprecated `primitiveMkdir()` to mirror FileContext semantics. `create(Path, EnumSet<CreateFlag>, CreateOpts...)` translates FileContext-style create flags and options into the `FileSystem.create()` signature: permissions after umask, overwrite boolean, buffer size, replication, block size, and optional `Progressable`. `appendToFile()` delegates to `fs.append()`.

## State And Persistence Behavior
The wrapper maintains no mutable state beyond the inherited test root and the held `FileSystem`. It mutates the backing filesystem through delegated calls. Permission translation reads the current filesystem configuration umask at create time.

## Dependencies And Integration Points
It is used by `SymlinkBaseTest` and other tests that compare `FileSystem` and `FileContext` semantics through `FSTestWrapper`. It depends on `CommonConfigurationKeysPublic`, `FsPermission`, `CreateOpts`, `Options.Rename`, `Progressable`, and Hadoop filesystem exceptions.

## Risks
The create-option translation does not implement every possible `CreateFlag` semantic; it primarily maps overwrite and create options. It may behave differently from native `FileContext` for append/create combinations or parent-creation rules. Deprecated APIs are intentionally used to match lower-level semantics.

## Test Signals
Passing wrapper-based suites through this class shows that legacy `FileSystem` operations conform to the shared wrapper contract for symlinks, metadata, create/open/read/write, checksums, permissions, and listing.
