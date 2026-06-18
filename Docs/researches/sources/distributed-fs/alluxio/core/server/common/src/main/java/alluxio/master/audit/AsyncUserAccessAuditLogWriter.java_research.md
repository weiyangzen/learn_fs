# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/audit/AsyncUserAccessAuditLogWriter.java

## Purpose
`AsyncUserAccessAuditLogWriter` asynchronously writes user access audit events to a configured logger.

## Important APIs, Types, And Functions
The constructor creates a bounded `LinkedBlockingQueue` from `MASTER_AUDIT_LOGGING_QUEUE_CAPACITY`. `start` creates the worker thread, `stop` interrupts and joins it, `append` blocks to enqueue an `AuditContext`, and `getAuditLogEntriesSize` exposes queue depth.

## Control Flow, State, Dependencies, Risks, And Tests
The worker loops while not stopped, takes audit contexts, and logs `toString()` at info level. State is in-memory queue and worker thread; persistence is delegated to the logging backend. Dependencies include SLF4J, `Configuration`, and `AuditContext`. Risks include append blocking under full queues, stop dropping queued entries because interruption exits immediately, appends accepted while stopped, and logging failures not handled. Tests should cover start/stop idempotency, queue capacity blocking/interrupt behavior, drain behavior on stop, and logger output.
