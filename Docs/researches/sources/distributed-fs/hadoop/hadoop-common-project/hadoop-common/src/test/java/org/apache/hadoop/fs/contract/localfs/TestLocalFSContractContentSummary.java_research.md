# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractContentSummary.java

## Purpose
`TestLocalFSContractContentSummary` applies the generic content-summary contract tests to local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractContentSummaryTest` and creates `LocalFSContract`.

## Control Flow
Inherited tests create directory/file trees, call content summary APIs, and compare counts and lengths to expected values.

## State And Persistence
There is no subclass state. File trees are created under the local test root.

## Dependencies And Integration Points
It exercises local filesystem `getContentSummary()` through the contract framework.

## Risks
Checksum side files should not be counted as user data by content summary. Platform path quirks can affect directory traversal.

## Test Signals
Expected file counts, directory counts, and byte totals should match the generated tree.
