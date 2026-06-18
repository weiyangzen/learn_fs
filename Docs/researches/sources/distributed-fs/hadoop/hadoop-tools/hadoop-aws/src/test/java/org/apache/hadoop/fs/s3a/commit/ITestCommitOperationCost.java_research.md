<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/ITestCommitOperationCost.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/ITestCommitOperationCost.java

## Purpose

`ITestCommitOperationCost` is an S3A performance/cost integration test suite for magic committer operations. It asserts that specific magic-path operations avoid unnecessary S3 HEAD/LIST/delete requests and produce expected metric deltas.

## Important APIs, Types, and Functions

- Extends `AbstractS3ACostTest`.
- `setup()` assumes multipart upload support and creates a `CommitterTestHelper`.
- `teardown()` aborts MPUs under the method path.
- `methodSubPath()` builds a path under the per-method test directory.
- `fileSystemIOStats()` returns pretty-printed FS IOStatistics.
- `testMagicMkdirs()` verifies mkdir/delete behavior under `__magic_job-<JOB_ID>/subdir`, including no bulk deletes and no parent marker recreation.
- `testCostOfCreatingMagicFile()` creates a file through a magic path, verifies no HEAD/LIST on create, magic stream capability, MPU initiation, marker/manifest PUTs on close, listing pending commits, loading pending commit without HEAD/LIST, and committing without extra probes/deletes.
- `testCostOfSavingLoadingPendingFile()` writes a synthetic `SinglePendingCommit` under a magic path, verifies save cost, verifies no marker header, and loads it from a `FileStatus` without HEAD/LIST.

## Control Flow and State

The tests use `verifyMetrics()` around a single filesystem or commit operation and assert expected statistic deltas. Magic file creation starts an S3A output stream, writes bytes, closes it, locates the pending commit manifest, loads it as `SinglePendingCommit`, then commits it via `CommitOperations`. The pending-file test constructs a minimal valid `SinglePendingCommit` manually before saving/loading it.

## State and Persistence Behavior

The suite creates and deletes S3 test paths under `methodPath()`, initiates multipart uploads for magic streams, writes pending commit manifests, and aborts any leftover MPUs in teardown. The active stream is stored in a field so it can be aborted on failure.

## Dependencies and Integration Points

It integrates S3A cost-test metrics, S3A statistics constants, magic committer path constants, `CommitterTestHelper`, `CommitOperations`, `PersistentCommitData`, `SinglePendingCommit`, S3A `FSDataOutputStream` abort semantics, and IOStatistics logging.

## Risks and Edge Cases

Cost assertions are sensitive to implementation changes in S3A request patterns. Magic-path behavior deliberately skips existence checks, so incorrect use outside isolated test paths could overwrite or bypass checks. The synthetic pending commit uses fake upload id/etag state only for save/load cost validation, not real MPU completion.

## Test Signals

Signals are metric assertions: no HEAD/LIST for magic create/save/load/commit paths, expected MPU initiation count, expected marker PUT counts, expected delete/list/metadata counts for magic mkdir/delete, one pending commit located, successful pending commit load, absent marker header on ordinary pending files, and cleanup of active streams/uploads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/ITestCommitOperationCost.java -->
