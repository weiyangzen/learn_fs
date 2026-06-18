# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/TestAuditIntegration.java

## Purpose

`TestAuditIntegration.java` unit-tests S3A audit integration points that are independent of a live S3 filesystem: exception translation, auditor instantiation, manager lifecycle, interceptor creation, and span attachment.

## Important APIs, Types, and Functions

It exercises `S3AUtils.translateException()`, `S3ARetryPolicy`, `AuditIntegration.createAndInitAuditor()`, `createAndStartAuditManager()`, `stubAuditManager()`, `attachSpanToRequest()`, and `retrieveAttachedSpan()`. It also checks `AUDIT_SPAN_EXECUTION_ATTRIBUTE`.

## Control Flow

Tests translate audit exceptions and inspect resulting types/retry decisions. Auditor tests create no-op or logging auditors, assert service states, close managers, and verify lifecycle propagation. Interceptor tests simulate the basic AWS SDK callback sequence and ensure an invalid span is attached when no active span exists.

## State and Persistence Behavior

The class owns an IOStatistics store. Manager/auditor state follows Hadoop service lifecycle and is explicitly closed or checked for stopped state.

## Dependencies and Integration Points

This covers audit integration factory methods, Hadoop service state, AWS SDK v2 interceptors, request factory builders, retry policy behavior, and span execution attributes.

## Risks and Edge Cases

Misclassification of audit failures can cause wrong retry behavior or wrong public exception type. Interceptor sequence tests are synthetic but cover key transition points.

## Test Signals

Signals include `AccessDeniedException` translation, fail-fast retry decision for unsupported audit operation, service started/stopped assertions, interceptor list size/type, and span identity round trip through execution attributes.
