# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mem.c

Purpose: provides small DMA allocation/free helpers for Delta firmware command buffers and other hardware-visible allocations.

Important APIs and functions: `hw_alloc` allocates write-combined DMA memory, fills a caller-provided `struct delta_buf`, logs the allocation, and increments `ctx->sys_errors` on failure. `hw_free` logs and frees a previously allocated buffer with the stored attributes.

Control flow: codec and IPC code call `hw_alloc` when they need contiguous memory visible to the Delta firmware or hardware. The caller owns the `delta_buf` object and must call `hw_free` exactly once after successful allocation.

State and persistence: allocated memory is runtime DMA state only. Metadata stored in `delta_buf` includes size, virtual address, physical address, name, and DMA attributes.

Dependencies and integration points: depends on `delta.h`, Linux DMA APIs, and `delta_ctx->dev` for the device handle. Used by `delta-ipc.c` to allocate the shared IPC buffer.

Risks: `hw_free` assumes `buf`, `buf->vaddr`, and metadata are valid; no null guard exists. Allocation uses `__GFP_NOWARN`, so callers must rely on explicit driver errors and counters. Write-combine memory is suitable for hardware but requires care if CPU reads are expected.

Test signals: allocation failure injection, open/close leak checks, DMA mapping visibility to firmware, and repeated MJPEG instance creation/destruction.
