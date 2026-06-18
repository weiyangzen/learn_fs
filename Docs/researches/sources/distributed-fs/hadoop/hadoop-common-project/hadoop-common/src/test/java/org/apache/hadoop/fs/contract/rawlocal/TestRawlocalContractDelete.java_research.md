# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractDelete.java

## Purpose
`TestRawlocalContractDelete` runs generic delete contract tests against raw local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractDeleteTest` and creates `RawlocalFSContract`.

## Control Flow
Inherited tests call raw local `delete()` on files/directories/missing paths and assert behavior according to rawlocal contract XML.

## State And Persistence
No subclass state. Temporary OS files/directories are created and removed.

## Dependencies And Integration Points
It exercises raw local deletion without checksum side-file cleanup considerations.

## Risks
Open files and permissions can produce platform-specific delete failures.

## Test Signals
Signals are expected delete return values and absence of deleted paths.
