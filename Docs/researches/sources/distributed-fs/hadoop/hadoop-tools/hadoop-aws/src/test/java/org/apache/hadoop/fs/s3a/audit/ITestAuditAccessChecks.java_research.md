# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/ITestAuditAccessChecks.java

## Purpose

`ITestAuditAccessChecks.java` is an S3A integration-cost test proving `S3AFileSystem.access()` delegates to the configured auditor and reports correct metrics for allowed, denied, and missing paths.

## Important APIs, Types, and Functions

It extends `AbstractS3ACostTest`, configures `AccessCheckingAuditor`, retrieves it from the filesystem in `setup()`, and tests file, directory, root, denied file, denied directory, and missing-path access cases. The local `access()` helper invokes `fs.access(path, FsAction.ALL)`.

## Control Flow

Allowed tests create a file/directory and verify access succeeds with expected metadata/list probes. Denied tests first create the target, switch the auditor to deny, and expect `AccessControlException` after existence probing. Missing-path access expects `FileNotFoundException` before the auditor denial is applied.

## State and Persistence Behavior

The test creates real S3 paths through the contract filesystem. Mutable auditor state controls authorization. Metrics are live filesystem IOStatistics.

## Dependencies and Integration Points

This validates `S3AFileSystem.access()`, audit access-check callback flow, `AccessCheckingAuditor`, cost validation helpers, and S3A statistic names.

## Risks and Edge Cases

Access checks are expected after status probing, so denial costs differ for file and directory targets. Missing paths must remain FNFE, not access denied.

## Test Signals

Signals include `INVOCATION_ACCESS`, `AUDIT_ACCESS_CHECK_FAILURE`, `AUDIT_REQUEST_EXECUTION`, `STORE_IO_REQUEST`, and operation-cost probes for file, directory, and root status.
