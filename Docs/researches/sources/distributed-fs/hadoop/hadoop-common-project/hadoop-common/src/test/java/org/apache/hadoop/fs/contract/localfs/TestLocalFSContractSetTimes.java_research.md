# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractSetTimes.java

## Purpose
`TestLocalFSContractSetTimes` validates local FS timestamp mutation through the generic contract suite.

## Important APIs, Types, And Functions
It extends `AbstractContractSetTimesTest` and creates `LocalFSContract`.

## Control Flow
Inherited tests create files/directories, call `setTimes()`, then read `FileStatus` to validate mtime/atime behavior and unsupported cases.

## State And Persistence
No subclass fields. Timestamp changes are applied to local temporary files.

## Dependencies And Integration Points
It exercises `LocalFileSystem.setTimes()` and platform filesystem timestamp resolution.

## Risks
Different OS/filesystem timestamp precision can cause flaky exact comparisons.

## Test Signals
Signals are observed modification/access times matching expected contract tolerance and failures for missing paths.
