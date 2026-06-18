# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/magic/ITestMagicCommitProtocolFailure.java

## Purpose
Negative integration test proving the magic committer cannot be constructed when multipart uploads are disabled.

## Important APIs, Types, and Functions
The class extends `AbstractS3ATestBase`. `createConfiguration()` removes bucket overrides, disables `MULTIPART_UPLOADS_ENABLED`, binds the S3A committer factory, and selects `COMMITTER_NAME_MAGIC`. `testCreateCommitter()` constructs a `TaskAttemptContextImpl` and intercepts `PathCommitException` from `new MagicS3GuardCommitter(...)`.

## Control Flow and Behavior
The filesystem is deliberately configured without MPU support before the committer is created. The single test asserts construction fails immediately rather than allowing a committer that would fail later at upload or commit time.

## State, Persistence, and Dependencies
There is no output persistence. Dependencies are S3A configuration, bucket override removal, MR task context, and magic committer constructor validation.

## Integration Points, Risks, and Test Signals
The test protects a critical precondition: magic commits require multipart uploads. A failure indicates that validation has weakened or configuration overrides are not being removed correctly.
