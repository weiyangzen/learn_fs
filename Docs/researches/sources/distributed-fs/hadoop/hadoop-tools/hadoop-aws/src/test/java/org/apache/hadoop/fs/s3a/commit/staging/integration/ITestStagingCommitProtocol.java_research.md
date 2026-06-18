# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/integration/ITestStagingCommitProtocol.java

## Purpose
Base integration protocol specialization for staging committers. It adapts `AbstractITCommitProtocol` expectations to local staging work directories and validates staging upload directory cleanup on success and failure.

## Important APIs, Types, and Functions
The class extends `AbstractITCommitProtocol`, uses `StagingCommitter` by default, configures committer threads and disables unique filenames, and uses `Paths.getLocalTaskAttemptTempDir()` and `Paths.getStagingUploadsParentDirectory()`. It defines a fault-injecting `CommitterWithFailedThenSucceed`.

## Control Flow and Behavior
`setup()` generates a Spark write UUID, verifies `AbstractS3ACommitter.buildJobUUID()` selects it, and removes any existing local task attempt temp dir. Working directory validation expects local `file` scheme, while task attempt write validation asserts local file existence and length. Staging committers are expected not to create success markers in these protocol tests. Cleanup tests start a job, verify the staging uploads directory exists after `setupJob`, commit or fail the job, and then assert the staging uploads parent directory has been deleted.

## State, Persistence, and Dependencies
State includes local task attempt files, staging uploads directories, pending commit metadata, S3A final output, and job UUID configuration. Dependencies include the abstract protocol suite, staging path utilities, MR contexts, local filesystem, and committer fault injection.

## Integration Points, Risks, and Test Signals
This is the common protocol bridge for staging, directory, and partitioned committers. It catches regressions in local staging path lifecycle, Spark UUID propagation, cleanup on failed commit, and mismatch between expected local work paths and S3 final output.
