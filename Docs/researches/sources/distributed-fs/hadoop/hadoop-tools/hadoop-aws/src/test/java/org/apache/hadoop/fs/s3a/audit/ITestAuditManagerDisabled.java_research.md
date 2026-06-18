# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/ITestAuditManagerDisabled.java

## Purpose

`ITestAuditManagerDisabled.java` verifies that setting `AUDIT_ENABLED=false` produces a no-op audit manager and stable no-op spans in an S3A filesystem.

## Important APIs, Types, and Functions

The test extends `AbstractS3ACostTest`, resets audit options, disables auditing, then asserts the filesystem audit manager is `NoopAuditManagerS3A`. It also compares spans returned by `fs.createSpan()` with `AuditTestSupport.NOOP_SPAN`.

## Control Flow

Filesystem construction uses the disabled audit configuration. Tests retrieve the manager and create two spans, expecting the no-op singleton span in both cases.

## State and Persistence Behavior

No real audit span state should be stored. All spans are the shared no-op span, so there is no per-operation lifecycle state.

## Dependencies and Integration Points

This covers S3A filesystem startup, audit manager selection, and no-op span behavior.

## Risks and Edge Cases

Any accidental creation of active audit managers when disabled would introduce overhead and possibly referrer headers or rejection behavior into disabled deployments.

## Test Signals

Signals are manager class identity and object identity of all created spans with `NOOP_SPAN`.
