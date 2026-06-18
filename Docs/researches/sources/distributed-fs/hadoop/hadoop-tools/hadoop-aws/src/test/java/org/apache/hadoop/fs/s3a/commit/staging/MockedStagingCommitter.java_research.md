# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/MockedStagingCommitter.java

## Purpose
Test-only `StagingCommitter` subclass that allows mocked S3A filesystems and clients to be used without strict destination-FS checks, and exposes recorded client outcomes to tests.

## Important APIs, Types, and Functions
The class overrides `getDestinationFS()`, `commitJob()`, and `maybeCreateSuccessMarker()`. It exposes `getResults()` and `getErrors()` by casting `getDestS3AFS()` to `MockS3AFileSystem` and reading the stored `ClientResults`/`ClientErrors` pair.

## Control Flow and Behavior
`commitJob()` delegates to the real staging committer, then optionally serializes `getResults()` to a local path configured as `mock-results-file`. Success marker creation is skipped because that path is not mocked for these unit tests.

## State, Persistence, and Dependencies
Persistent state may include a local serialized results object and the real staged pending files produced by the superclass. Dependencies include `MockS3AFileSystem`, `StagingTestBase` result/error containers, `SuccessData`, and `IOStatisticsSnapshot`.

## Integration Points, Risks, and Test Signals
This helper lets committer unit tests exercise real staging committer logic against mock S3 operations. Risks are that it deliberately skips success marker behavior and suppresses exceptions while serializing results, so tests using it should not infer success-marker correctness.
