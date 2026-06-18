# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/AbstractBlockManagementTask.java

Purpose: Shared base for background block management tasks, wiring common store, metadata, load, executor, and transfer-executor dependencies.

Important APIs: Constructor stores dependencies and creates a `BlockTransferExecutor` using `WORKER_MANAGEMENT_BLOCK_TRANSFER_CONCURRENCY_LIMIT`.

Control flow: Concrete tasks call `mTransferExecutor` to execute generated move or swap orders.

State and persistence: Holds references for a single task instance. No persistence.

Dependencies and integration: Used by tier tasks `AlignTask`, `PromoteTask`, and `SwapRestoreTask`.

Risks and test signals: The eviction view is captured at task creation, so long-running tasks may act on stale metadata. Tests should verify configured concurrency is passed and concrete task constructors wire dependencies correctly.
