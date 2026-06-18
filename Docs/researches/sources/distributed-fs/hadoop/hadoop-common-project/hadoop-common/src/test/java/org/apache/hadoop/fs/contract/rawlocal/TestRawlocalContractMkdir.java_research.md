# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractMkdir.java

## Purpose
`TestRawlocalContractMkdir` validates raw local directory creation through the generic contract suite.

## Important APIs, Types, And Functions
It extends `AbstractContractMkdirTest` and creates `RawlocalFSContract`.

## Control Flow
Inherited tests call `mkdirs()` for common success and conflict cases.

## State And Persistence
No subclass state. Temporary raw local directories are created and cleaned.

## Dependencies And Integration Points
It exercises raw local `mkdirs()` behavior.

## Risks
Case-insensitive local filesystems and permissions can affect expected outcomes.

## Test Signals
Signals are correct `mkdirs()` return values and directory statuses.
