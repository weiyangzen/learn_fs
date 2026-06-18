# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/magic/ITestMagicCommitProtocol.java

## Purpose
Integration tests for the low-level magic committer protocol, reusing the abstract committer protocol suite while specializing path, marker, cleanup, and fault-injection behavior for `MagicS3GuardCommitter`.

## Important APIs, Types, and Functions
The class extends `AbstractITCommitProtocol`, is parameterized over `FS_S3A_COMMITTER_MAGIC_TRACK_COMMITS_IN_MEMORY_ENABLED`, and returns `COMMITTER_NAME_MAGIC`. It creates `MagicS3GuardCommitter` instances, verifies magic FS support, overrides validation hooks, and defines `CommitterWithFailedThenSucceed` backed by `CommitterFaultInjectionImpl`.

## Control Flow and Behavior
Configuration removes bucket overrides and sets in-memory commit tracking on or off. During setup it verifies the S3A filesystem supports magic commits. Task write validation asserts paths contain `__magic/<uuid>/` and are not visible during write. After write, the test verifies the `.pending` sidecar, lists the marker as zero length, and checks marker xattrs. Working directory validation requires an `s3a` scheme and a magic UUID path. `testCommittersPathsHaveUUID()` checks task and temporary paths include or exclude magic/base/temp components appropriately. `testCommitterCleanup()` commits with cleanup enabled and disabled and asserts whether the job attempt path remains.

## State, Persistence, and Dependencies
State is persisted in S3 magic marker files, `.pending` metadata, and optional in-memory tracking lists. Dependencies include `AbstractITCommitProtocol`, `MagicS3GuardCommitter`, `CommitUtilsWithMR.getMagicJobPath()`, list/filter utilities, and fault-injection wrappers around committer lifecycle calls.

## Integration Points, Risks, and Test Signals
This file validates the magic committer contract against the shared MR output protocol tests. It is sensitive to UUID scoping, marker visibility, pending metadata discovery, cleanup settings, and retries after commit failure. Passing both in-memory tracking modes is important because production deployments may choose either metadata discovery strategy.
