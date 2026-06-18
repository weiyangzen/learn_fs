# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/AbstractOperationAuditor.java

## Purpose
`AbstractOperationAuditor` is the base service implementation for audit plugins. It manages initialization options, IO statistics, auditor IDs, span ID generation, and out-of-span rejection flags.

## Important APIs and control flow
`init(OperationAuditorOptions)` saves options/statistics and calls service `init(Configuration)`. `serviceInit()` reads reject-out-of-span configuration. `createSpanID()` combines the auditor UUID with a static counter. `setAuditFlags()` stores flags and calls `auditorFlagsChanged()`, which disables out-of-span rejection when `PermitOutOfBandOperations` is present.

## State, dependencies, and integration
State includes `IOStatisticsStore`, options, `AtomicBoolean rejectOutOfSpan`, a UUID-backed auditor ID, and current flags. It depends on `AuditIntegration`, `AuditorFlags`, `OperationAuditor`, and Hadoop service/config classes. Concrete implementations include `LoggingAuditor` and `NoopAuditor`.

## Risks and test signals
`auditorFlagsChanged()` assumes a non-null `EnumSet`; callers should not pass null. Static span counter is process-wide, which is fine for uniqueness but affects deterministic tests. Tests should cover reject flag defaults, flag override, ID uniqueness, and missing statistics validation.
