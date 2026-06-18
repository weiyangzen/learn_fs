# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditIntegration.java

## Purpose
`AuditIntegration` provides static glue for creating audit managers/auditors, attaching spans to AWS execution attributes, and translating audit-specific exceptions into Hadoop IO exceptions.

## Important APIs and control flow
`createAndStartAuditManager()` chooses `ActiveAuditManagerS3A` when auditing is enabled and `NoopAuditManagerS3A` otherwise, then initializes and starts the service. `createAndInitAuditor()` reflects the configured `OperationAuditor` class, defaulting to `LoggingAuditor`, and initializes it with `OperationAuditorOptions`. `retrieveAttachedSpan()` and `attachSpanToRequest()` read/write the internal execution attribute. `translateAuditException()` maps `AuditOperationRejectedException` to `UnsupportedRequestException`; other audit failures become `AccessDeniedException`. `maybeTranslateAuditException()` and `containsAuditException()` inspect direct and immediate-cause exceptions. `isRejectOutOfSpan()` reads the rejection flag.

## State, dependencies, and integration
The class is stateless. It depends on Hadoop configuration/service classes, AWS execution attributes, audit implementations, `IOStatisticsStore`, and `S3AInternalAuditConstants`. It is used during filesystem initialization and exception handling.

## Risks and test signals
Reflection failures must report the configured key/class clearly. Cause scanning is shallow and may miss deeply nested audit failures. Tests should cover enabled/disabled manager creation, custom auditor construction, span attribute round trip, exception translation paths, and reject-out-of-span configuration defaults.
