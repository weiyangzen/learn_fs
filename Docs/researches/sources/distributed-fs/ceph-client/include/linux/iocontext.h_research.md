# sources/distributed-fs/ceph-client/include/linux/iocontext.h

Purpose: This header defines per-task block I/O context state and queue-specific `io_cq` associations used by block elevators.

Important APIs, types, and functions: `struct io_context` holds refcounts, active refs, I/O priority, and, under `CONFIG_BLK_ICQ`, a lock, radix tree, hint, ICQ list, and release work. `struct io_cq` links an `io_context` to a `request_queue` with queue and ioc list nodes. APIs include `put_io_context`, `exit_io_context`, `__copy_io`, and `copy_io`.

Control flow: Block core creates and destroys `io_cq` objects when elevators request ICQ storage. Requests hold an extra `io_context` reference while using ICQ state. `copy_io` only calls the real clone helper when the current task has an `io_context`; no-block builds stub out all operations.

State and persistence: `io_context` is refcounted and may be shared between processes. ICQs are not individually refcounted; they are destroyed when either queue or context exits, with RCU used for lookup/free safety.

Dependencies and integration points: Depends on radix trees, RCU, workqueues, block queues, elevators, task clone/exit, and I/O priority code.

Risks: Lock ordering is subtle: ioc lock nests inside queue lock, while ioc exit needs reverse-order handling. ICQ lookup validity ends when the queue lock is released. Elevator-private ICQ extensions must embed `io_cq` first and respect size/alignment requirements.

Test signals: Exercise process clone/exit with shared and unshared I/O contexts, elevator ICQ allocation/destruction, RCU lookup under queue lock, request completion references, and `CONFIG_BLOCK`/`CONFIG_BLK_ICQ` stubs.
