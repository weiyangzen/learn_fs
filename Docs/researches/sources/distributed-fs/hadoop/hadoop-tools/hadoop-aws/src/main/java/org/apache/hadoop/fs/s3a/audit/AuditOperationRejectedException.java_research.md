# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditOperationRejectedException.java

## Purpose
`AuditOperationRejectedException` marks an audit failure where the auditor deliberately rejects an operation as forbidden or unavailable.

## Important APIs and control flow
It extends `AuditFailureException` and provides message and message-plus-cause constructors. `AuditIntegration.translateAuditException()` treats this subclass specially and emits `UnsupportedRequestException`.

## State, dependencies, and integration
State is inherited exception data. It is used by `LoggingAuditor` when multipart requests are attempted while multipart uploads are disabled.

## Risks and test signals
Tests should ensure rejected audit operations translate to unsupported-request IO errors, not generic access-denied errors, and that rejected SDK interceptor exceptions increment audit failure counters.
