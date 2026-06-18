# sources/distributed-fs/ceph-client/fs/smb/server/ksmbd_work.h

Purpose: defines the per-request `struct ksmbd_work` context and declares work-pool, workqueue, and response-iovec helper APIs.

Important APIs/types/functions: `enum KSMBD_WORK_*` describes active/cancelled/closed work state. `struct aux_read` tracks extra read buffers attached to response iovecs. `struct ksmbd_work` contains connection/session/tree pointers, request and response buffers, response iovecs, compound request/response offsets, compound FIDs, saved credentials, credits granted, transform buffer, state bits for encrypted/async/no-response/RDMA invalidation, async cancel metadata, embedded `work_struct`, request/async/file list entries, and auxiliary read list. Inline helpers return current/next SMB2 request/response buffer pointers.

Control flow: connection/protocol code allocates a work item, parses command buffers using the inline offset helpers, processes the command on the KSMBD workqueue, builds iovecs, writes the response, dequeues the work, and frees it.

State and persistence behavior: work items are transient request state. Compound offsets and FIDs persist only for the lifetime of one SMB request chain. Saved credentials must be reverted before destruction.

Dependencies and integration points: depends on Linux workqueues, ctype helpers, KSMBD connection/session/tree types, SMB protocol definitions, async cancellation, RDMA response metadata, and VFS/file operation paths that attach `fp_entry`.

Risks: pointer arithmetic assumes response/request buffers include the 4-byte RFC1002 prefix and valid compound offsets. Incorrect async state can leave cancellation callbacks or async IDs dangling. The struct is central and shared across protocol handlers, so field lifetime conventions must be maintained.

Test signals: command parsing for compound chains, async create/ioctl/read paths, encrypted requests, cancelled requests, RDMA read/write responses, saved credential warning coverage, and workqueue cleanup at server shutdown.
