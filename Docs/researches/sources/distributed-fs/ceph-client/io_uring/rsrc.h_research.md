# sources/distributed-fs/ceph-client/io_uring/rsrc.h

Purpose: defines resource-node and mapped-buffer structures plus inline lookup/ref helpers for registered files and buffers.

Important APIs/types/functions: `IORING_RSRC_FILE`, `IORING_RSRC_BUFFER`, `struct io_rsrc_node`, `struct io_mapped_ubuf`, `struct io_imu_folio_data`, and flags `IO_IMU_DEST`, `IO_IMU_SOURCE`, `IO_REGBUF_F_KBUF`. Inline helpers include `io_rsrc_node_lookup()`, `io_put_rsrc_node()`, `io_reset_rsrc_node()`, `__io_unaccount_mem()`, `io_vec_reset_iovec()`, and `io_alloc_cache_vec_kasan()`. Prototypes expose registration, import, accounting, clone, and vector allocation APIs.

Control flow: inline lookup bounds-checks with nospec indexing. Put/reset require `ctx->uring_lock`, decrement node refs, free on zero, and clear table slots. Vector helpers free/repoint cached iovec storage.

State and persistence: defines the shape of fixed resource state: file pointer or mapped buffer, tag, refs, pinned bvec metadata, accounting, release callback, direction mask, and optional kernel-buffer flag.

Dependencies/integration: consumed by open/close, splice, read/write, uring_cmd, register, and filetable code. It requires io_uring core types, lockdep, folio/page and iov iterator users.

Risks/test signals: wrong locking around `io_put_rsrc_node()` or `io_reset_rsrc_node()` risks UAF. Header tests are indirect through fixed-resource registration, fixed IO, uring_cmd fixed imports, and KASAN/fault-injection paths.
