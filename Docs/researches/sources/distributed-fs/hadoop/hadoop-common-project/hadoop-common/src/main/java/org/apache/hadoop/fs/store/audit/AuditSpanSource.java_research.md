# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/AuditSpanSource.java

Purpose: factory interface for creating audit spans for filesystem operations.

Important APIs, types, and functions: `createSpan(String operation, @Nullable String path1, @Nullable String path2)`.

Control flow: filesystem entry points call `createSpan()` with operation name and relevant paths, then activate the returned span around work.

State and persistence: no state in the interface. Implementations may allocate span IDs, timestamps, and attach context for audit logs.

Dependencies and integration points: depends on `AuditSpan`, nullable annotations, and `IOException`. Operation names should come from `StoreStatisticNames` or `StreamStatisticNames`.

Risks and test signals: failures can throw `IOException` before an operation runs. Tests should cover path nullability, operation-name propagation, error handling, and returned span validity.
