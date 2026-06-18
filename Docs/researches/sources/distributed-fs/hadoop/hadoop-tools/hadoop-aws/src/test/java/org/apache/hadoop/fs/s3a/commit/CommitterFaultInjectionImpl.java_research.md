<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/CommitterFaultInjectionImpl.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/CommitterFaultInjectionImpl.java

## Purpose

`CommitterFaultInjectionImpl` is a concrete `PathOutputCommitter` used to simulate failures at specific output committer lifecycle methods. It is a generic fault-injection implementation for committer tests.

## Important APIs, Types, and Functions

- Constructor takes output path, job context, `resetOnFailure`, and initial faults.
- `setFaults(Faults...)` replaces the active fault set.
- `maybeFail(Faults)` throws `Failure` if the condition is active and optionally removes it first.
- Lifecycle overrides call `maybeFail()` for `getWorkPath`, `setupJob`, `setupTask`, `needsTaskCommit`, `commitTask`, `abortTask`, `commitJob`, and `abortJob`.
- `Failure` extends `IOException` and uses `COMMIT_FAILURE_MESSAGE`.

## Control Flow and State

Each lifecycle method checks the `faults` set before returning or doing nothing. If `resetOnFailure` is true, the first failure at a given condition consumes that condition, allowing retry to succeed. `getOutputPath()` and non-faulting methods return null/no-op values because this class is not intended as a functional committer.

## State and Persistence Behavior

The fault set and reset flag are in-memory only. There is no filesystem state beyond the superclass constructor binding.

## Dependencies and Integration Points

It depends on Hadoop `PathOutputCommitter`, `JobContext`, `TaskAttemptContext`, and `JobStatus.State`. It is used directly or as a helper by failing S3A committer implementations.

## Risks and Edge Cases

Because it returns null paths and does not perform real commit logic, it is suitable only for targeted lifecycle failure tests. The `cleanupJob` enum member is declared in the interface but not handled here by an override.

## Test Signals

Tests observe `CommitterFaultInjectionImpl.Failure` at configured lifecycle points and, when `resetOnFailure` is used, successful retry after the first injected exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/CommitterFaultInjectionImpl.java -->
