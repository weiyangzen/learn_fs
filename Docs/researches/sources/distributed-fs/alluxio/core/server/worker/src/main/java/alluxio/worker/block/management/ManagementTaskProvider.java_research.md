# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/ManagementTaskProvider.java

Purpose: Factory interface for management subsystems that can supply the next pending task.

Important APIs: `getTask()` returns a `BlockManagementTask` or null.

Control flow: `ManagementTaskCoordinator` queries providers in order until one returns a task.

State and persistence: Interface only.

Dependencies and integration: Implemented by `TierManagementTaskProvider`.

Risks and test signals: Null is the no-work signal, so implementations must avoid returning null for transient failures without intentional backoff. Tests should verify coordinator priority and null handling.
