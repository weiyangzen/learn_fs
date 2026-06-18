# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractMkdir.java

## Purpose
`TestLocalFSContractMkdir` runs generic directory creation tests against local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractMkdirTest` and creates `LocalFSContract`.

## Control Flow
Inherited tests exercise `mkdirs()` for new, existing, nested, and conflicting paths.

## State And Persistence
No subclass fields. Created local directories persist until teardown.

## Dependencies And Integration Points
It validates local `mkdirs()` through the shared contract suite.

## Risks
Case-insensitive platforms may collapse paths that are distinct on POSIX.

## Test Signals
Correct return values and `FileStatus.isDirectory()` checks are the expected signals.
