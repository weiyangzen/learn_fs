# sources/distributed-fs/openafs/src/util/work_queue.h

Purpose: Public API header for the OpenAFS work queue package.

Important APIs and constants: Defines package error constants `AFS_WQ_ERROR`, `AFS_WQ_ERROR_RECOVERABLE`, and `AFS_WQ_ERROR_RESCHEDULE`. Declares all public queue, node, dependency, scheduling, execution, and wait functions implemented in `work_queue.c`.

Control flow and state: Header-only declaration layer. The public types are incomplete or option/callback types from `work_queue_types.h`; implementation internals stay hidden unless `work_queue_impl_types.h` is included by the implementation.

Dependencies and integration: Includes `work_queue_types.h`. Intended for volume/package code or other subsystems needing asynchronous dependency-aware work scheduling.

Risks and test signals: Error constants are marked as a future error-table TODO, so callers depend on raw negative values. API docs imply `afs_wq_del()` exists, but implementation returns `ENOTSUP`. Tests should compile against this header and exercise public API semantics.
