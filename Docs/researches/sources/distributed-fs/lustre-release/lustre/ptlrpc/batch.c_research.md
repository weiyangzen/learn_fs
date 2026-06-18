# Research: sources/distributed-fs/lustre-release/lustre/ptlrpc/batch.c

## Purpose
`batch.c` implements client-side batched metadata updates for Lustre. It groups multiple packed metadata update messages into one `MDS_BATCH` PTLRPC, sends the group inline or through a bulk transfer, dispatches per-subrequest callbacks from the batched reply, and can resend unfinished subrequests after server overflow.

## Important APIs, Types, And Functions
The public API is `cli_batch_create()`, `cli_batch_stop()`, `cli_batch_flush()`, and `cli_batch_add()`. Internally, `struct batch_update_head` tracks the export, owning `struct lu_batch`, update count, expected reply size, callback list, and update buffers. This file adds `struct batch_update_buffer` for allocated `batch_update_request` payloads, `struct batch_update_args` for PTLRPC async callback state, and `struct batch_work_resend` for deferred resend work.

Key helpers are `batch_prep_inline_update_req()`, `batch_prep_update_req()`, `batch_update_buffer_create()`, `batch_insert_update_callback()`, `batch_update_request_fini()`, `batch_update_interpret()`, `batch_send_update_req()`, `batch_update_request_add()`, and `cli_batch_resend_work()`.

## Control Flow
`cli_batch_create()` allocates a `cli_batch`, initializes flags and max count, and creates the first `batch_update_head` with a 4 KiB update buffer. `cli_batch_add()` creates a new head if the previous one was flushed, then calls `batch_update_request_add()`.

`batch_update_request_add()` repeatedly asks the caller-provided packer to encode an `md_op_item` into the current buffer. If the packer returns `-E2BIG`, it allocates a larger/new buffer sized from the packer's returned length and retries. On success it advances buffer offsets, increments request/update counts, accumulates reply size from `lm_repsize`, inserts the per-update callback, and auto-flushes if `lbt_max_count` is reached.

`batch_send_update_req()` converts the accumulated head into a PTLRPC request. `batch_prep_update_req()` chooses inline mode when there is one small buffer under `OUT_UPDATE_MAX_INLINE_SIZE`; otherwise it packs a header plus `but_update_buffer` descriptors and attaches a bulk descriptor with `ptlrpc_bulk_kiov_nopin_ops`. Non-read-only batches acquire a modification RPC slot. Synchronous batches call `ptlrpc_queue_wait()`, request-set batches add to the supplied set and check it, and default async batches go to `ptlrpcd`.

`batch_update_interpret()` releases the modification RPC slot, unpacks `RMF_BUT_REPLY`, validates `BUT_REPLY_MAGIC`, and calls `batch_update_request_fini()`. Finalization walks the callback list in request order, maps available embedded reply messages to callbacks, reports `-ECANCELED` for subrequests the server did not process, and schedules `cli_batch_resend_work()` when the enclosing RPC returned `-EOVERFLOW` and unfinished updates remain.

The resend worker creates a fresh head, copies or moves only unprocessed messages from the old buffers starting at `bwr_index`, splices callbacks to the new head, uses a conservative maximum reply size, sends the new request, and destroys the old head on success. On errors it finalizes both old and new heads with the error.

## State And Persistence
Batch state is transient and memory-resident. Buffers own packed subrequest bytes until the enclosing request completes or is resent. Callback objects carry caller data and interpreter functions and are freed after invocation. There is no disk persistence; durable effects are delegated to the MDS/MDT handlers that execute the embedded updates. Ordering is the insertion order in `buh_cb_list` and packed buffers.

## Dependencies And Integration Points
The file depends on PTLRPC request capsules, bulk descriptors, `ptlrpcd`, request sets, modification RPC slot accounting, Lustre message packing helpers, and batch wire structs such as `but_update_header`, `batch_update_request`, and `batch_update_reply`. It is paired with server-side batch handling in MDT/target code for `MDS_BATCH`. The Makefile builds `batch.o` into the PTLRPC module for both client and server-capable builds.

## Risks
The callback list and packed message stream must remain exactly aligned; any packer that reports an incorrect length or reply size can misroute subreply results. The overflow resend path transfers ownership of buffers and callbacks between heads, so cleanup ordering is delicate. In `batch_send_update_req()`, request-set handling calls `ptlrpc_check_set(env, bh->lbt_rqset)` and some callers pass `NULL` env elsewhere, so callback paths must tolerate the execution context used. Bulk buffer page counting is intentionally overestimated for partial first/last pages; changes there risk underallocating bulk fragments.

## Test Signals
Tests should cover inline vs bulk batch selection, read-only batches without modification slots, synchronous and asynchronous batches, request-set batches, packer `-E2BIG` growth, partial server replies, `-EOVERFLOW` resend from a nonzero subrequest index, callback return aggregation, and cleanup after allocation failures in buffer creation or resend work allocation.
