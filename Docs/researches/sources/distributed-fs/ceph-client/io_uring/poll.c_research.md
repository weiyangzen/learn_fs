# sources/distributed-fs/ceph-client/io_uring/poll.c

Purpose: implements explicit `POLL_ADD`/`POLL_REMOVE` and internal async-poll arming used to retry operations when files are not immediately ready.

Important APIs/types/functions: key local types are `io_poll_update` and `io_poll_table`. Public entry points are `io_poll_add_prep()`, `io_poll_add()`, `io_poll_remove_prep()`, `io_poll_remove()`, `io_poll_cancel()`, `io_poll_remove_all()`, `io_arm_apoll()`, `io_arm_poll_handler()`, and `io_poll_task_func()`. `IO_POLL_CANCEL_FLAG`, `IO_POLL_RETRY_FLAG`, and the ref mask encode ownership and wake races in `req->poll_refs`.

Control flow: prep parses event masks and update flags. Arming initializes wait queue entries, calls `vfs_poll()`, records one or two waitqueues, inserts the request into the cancel hash, and either completes inline or hands ownership to task_work. Wake callbacks match poll masks, handle `POLLFREE`, remove one-shot entries, and queue `io_poll_task_func()`. Task work rechecks current readiness, posts multishot CQEs or reissues the original operation, then tears down waitqueue and cancel-table state. Removal can either cancel a poll or update its user data/events and re-arm it.

State and persistence: poll state lives in request flags, `poll_refs`, waitqueue entries, optional allocated double poll entry, `ctx->cancel_table`, and `req->apoll`. It is transient but highly concurrent with file waitqueue lifetime and task_work execution.

Dependencies/integration: depends on VFS poll callbacks, io_uring task work, cancellation matching, NAPI tracking, provided-buffer multishot read retry, and opcode pollability metadata from `opdef`.

Risks/test signals: risks center on ownership races, double-waitqueue allocation failure, `POLLFREE` lifetime, multishot overflow termination, and cancel/update interactions. Test with one-shot and multishot poll, edge vs level flags, event updates, fd/op/user-data cancellation, two-waitqueue files such as sockets, and poll-free teardown under concurrent close.
