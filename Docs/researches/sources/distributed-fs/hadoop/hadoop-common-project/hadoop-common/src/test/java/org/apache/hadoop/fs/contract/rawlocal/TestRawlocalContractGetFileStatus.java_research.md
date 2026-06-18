# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractGetFileStatus.java

## Purpose
`TestRawlocalContractGetFileStatus` runs generic status tests against raw local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractGetFileStatusTest` and creates `RawlocalFSContract`.

## Control Flow
Inherited tests create paths and validate `getFileStatus()` type, length, path qualification, and missing-path behavior.

## State And Persistence
No subclass fields. Raw OS files/directories are temporary.

## Dependencies And Integration Points
It exercises `RawLocalFileSystem.getFileStatus()`.

## Risks
Symlinks, permissions, and platform path casing can alter visible status.

## Test Signals
Signals include correct file/directory flags and expected exceptions for missing paths.
