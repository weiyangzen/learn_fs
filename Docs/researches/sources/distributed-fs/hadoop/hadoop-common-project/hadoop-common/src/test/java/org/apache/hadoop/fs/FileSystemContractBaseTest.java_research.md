# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FileSystemContractBaseTest.java

## Purpose
`FileSystemContractBaseTest` is the abstract legacy `FileSystem` contract suite. It checks general-purpose filesystem implementations for status, working directory, mkdir, umask, listing, read/write/delete, overwrite, rename, case sensitivity, root handling, and byte-accurate data persistence.

## Important APIs, Types, And Functions
The fixture is `protected FileSystem fs` plus deterministic `data = dataset(getBlockSize() * 2, 0, 255)`. Extension points include `getGlobalTimeout()`, `getTestBaseDir()`, `getBlockSize()`, `getDefaultWorkingDirectory()`, `renameSupported()`, `rootDirTestEnabled()`, and `filesystemIsCaseSensitive()`. Helpers include `path(String)`, `cleanupDir(Path)`, `createFile(Path)`, `rename(Path, Path, boolean, boolean, boolean)`, `writeAndRead()`, `assertListStatusFinds()`, `assertIsFile()`, `toChar()`, and `dataset()`.

## Control Flow
`tearDown()` cleans both root-level and base-directory test paths. Tests progress from status and working-directory behavior to mkdir, mkdir failure under files, umask application, missing-status exceptions, listing, write-read-delete at several lengths, overwrite behavior, auto-parent creation, delete behavior, and many rename cases. Later tests validate overwrite/read consistency for eventually consistent stores, case sensitivity, file status for zero/multi-byte files, root existence, forbidden root and child renames, self-renames, list root behavior, and data comparison diagnostics.

## State And Persistence Behavior
The suite writes test data under `getTestBaseDir()` and sometimes `/FileSystemContractBaseTest` when root tests are enabled. It temporarily mutates `fs.getConf()` for umask testing and restores the old value. `writeAndRead()` persists data until optional deletion.

## Dependencies And Integration Points
Concrete `FileSystem` implementations inherit this suite. It integrates with Hadoop `Configuration`, `FsPermission`, `FsStatus`, `FileStatus`, `LocatedFileStatus`, `RemoteIterator`, and filesystem-specific rename/status implementations.

## Risks
Legacy `FileSystem.rename()` semantics differ from newer `FileContext.rename()` semantics, especially for file self-renames and moving into existing directories. Root tests can be dangerous for real filesystems, so subclasses must override `rootDirTestEnabled()` when needed. Case sensitivity assumptions are configurable but easy to forget for object stores or local platforms.

## Test Signals
Passing the suite signals broad compatibility with the old `FileSystem` API: correct data durability, path resolution, directory semantics, rename state transitions, root/list behavior, and diagnostic byte-level validation.
