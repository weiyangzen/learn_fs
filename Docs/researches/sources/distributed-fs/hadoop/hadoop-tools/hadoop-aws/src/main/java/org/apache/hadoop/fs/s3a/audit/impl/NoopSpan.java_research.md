# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/NoopSpan.java

## Purpose
`NoopSpan` is a minimal `AuditSpanS3A` implementation with no direct audit side effects except optional activation/deactivation callbacks.

## Important APIs and control flow
The protected constructor stores span ID, operation name, paths, and callbacks. The singleton `INSTANCE` is a default no-op span. `activate()` and `deactivate()` notify callbacks when present and otherwise do nothing. `toString()` includes id, operation name, and paths.

## State, dependencies, and integration
State is immutable span metadata plus callback reference. It extends `AbstractAuditSpanImpl` and is produced by `NoopAuditor` and `NoopAuditManagerS3A`.

## Risks and test signals
The singleton has an empty span ID and `no-op` operation, so code requiring unique IDs should use auditor-created spans instead. Tests should cover callback invocation and harmless reuse of `INSTANCE`.
