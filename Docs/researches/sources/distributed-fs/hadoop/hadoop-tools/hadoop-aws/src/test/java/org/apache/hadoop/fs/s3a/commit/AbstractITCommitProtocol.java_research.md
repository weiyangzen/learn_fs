<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/AbstractITCommitProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/AbstractITCommitProtocol.java

## Purpose

`AbstractITCommitProtocol` is the main abstract integration suite for S3A committers. It exercises the full MapReduce output committer lifecycle across normal commits, task/job aborts, duplicate attempts, speculative attempts, failure injection, output-format integration, AM-like workflows, parallel jobs, UUID propagation, and committer factory binding.

## Important APIs, Types, and Functions

- Abstract extension points: `suitename()`, `createCommitter(Path, TaskAttemptContext)`, `getCommitterName()`, `createFailingCommitter()`, and validation hooks for work paths and task output paths.
- Setup builds unique `jobId`, task attempt IDs, verifies multipart support, derives an isolated output dir, aborts old MPUs, and deletes old output.
- `JobData` stores `Job`, `JobContext`, `TaskAttemptContext`, `AbstractS3ACommitter`, configuration, and optional written path.
- `newJob()`, `startJob()`, `setup()`, `commit()`, `commitTask()`, `commitJob()`, and `abortJobQuietly()` model MR job/task setup, write, commit, and cleanup.
- `writeTextOutput()` and `writeMapFileOutput()` write deterministic output through `LoggingTextOutputFormat` or `MapFileOutputFormat`.
- `validateContent()`, `getPart0000()`, `validateMapFileOutputContent()`, and `validateStorageClass()` assert final output.
- Tests cover recovery unsupported, commit lifecycle, storage class, duplicate commit, two task attempts, injected job commit failure/retry, no-output commit, map-file output, abort variants, concurrent subdir commits, output format integration, AM workflow, parallel jobs to adjacent/same destinations, self-generated UUIDs, required propagated UUIDs, and factory binding.

## Control Flow and State

Each test starts with a clean S3 output directory and no pending MPUs. `startJob()` creates a job, contexts, and committer, runs `setupJob()` and `setupTask()`, registers cleanup, and optionally writes output. Task commit promotes task data/metadata to job-commit-visible state, while job commit makes final output visible and writes `_SUCCESS`. Abort paths cancel task/job state and pending uploads. Parallel-job tests deliberately interleave task writes and job commits to validate isolation through unique paths and UUIDs.

## State and Persistence Behavior

The suite creates S3 objects, pending multipart uploads, committer metadata, MapFile directories, and success markers under per-method output paths. It keeps a list of jobs to abort during teardown and always attempts MPU cleanup under the output dir. It also checks that no S3A committer thread pools leak after all tests.

## Dependencies and Integration Points

It integrates S3A committer implementations, `AbstractS3ACommitter`, `MagicS3GuardCommitter`, `S3ACommitterFactory`, `CommitterFaultInjection`, MapReduce `OutputFormat` and `OutputCommitter`, `LoggingTextOutputFormat`, `MapFileOutputFormat`, S3A storage-class metadata, IOStatistics, Spark write UUID config, and Hadoop contract test helpers.

## Risks and Edge Cases

The suite targets high-risk commit semantics: output must not be visible after task commit alone; duplicate task commit should fail or be safely handled; a later speculative attempt must supersede earlier output; job commit retry can expose partially completed state; aborts must be idempotent and MPU-clean; two jobs to the same destination must not delete each other's active uploads when configured; generated UUIDs must not be used by independent task-only committers; and factory binding must select the configured committer.

## Test Signals

Signals include final file content equality, storage class equality, success marker validation with committer UUID, no pending MPUs after commit/abort, expected `FileNotFoundException` or `PathCommitException` failures, task commit IOStatistic counters, absence of leaked committer threads, isolation of parallel job output filenames, UUID source/config assertions, and factory-created class equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/AbstractITCommitProtocol.java -->
