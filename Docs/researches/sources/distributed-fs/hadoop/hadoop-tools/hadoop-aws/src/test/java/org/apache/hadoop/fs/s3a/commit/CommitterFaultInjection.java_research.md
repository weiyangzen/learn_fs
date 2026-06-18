<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/CommitterFaultInjection.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/CommitterFaultInjection.java

## Purpose

`CommitterFaultInjection` is a small interface that marks failing committer test implementations and defines which lifecycle operations can be forced to fail.

## Important APIs, Types, and Functions

- `COMMIT_FAILURE_MESSAGE` is the common failure text.
- `setFaults(Faults...)` configures active fault points.
- `Faults` enum covers `abortJob`, `abortTask`, `cleanupJob`, `commitJob`, `commitTask`, `getWorkPath`, `needsTaskCommit`, `setupJob`, and `setupTask`.

## Control Flow and State

Implementations are expected to store the configured enum set and throw when a matching lifecycle method is invoked. `AbstractITCommitProtocol` casts failing committers to this interface to inject `commitJob` failure and validate retry behavior.

## State and Persistence Behavior

The interface itself has no state. Implementations maintain in-memory fault sets.

## Dependencies and Integration Points

It is used by `CommitterFaultInjectionImpl` and abstract/protocol committer subclasses that need to provide failing variants.

## Risks and Edge Cases

The enum includes lifecycle points that may not be implemented by every failing committer wrapper. Tests relying on a specific fault require the committer under test to honor that enum member.

## Test Signals

The signal is an expected injected `IOException` with `COMMIT_FAILURE_MESSAGE`, followed by test-specific assertions about retry or cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/CommitterFaultInjection.java -->
