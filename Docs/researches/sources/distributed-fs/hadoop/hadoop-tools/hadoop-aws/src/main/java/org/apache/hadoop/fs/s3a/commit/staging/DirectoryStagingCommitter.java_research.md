# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/DirectoryStagingCommitter.java

## Purpose
Staging committer variant that applies conflict resolution at the whole output directory level.

## Important APIs, Types, And Functions
`NAME` is `directory`. `setupJob()` checks the destination path and conflict policy before delegating to base setup. `preCommitJob()` delegates pending-file validation to the base class, then deletes the output directory only for `REPLACE`.

## Control Flow
During setup, an existing non-directory path always fails. Existing directories fail in `FAIL` mode and are permitted in `APPEND` or `REPLACE`. During pre-commit, `REPLACE` recursively deletes the output path after all task output has succeeded and before final MPU completion.

## State And Persistence
Uses inherited staging state: local task work directories, cluster pending sets, and pending MPUs. It adds no new persistent fields.

## Dependencies And Integration Points
Extends `StagingCommitter`; uses destination `FileSystem`, `ConflictResolution`, and inherited `ActiveCommit` job pre-commit flow.

## Risks
Whole-directory replacement is broad; deleting output during pre-commit must happen only after task success. `FAIL` only checks at setup, so concurrent external writes after setup are not rechecked here.

## Test Signals
Existing absent/file/directory destinations, all conflict policies, replace deletion timing, append preservation, and final job commit after replacement.
