<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block/mq/operations.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/block/mq/operations.rs

## Purpose
This file defines the Rust trait and generated C vtable used by blk-mq to call into Rust block drivers.

## Important APIs, Types, and Functions
`Operations` requires an associated `QueueData: ForeignOwnable` and callbacks `queue_rq`, `commit_rqs`, and `complete`, with optional `poll`. `OperationsVTable<T>` builds a `bindings::blk_mq_ops` with callbacks for queueing, commits, completion, polling, hardware-context init/exit, and request init/exit.

## Control Flow and State
`queue_rq_callback` receives `blk_mq_queue_data`, casts the request to `Request<T>`, sets the Rust request refcount to `2` for one `ARef` plus in-flight ownership, creates `ARef`, borrows queue data from `queue.queuedata`, starts the request with `blk_mq_start_request`, and calls `T::queue_rq`. Errors convert to blk status. `commit_rqs_callback` borrows queue data and calls `T::commit_rqs`. `complete_callback` reconstructs the `ARef` leaked by `Request::complete` and calls `T::complete`. `init_request_callback` initializes per-request `RequestDataWrapper.refcount`; `exit_request_callback` drops it.

## State and Persistence Behavior
Per-request Rust state lives in the blk-mq private PDU area sized by `TagSet`. Queue data is a foreign-owned pointer installed by `GenDiskBuilder` and borrowed during callbacks. The static vtable persists for the driver type.

## Dependencies and Integration Points
This file integrates directly with C `blk_mq_ops`, `blk_mq_hw_ctx`, request PDU storage, `ARef`, `Refcount`, `ForeignOwnable`, and kernel error conversion. It is consumed by `TagSet::new`.

## Risks
The callback contracts are strict: C pointers must be valid, request private data must be initialized, and queue data must outlive callbacks. The refcount transition in `queue_rq_callback` is the root of later request-ending safety. Returning success without eventually ending the request can stall I/O; ending with extra refs fails in `Request`. Optional callbacks are installed only when vtable metadata says they exist.

## Test Signals
No local tests exist. Useful signals are compile-time vtable generation, a minimal block driver example, and runtime tests that queue, complete, poll, and tear down requests without refcount panics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block/mq/operations.rs -->
