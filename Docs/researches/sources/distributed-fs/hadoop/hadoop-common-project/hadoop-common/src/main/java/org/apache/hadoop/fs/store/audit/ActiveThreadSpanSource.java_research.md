# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/ActiveThreadSpanSource.java

Purpose: generic interface for filesystem implementations that can expose the currently active audit span for the calling thread.

Important APIs, types, and functions: `getActiveAuditSpan()` returning a non-null span of type `T extends AuditSpan`.

Control flow: callers can capture the active span and propagate it into other threads or asynchronous work; the returned span may be invalid but must not be null.

State and persistence: no state in the interface. Implementations usually read thread-local or filesystem-specific active span state.

Dependencies and integration points: depends on `AuditSpan`. Used by audited filesystems to bridge thread-local span context into async operations.

Risks and test signals: returning null violates the contract and can break propagation code. Tests should cover inactive-span behavior, non-null guarantee, and cross-thread propagation.
