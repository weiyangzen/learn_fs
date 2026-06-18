# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractSeek.java

## Purpose
`TestLocalFSContractSeek` runs common seek/positioned read contract tests against local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractSeekTest` and creates `LocalFSContract`.

## Control Flow
Inherited tests generate datasets, seek to offsets, read and compare bytes, and check EOF/negative/closed-stream behavior according to contract flags.

## State And Persistence
No subclass state. Test files and checksum files are local and temporary.

## Dependencies And Integration Points
It exercises seek support in `LocalFSFileInputStream` via Hadoop FS abstractions.

## Risks
Checksum wrappers can affect positioned reads and EOF checks; platform buffering can mask closed-stream behavior.

## Test Signals
Signals include exact byte equality after seeks and expected exceptions for invalid positions.
