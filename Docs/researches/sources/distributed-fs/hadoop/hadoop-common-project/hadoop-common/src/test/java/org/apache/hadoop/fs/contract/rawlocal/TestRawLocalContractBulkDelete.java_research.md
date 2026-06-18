# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawLocalContractBulkDelete.java

## Purpose
`TestRawLocalContractBulkDelete` runs bulk-delete contract behavior against raw local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractBulkDeleteTest` and creates `RawlocalFSContract`.

## Control Flow
Inherited tests create sets of raw local files/directories, perform bulk deletes, and assert final namespace state.

## State And Persistence
No subclass state. Raw OS files are temporary.

## Dependencies And Integration Points
It exercises raw local deletion without checksum wrappers.

## Risks
Local OS permissions, locked files, and root-safety checks can influence delete outcomes.

## Test Signals
Signals are expected deleted path sets and clean post-test directories.
