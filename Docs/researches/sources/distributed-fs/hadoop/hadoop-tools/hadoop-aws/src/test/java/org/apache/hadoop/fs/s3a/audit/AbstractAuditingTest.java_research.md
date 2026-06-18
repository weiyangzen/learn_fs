# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/AbstractAuditingTest.java

## Purpose

`AbstractAuditingTest.java` is the shared unit-test base for S3A audit-manager and auditor tests. It creates an audit manager, request factory, and IOStatistics store, then provides helpers to synthesize AWS SDK request callback sequences.

## Important APIs, Types, and Functions

Subclasses implement `createConfig()`. `setup()` creates a `RequestFactoryImpl` and starts an `AuditManagerS3A` through `AuditIntegration.createAndStartAuditManager()`. Helpers include `head()`, `get(range)`, `headForBulkDelete()`, `span()`, `activeSpan()`, `assertHeadUnaudited()`, and counter checks for `AUDIT_FAILURE` and `AUDIT_REQUEST_EXECUTION`.

## Control Flow

Request helpers construct S3 request builders, notify the manager through `requestCreated()`, build `InterceptorContext` and `ExecutionAttributes`, then run `beforeExecution()` and `modifyHttpRequest()` to simulate AWS SDK interceptor flow without performing network I/O.

## State and Persistence Behavior

The base owns a per-test `IOStatisticsStore`, `RequestFactory`, and audit manager. Teardown stops the manager quietly. Audit span state is thread-local/manager-local, not persisted.

## Dependencies and Integration Points

It ties together audit manager lifecycle, AWS SDK v2 interceptors, S3 request builders, Hadoop audit spans, and S3A statistics counters.

## Risks and Edge Cases

If the simulated callback order diverges from the AWS SDK flow, tests could miss integration regressions. The base deliberately exposes helpers for HEAD, GET with Range, and bulk delete to reduce that risk.

## Test Signals

Subclasses rely on active-span identity, generated referrer headers, expected audit exceptions, and IOStatistics counter values.
