# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/AbstractAuditSpanImpl.java

## Purpose
`AbstractAuditSpanImpl` is the base class for S3A audit span implementations, providing immutable span ID, timestamp, and operation name handling.

## Important APIs and control flow
Constructors set the span ID, timestamp (defaulting to `Time.now()`), and operation name. `getSpanId()`, `getOperationName()`, and `getTimestamp()` expose these values. Default `activate()` returns `this`. `close()` is final and delegates to `deactivate()`, enforcing try-with-resources semantics through the `AuditSpan` lifecycle.

## State, dependencies, and integration
State is immutable per span. Dependencies are `AuditSpanS3A`, Hadoop `AuditSpan`, and `Time`. It is extended by `LoggingAuditor.LoggingAuditSpan`, `WarningSpan`, `NoopSpan`, and `ActiveAuditManagerS3A.WrappingAuditSpan`.

## Risks and test signals
Subclasses must implement valid deactivation behavior because `close()` is final. Tests should verify timestamps are set, null span IDs fail, and try-with-resources calls subclass `deactivate()`.
