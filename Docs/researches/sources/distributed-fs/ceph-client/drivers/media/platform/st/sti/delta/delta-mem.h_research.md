# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mem.h

Purpose: declares Delta hardware-visible memory allocation helpers.

Important APIs and functions: exports `hw_alloc(struct delta_ctx *ctx, u32 size, const char *name, struct delta_buf *buf)` and `hw_free(struct delta_ctx *ctx, struct delta_buf *buf)`.

Control flow: callers allocate a `delta_buf` metadata structure, request a DMA buffer with a debug name, then free the same metadata through `hw_free`.

State and persistence: none in the header. Allocated DMA state is owned by the implementation and caller-provided `delta_buf`.

Dependencies and integration points: requires `struct delta_ctx` and `struct delta_buf` from `delta.h`. It is the local memory-management boundary for Delta IPC and future codec code.

Risks: the terse `hw_alloc`/`hw_free` names are generic inside the kernel tree and should remain file-local through includes to avoid confusion. Include order matters because this header does not include `delta.h`.

Test signals: compile coverage and allocation/free exercised by `delta_ipc_open` and `delta_ipc_close`.
