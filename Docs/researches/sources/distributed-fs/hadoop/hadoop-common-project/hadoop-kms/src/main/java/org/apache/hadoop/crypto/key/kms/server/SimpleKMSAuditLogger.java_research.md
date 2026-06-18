# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/SimpleKMSAuditLogger.java

## Purpose
`SimpleKMSAuditLogger.java` is the default text-format KMS audit logger implementation.

## Important APIs, Types, and Functions
It implements `KMSAuditLogger`. `logAuditEvent` chooses an aggregate-aware format for whitelisted successful events and a simple key-value format otherwise. `initialize` and `cleanup` are no-ops. Logs are written to the logger named `kms-audit`.

## Control Flow
For aggregate-eligible events with user, key, and op, OK status is logged as status plus op/key/user/accessCount/interval. Unauthorized and other statuses fall back to `logAuditSimpleFormat`. The simple format includes non-empty op, key, and user fields, or only status plus extra message when no fields are present.

## State and Persistence
No mutable state is held beyond the logger reference. Persistence depends on the configured logging backend.

## Dependencies and Integration Points
It is instantiated by `KMSAudit` by default or via `hadoop.kms.audit.logger`. It uses Guava `Strings` and `Joiner` for output formatting.

## Risks
The class carries a strong compatibility warning: audit log text format should not change because external tools parse it. Aggregated and non-aggregated formats differ, which consumers must handle.

## Test Signals
Tests should snapshot log output for OK aggregate events, unauthorized fallback, empty-field events, extra message preservation, and default selection by `KMSAudit`.
