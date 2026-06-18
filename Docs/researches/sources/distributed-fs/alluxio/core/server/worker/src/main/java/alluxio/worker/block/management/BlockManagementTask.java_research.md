# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockManagementTask.java

Purpose: Minimal interface for background worker block management jobs.

Important APIs: `run()` returns a `BlockManagementTaskResult`.

Control flow: `ManagementTaskCoordinator` obtains implementations from providers and runs them on the coordinator thread.

State and persistence: Interface only.

Dependencies and integration: Implemented by tier management tasks and returned by `ManagementTaskProvider`.

Risks and test signals: Implementations should be idempotent enough for repeated coordinator loops. Tests should check task result reporting for progress and no-progress cases.
