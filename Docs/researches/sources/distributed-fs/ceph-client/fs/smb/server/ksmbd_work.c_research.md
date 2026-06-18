# sources/distributed-fs/ceph-client/fs/smb/server/ksmbd_work.c

Purpose: implements allocation, freeing, queueing, and response-iovec construction for KSMBD request work items.

Important APIs/types/functions: `ksmbd_work_pool_init()`/`ksmbd_work_pool_destroy()` manage the `ksmbd_work_cache` slab. `ksmbd_workqueue_init()`/`ksmbd_workqueue_destroy()` manage the per-CPU `ksmbd-io` workqueue. `ksmbd_alloc_work_struct()` and `ksmbd_free_work_struct()` allocate/free `struct ksmbd_work`. `ksmbd_queue_work()` queues protocol work. `ksmbd_iov_pin_rsp()`, `ksmbd_iov_pin_rsp_read()`, and `allocate_interim_rsp_buf()` build response buffers.

Control flow: request processing allocates a zeroed work object, initializes compound FIDs to `KSMBD_NO_FID`, list heads, default iovec capacity, and a kvec array. Protocol handlers fill request/session/tree state and queue the embedded work item. Response building ensures the first iovec contains a 4-byte RFC1002 length field, appends response buffers and optional auxiliary read buffers, increments the stream length, and tracks auxiliary buffers for later cleanup. Freeing releases response/request buffers, transform buffers, iovecs, auxiliary read buffers, async IDs, and the slab object.

State and persistence behavior: all state is per-request and transient. The slab cache and workqueue persist while the server is running. Async message IDs are allocated from the connection IDA and released when the work object is freed.

Dependencies and integration points: depends on KSMBD server/connection state, IDA helpers, Linux slab/workqueue/list memory APIs, and common RFC1001 length helpers. It integrates with SMB2 command handlers, connection request queues, async cancellation, read response construction, and transport writev.

Risks: iovec growth and RFC1002 length increments must stay synchronized or clients receive malformed responses. Auxiliary read buffers are owned by the work object after pinning; double-free or missed list insertion causes memory bugs. `saved_cred` must be reverted before freeing, enforced by a warning. Async IDs must be released exactly once.

Test signals: simple and compound responses, large read responses with auxiliary buffers, iovec reallocation, interim responses, async request/cancel cleanup, error paths after partial response construction, and slab/workqueue leak checks on disconnect.
