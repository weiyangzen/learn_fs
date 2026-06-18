<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/waitqueue.c -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/waitqueue.c

## Purpose
Implements in-kernel operation queuing, blocking waits, retry behavior, purge handling, and cancellation waits for OrangeFS upcalls. It is the synchronization core between VFS callers and `pvfs2-client-core` downcalls.

## Important APIs, Types, and Functions
Primary functions are `service_operation`, `wait_for_matching_downcall`, `wait_for_cancellation_downcall`, `pvfs2_clean_up_interrupted_operation`, and `purge_waiting_ops`. It manipulates `pvfs2_kernel_op_t`, global `pvfs2_request_list`, `pvfs2_request_list_lock`, `request_semaphore`, per-op wait queues and locks, the operations-in-progress hash table, `pvfs2_bufmap_init_waitq`, and operation state helpers such as `op_state_waiting`, `set_op_state_purged`, and `set_op_state_interrupted`.

## Control Flow
`service_operation` stamps process identity on the upcall, optionally masks signals, optionally enters `request_semaphore`, increments attempts if the daemon is not in service, queues the op on the normal or priority request list, and returns immediately for asynchronous operations. Synchronous calls wait either for cancellation downcall or normal matching downcall. On success the downcall status is normalized to errno format. On unserviced `-EAGAIN`, non-shared-memory operations are requeued immediately; shared-memory operations wait briefly for bufmap initialization and return `-EAGAIN` so the caller can repopulate shared buffers.

## State and Persistence
Operation state is transient but concurrency-sensitive. Ops move through waiting, in-progress, serviced, purged, and interrupted states under per-op locks and list/hash locks. `attempts` controls retry and timeout behavior. `op->downcall.status` is the persistent result visible to callers after the wait completes.

## Dependencies and Integration Points
Integrates with device close/purge behavior, client-core service status checks, request-list insertion/removal, in-progress hash removal, signal masking helpers, bufmap initialization, and VFS operations throughout the kernel module. Mount remount priority operations in `super.c` rely on `PVFS2_OP_PRIORITY` and `PVFS2_OP_NO_SEMAPHORE` behavior here.

## Risks
Lock ordering is explicitly sensitive: cleanup locks op first, then list/hash helpers, while purge scans under request-list lock and then op lock. Incorrect changes can deadlock. Signal masking must be balanced on every exit. Timeout/retry paths can return `-EAGAIN`, `-EIO`, `-EINTR`, or `-ETIMEDOUT`; callers must handle each correctly. Shared-memory restart handling depends on `get_bufmap_init()` and can fail user I/O after the configured wait.

## Test Signals
Test normal lookup/getattr/statfs service, signal interruption of interruptible and non-interruptible operations, client-core shutdown purge and restart, repeated purge retry limit, cancellation requests with pending signals, daemon-not-in-service timeout behavior, priority remount ordering, and shared-memory operation recovery after bufmap reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/waitqueue.c -->
