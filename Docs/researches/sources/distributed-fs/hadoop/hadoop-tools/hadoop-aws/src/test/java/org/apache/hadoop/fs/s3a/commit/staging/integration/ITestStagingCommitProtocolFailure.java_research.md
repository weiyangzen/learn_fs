# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/integration/ITestStagingCommitProtocolFailure.java

## Purpose
Negative integration test proving the staging committer cannot be created when multipart uploads are disabled.

## Important APIs, Types, and Functions
The class extends `AbstractS3ATestBase`. `createConfiguration()` removes bucket overrides, disables `MULTIPART_UPLOADS_ENABLED`, binds the S3A committer factory and staging committer name, and disables filesystem caching. `testCreateCommitter()` expects `PathCommitException` from `new StagingCommitter(...)`.

## Control Flow and Behavior
The test constructs a task attempt context against a deliberately MPU-disabled configuration and asserts immediate constructor failure.

## State, Persistence, and Dependencies
There is no output persistence. Dependencies are S3A configuration, staging committer constructor validation, and MR task context classes.

## Integration Points, Risks, and Test Signals
Like the magic failure test, this protects an essential committer precondition. It also verifies bucket overrides and filesystem caches do not mask the disabled-MPU setting.
