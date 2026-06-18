<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/kbuf.h -->
# sources/distributed-fs/ceph-client/io_uring/kbuf.h

## Purpose
`kbuf.h` declares the internal data structures and APIs for io_uring provided buffers. It covers legacy buffer lists, mapped buffer rings, incremental consumption, multi-buffer selection arguments, buffer lifecycle helpers, registration hooks, and small inline helpers used by network/rw paths.

## Important APIs, Types, and Functions
- `IOBL_BUF_RING` marks mapped provided-buffer rings; `IOBL_INC` marks incremental buffer consumption.
- `struct io_buffer_list` stores either a legacy `buf_list` or mapped `buf_ring`, buffer count/group id, ring head/mask, flags, incremental threshold, and `io_mapped_region`.
- `struct io_buffer` is the legacy per-buffer node with address, length, buffer id, and group id.
- `struct buf_sel_arg` describes multi-buffer selection input/output: iovec storage, accumulated length, max length, vector count, allocation mode, group id, and partial-map indicator.
- Public helpers include `io_buffer_select()`, `io_buffers_select()`, `io_buffers_peek()`, `io_destroy_buffers()`, prep/issue functions for provide/remove buffers, pbuf registration/status functions, recycle/drop helpers, `__io_put_kbufs()`, `io_kbuf_commit()`, and `io_pbuf_get_region()`.
- Inline helpers include `io_kbuf_recycle_ring()`, `io_do_buffer_select()`, `io_kbuf_recycle()`, `io_put_kbuf()`, and `io_put_kbufs()`.

## Control Flow
Opcode handlers check `io_do_buffer_select()` to determine whether a request still needs buffer selection. After a transfer, handlers call `io_put_kbuf()` or `io_put_kbufs()` to commit buffers and obtain CQE flags. If an operation must retry or poll, `io_kbuf_recycle()` returns selected buffers where legal: ring buffers are cleared from request state, legacy selected buffers are reinserted into the group, and `REQ_F_BL_NO_RECYCLE` prevents unsafe reuse.

## State and Persistence Behavior
The header defines the persistent per-group state in `struct io_buffer_list` and the transient request state used by inline helpers. The `io_mapped_region` embedded in ring buffer lists persists until unregister or context teardown. Inline helpers mutate request flags to prevent double commit/recycle.

## Dependencies and Integration Points
It includes UAPI io_uring definitions and `io_uring_types.h`. It depends on `memmap.h` indirectly through `struct io_mapped_region` in the included type definitions. It is consumed by core completion paths, network send/recv, read/write, and mmap region dispatch.

## Risks and Edge Cases
- `io_put_kbuf()` and `io_put_kbufs()` are no-ops unless a buffer was actually selected, so callers must not rely on them for unrelated CQE flags.
- `io_kbuf_recycle_ring()` only clears flags when a valid list is supplied; null lists mean the buffer was already committed or cannot be recycled.
- `REQ_F_BL_NO_RECYCLE` is critical for bundle paths where buffers were already committed.

## Test Signals
Header-level signals come from builds across buffer-select users. Runtime signals should verify callers consistently call put/recycle helpers exactly once and preserve CQE buffer IDs for both single and multi-buffer selections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/kbuf.h -->
