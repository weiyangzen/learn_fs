# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractGetFileStatus.java

## Purpose
`TestLocalFSContractGetFileStatus` applies the generic file-status contract tests to local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractGetFileStatusTest` and creates `LocalFSContract`.

## Control Flow
Inherited tests check `getFileStatus()` on files, directories, missing paths, and probably root-related cases, asserting type, length, and exception behavior.

## State And Persistence
No local state. Files/directories are created under the local test root.

## Dependencies And Integration Points
It tests `LocalFileSystem.getFileStatus()` through common contract assertions.

## Risks
Checksum side files and platform permission/mtime behavior must not leak into user-visible status expectations.

## Test Signals
Signals are correct `FileStatus` file/directory flags, lengths, path qualification, and missing-path exceptions.
