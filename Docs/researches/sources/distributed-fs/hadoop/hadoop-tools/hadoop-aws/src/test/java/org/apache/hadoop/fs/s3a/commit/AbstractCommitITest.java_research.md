<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/AbstractCommitITest.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/AbstractCommitITest.java

## Purpose

`AbstractCommitITest` is the shared base for S3A committer integration tests. It prepares committer-friendly S3A configuration, creates test helpers and report directories, manages multipart upload assertions, constructs MapReduce task contexts, and validates S3A `_SUCCESS` marker content and statistics.

## Important APIs, Types, and Functions

- `createConfiguration()` disables FS caching, clears committer/buffer overrides, enables magic committer default, sets multipart threshold/size to minimum, uses array fast-upload buffer, configures summary report directory, and enables experimental IOStatistics collection.
- `setup()` creates a local reports directory and initializes `CommitterTestHelper`.
- `bindCommitter()` writes committer factory and committer name options.
- `rmdir()` deletes paths through their configured filesystem.
- `randomJobId()` builds a MapReduce-compatible job id from current date/randomness and `test.unique.fork.id`.
- `abortMultipartUploadsUnderPath()`, `assertMultipartUploadsPending()`, `assertNoMultipartUploadsPending()`, and `countMultipartUploads()` wrap S3A multipart upload test utilities.
- `verifySuccessMarker()`, `validateSuccessFile()`, and `loadSuccessFile()` load `_SUCCESS`, validate committer name/job id/file count, log metrics/diagnostics, aggregate job IOStatistics, and also read it through manifest committer tooling.
- `CloseWriter` safely closes `RecordWriter`s.
- `taskAttemptForJob()` creates a MapReduce `TaskAttemptContext` from a YARN job id.

## Control Flow and State

Subclasses inherit configuration setup before creating S3A filesystems. Per-test setup creates report output and helper state. Commit tests write data, commit jobs, then call success-marker and MPU assertions. Static `JOB_STATISTICS` aggregates IO stats from all loaded success files and is logged in `@AfterAll`.

## State and Persistence Behavior

Local report files are written under the project build directory. S3A test output and multipart uploads are created in the target bucket by subclasses. The base cleans only through helper calls used by subclasses; it also maintains static aggregate IO statistics.

## Dependencies and Integration Points

It integrates S3A committer constants, multipart test utilities, `SuccessData`, manifest success data/printer, Hadoop MapReduce contexts, YARN id builders, S3A filesystem instrumentation, AssertJ, and contract test utilities.

## Risks and Edge Cases

Committer tests rely on real multipart upload support, correct cleanup of pending MPUs, and non-empty S3A success data. `randomJobId()` assumes the fork id ends in four digits. The success-file validation intentionally fails if `_SUCCESS` is zero bytes, because that indicates a non-S3A committer path.

## Test Signals

Signals include presence and nonzero size of `_SUCCESS`, valid `SuccessData`, matching committer and job id, minimum committed file count, manifest-printer loadability, logged IOStatistics/diagnostics, and absence/presence of pending MPUs under tested prefixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/AbstractCommitITest.java -->
