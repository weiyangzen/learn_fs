# sources/distributed-fs/openafs/src/util/work_queue_impl.h

Purpose: Implementation-private umbrella header for the work queue package.

Important content: Includes the public `work_queue.h` and private `work_queue_impl_types.h`. It intentionally exposes no additional functions.

Control flow and state: Header-only include aggregator. Access to private types is guarded by `work_queue_impl_types.h`, which requires `__AFS_WORK_QUEUE_IMPL`.

Dependencies and integration: Included by `work_queue.c` after defining `__AFS_WORK_QUEUE_IMPL`. Not intended for external consumers.

Risks and test signals: Misuse outside implementation should be caught by the private types header. Compile-time enforcement is the main signal.
