# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/AccessCheckingAuditor.java

## Purpose

`AccessCheckingAuditor.java` is a controllable no-op auditor used by access-check integration tests. It lets tests switch `checkAccess()` between allow and deny outcomes.

## Important APIs, Types, and Functions

The class extends `NoopAuditor`, exposes class name constant `CLASS`, stores an `accessAllowed` boolean, provides `setAccessAllowed(boolean)`, and overrides `checkAccess(Path, S3AFileStatus, FsAction)`.

## Control Flow

`checkAccess()` logs the path and current allow flag, then returns that flag. It does not inspect path, status, or requested action beyond logging.

## State and Persistence Behavior

The only mutable state is the in-memory `accessAllowed` flag on the auditor instance. It is not synchronized, which is acceptable for single-test control but important if reused concurrently.

## Dependencies and Integration Points

It integrates with S3A `S3AFileSystem.access()` through the audit access-check callback and with `ITestAuditAccessChecks`.

## Risks and Edge Cases

Because all paths share one flag, it cannot validate path-specific or action-specific authorization. It is a test double for control flow, not a policy model.

## Test Signals

Downstream signals are access success when true and `AccessControlException` plus audit failure metrics when false.
