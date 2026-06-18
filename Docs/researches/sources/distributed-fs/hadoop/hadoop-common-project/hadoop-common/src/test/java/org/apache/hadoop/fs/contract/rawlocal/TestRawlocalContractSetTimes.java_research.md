# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractSetTimes.java

## Purpose
`TestRawlocalContractSetTimes` validates raw local timestamp mutation through the generic contract suite.

## Important APIs, Types, And Functions
It extends `AbstractContractSetTimesTest` and creates `RawlocalFSContract`.

## Control Flow
Inherited tests call `setTimes()` on raw local files/directories and assert observed status timestamps.

## State And Persistence
No subclass state. Temporary OS file timestamps are changed.

## Dependencies And Integration Points
It exercises `RawLocalFileSystem.setTimes()`.

## Risks
Filesystem timestamp precision and access-time mount options can affect assertions.

## Test Signals
Signals are expected mtime/atime values or documented unsupported behavior.
