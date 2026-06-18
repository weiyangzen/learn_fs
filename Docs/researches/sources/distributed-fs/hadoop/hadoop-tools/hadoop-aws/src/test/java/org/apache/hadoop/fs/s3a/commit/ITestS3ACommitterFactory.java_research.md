# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/ITestS3ACommitterFactory.java

## Purpose
Parameterized integration tests for `S3ACommitterFactory` selection rules. It verifies that committer names configured either in the filesystem configuration or in the task/job configuration produce the expected output committer class, and that invalid names fail with a path commit exception.

## Important APIs, Types, and Functions
The class extends `AbstractCommitITest` and is a JUnit 5 `@ParameterizedClass` over `BINDINGS`. It covers `FileOutputCommitter`, `PartitionedStagingCommitter`, `StagingCommitter`, `MagicS3GuardCommitter`, and `DirectoryStagingCommitter`. `maybeSetCommitterName()` mutates `FS_S3A_COMMITTER_NAME`, `createConfiguration()` clears bucket overrides, and `setup()` constructs a `JobConf`, `TaskAttemptID`, `TaskAttemptContextImpl`, output path, and `S3ACommitterFactory`.

## Control Flow and Behavior
Each parameter pair sets an optional filesystem-level committer name and an optional task-level committer name. `testBinding()` calls `assertFactoryCreatesExpectedCommitter()`, which either compares the exact class returned by `factory.createOutputCommitter(outDir, tContext)` or intercepts `PathCommitException` for invalid configuration. The setup explicitly closes cached filesystems for the current UGI so every parameter observes its own FS configuration.

## State, Persistence, and Dependencies
The test uses only configuration state and task attempt metadata; it does not rely on committed output. It depends on multipart upload availability, S3A committer constants, MR job/task config keys, and Hadoop filesystem caching behavior.

## Integration Points, Risks, and Test Signals
The main integration point is the precedence between filesystem and job-level committer options. A failure here usually means a regression in committer discovery, configuration override handling, or filesystem caching. The test is sensitive to default binding expectations: no committer name should produce `FileOutputCommitter`, while invalid names must be rejected rather than silently falling back.
