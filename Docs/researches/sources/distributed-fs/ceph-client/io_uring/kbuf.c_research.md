<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/kbuf.c -->
# sources/distributed-fs/ceph-client/io_uring/kbuf.c

## Purpose
`kbuf.c` implements io_uring provided buffers. It supports legacy kernel-managed buffer lists supplied by `IORING_OP_PROVIDE_BUFFERS`, ring-mapped provided buffers registered with `io_register_pbuf_ring()`, incremental buffer consumption, buffer selection for recv/send/write-style operations, buffer recycling/drop, buffer removal, status query, and cleanup at ring teardown.

## Important APIs, Types, and Functions
- `struct io_provide_buf` is the per-request command payload for provide/remove buffer operations.
- `io_kbuf_commit()` commits selected ring buffers after a transfer, advancing `head` or incrementally shortening buffers for `IOBL_INC`.
- `io_buffer_select()` selects one provided buffer from a legacy list or mapped buffer ring.
- `io_buffers_select()` selects one or more buffers for bundle operations, optionally expanding the iovec array.
- `io_buffers_peek()` peeks multiple buffers while the caller holds `uring_lock`, used when selection and later commit must be coordinated.
- `__io_put_kbufs()`, `io_kbuf_recycle_legacy()`, and `io_kbuf_drop_legacy()` return CQE buffer flags, commit ring buffers, or put legacy buffers back/drop them.
- `io_manage_buffers_legacy()` handles `IORING_OP_PROVIDE_BUFFERS` and `IORING_OP_REMOVE_BUFFERS`.
- `io_register_pbuf_ring()`, `io_unregister_pbuf_ring()`, and `io_register_pbuf_status()` manage mapped provided-buffer rings.
- `io_pbuf_get_region()` integrates pbuf ring mmap offsets with `memmap.c`.
- `io_destroy_buffers()` frees all buffer groups during context teardown.

## Control Flow
Legacy provide/remove requests are prepared by `io_provide_buffers_prep()` and `io_remove_buffers_prep()`, validating counts, address ranges, buffer IDs, and reserved SQE fields. `io_manage_buffers_legacy()` locks the ring, looks up the buffer group, creates one if providing to a missing group, rejects operations against mapped ring groups, then adds or removes `struct io_buffer` nodes.

Runtime buffer selection locks the ring with `io_ring_submit_lock()`, looks up `ctx->io_bl_xa[bgid]`, then chooses legacy or ring behavior. Legacy selection pops a `struct io_buffer` from `buf_list`, stores it in `req->kbuf`, sets `REQ_F_BUFFER_SELECTED`, and returns its user pointer. Ring selection reads the userspace ring tail with acquire semantics, reads the buffer at `head`, sets `REQ_F_BUFFER_RING|REQ_F_BUFFERS_COMMIT`, stores `req->buf_index`, and either commits immediately for unlocked/non-pollable cases or returns a `buf_list` for later commit.

Bundle selection uses `io_ring_buffers_peek()` to map multiple ring entries into an iovec array, optionally expanding the vector when data is known to exist. It records `out_len`, truncates to `max_len`, marks partial maps for non-incremental buffers, and sets `REQ_F_BL_EMPTY` when the ring drains. Finalization through `__io_put_kbufs()` returns `IORING_CQE_F_BUFFER` plus the selected bid and may add `IORING_CQE_F_BUF_MORE` for incremental buffers with remaining data.

Registration of pbuf rings copies `io_uring_buf_reg`, validates flags and power-of-two entry count, prevents ambiguous full/empty rings, rejects `min_left` without incremental mode, creates or replaces an empty legacy group, creates an `io_mapped_region` either from kernel pages or user-provided memory, validates SHM color aliasing where needed, initializes mask/flags/head, and publishes the buffer list under `mmap_lock`.

## State and Persistence Behavior
Buffer groups live in `ctx->io_bl_xa` indexed by `bgid`. Legacy groups persist as linked lists of heap `struct io_buffer` nodes and `nbufs`. Ring groups persist as `struct io_buffer_list` with `buf_ring`, `head`, `mask`, flags, `min_left_sub_one`, and an owned `io_mapped_region`. Userspace owns the ring tail and buffer descriptors; the kernel owns `head` and commit behavior. `io_buffer_add_list()` publishes groups under `mmap_lock` because mmap lookup can access the xarray without `uring_lock`.

Requests carry transient state in `req->kbuf`, `req->buf_index`, and flags such as `REQ_F_BUFFER_SELECTED`, `REQ_F_BUFFER_RING`, `REQ_F_BUFFERS_COMMIT`, `REQ_F_BUF_MORE`, `REQ_F_BL_EMPTY`, and `REQ_F_BL_NO_RECYCLE`. Cleanup must drop or recycle legacy buffers and commit or clear ring-buffer state.

## Dependencies and Integration Points
This module depends on `io_uring.h` for request flags and locking, `opdef.h` for opcode dispatch, and `memmap.h` for mapped region allocation/free. `net.c`, `rw.c`, and uring command paths call buffer selection helpers and include returned CQE flags in completions. `memmap.c` calls `io_pbuf_get_region()` for pbuf ring mmap offsets.

## Risks and Edge Cases
- Incremental commit must not consume a zero-length transfer and must avoid infinite loops on invalid zero-length buffer descriptors.
- Ring `head`/userspace `tail` use 16-bit arithmetic; entry counts >= 65536 are rejected to preserve full/empty disambiguation.
- Unlocked io-wq selection commits immediately because another request could otherwise reuse the same ring entry.
- A legacy buffer selected before the group is upgraded or removed is dropped instead of recycled.
- Partial bundle maps can shorten non-incremental buffer lengths visible to userspace, so bundle retry paths must respect `partial_map`.
- Publishing/removing buffer groups must coordinate `uring_lock` with `mmap_lock` to avoid mmap seeing freed regions.

## Test Signals
Tests should cover legacy provide/remove counts and BID overflow, selection from empty groups, recycle after async retry, mapped pbuf registration/unregistration/status, mmap of pbuf regions, incremental buffer consumption including zero/partial transfers, bundle send/recv with vector expansion, CQE buffer flags and `BUF_MORE`, group replacement rules, and teardown with mixed legacy and mapped groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/kbuf.c -->
