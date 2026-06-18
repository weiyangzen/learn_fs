# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/S3ACommitterFactory.java

## Purpose
MapReduce `PathOutputCommitter` factory for S3A. It selects the concrete S3A committer from configuration, falling back to the classic `FileOutputCommitter` when the file committer or an empty name is configured.

## Important APIs, Types, And Functions
`CLASSNAME` is the fully qualified factory name used in job configuration. `createTaskCommitter()` calls `chooseCommitterFactory()` and delegates to `DirectoryStagingCommitterFactory`, `PartitionedStagingCommitterFactory`, `MagicS3GuardCommitterFactory`, or test-only `StagingCommitterFactory`; unknown names raise `PathCommitException`.

## Control Flow
Selection first reads the resolved filesystem configuration, then lets the task/job configuration override `fs.s3a.committer.name`. Known committer names produce factory instances; `file` and empty produce null, triggering the standard file committer path and a warning about safety/performance.

## State And Persistence
Stateless. It relies on per-bucket configuration already resolved into the destination `S3AFileSystem` configuration.

## Dependencies And Integration Points
Connects Hadoop MapReduce output committer creation to S3A-specific committers. Depends on `AbstractS3ACommitterFactory`, committer name constants, and the destination `S3AFileSystem`.

## Risks
Misconfiguration silently falls back only for empty/file names; typos fail fast. The factory explicitly does not verify filesystem compatibility, so magic committer requirements are enforced later by the concrete committer.

## Test Signals
Exercise all configured names, task-config override precedence, unknown-name failures, logging of selected committers, and fallback behavior for empty/file committer names.
