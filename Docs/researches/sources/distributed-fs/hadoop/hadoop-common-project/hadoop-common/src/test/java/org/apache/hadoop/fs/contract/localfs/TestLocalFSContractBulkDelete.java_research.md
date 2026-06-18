# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractBulkDelete.java

## Purpose
`TestLocalFSContractBulkDelete` validates local filesystem behavior through the generic bulk-delete contract suite.

## Important APIs, Types, And Functions
The class extends `AbstractContractBulkDeleteTest` and constructs `LocalFSContract`.

## Control Flow
Inherited tests build sets of files/directories and exercise the filesystem bulk deletion contract, checking accepted inputs, missing paths, recursive behavior, and resulting namespace state.

## State And Persistence
It stores no fields. Test data persists only under the local test directory until cleanup.

## Dependencies And Integration Points
It integrates local filesystem behavior with contract-level bulk delete expectations.

## Risks
Bulk delete can be sensitive to root-operation guards and local filesystem permissions. Failures may leave many temporary paths if cleanup is interrupted.

## Test Signals
Signals are correct deleted/not-deleted path sets and clean final directory state.
