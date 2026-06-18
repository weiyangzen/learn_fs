# sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_vb2.c

## Purpose

`dvb_vb2.c` adapts the videobuf2 core to DVB demux capture buffers. It provides a small DVB-facing context that supports mmap buffer allocation, queue/dequeue/query/export operations, stream on/off, poll/mmap wrappers, and a demux callback helper that copies incoming TS or section data into queued vb2 buffers.

Only `VB2_MMAP` is supported in this implementation, using `vb2_vmalloc_memops`. The code is intended for DVB demux devices that expose the newer buffer API through `dmx_buffer` request/query/qbuf/dqbuf style operations.

## Important APIs, Types, And Functions

The queue ops are `_queue_setup`, `_buffer_prepare`, `_buffer_queue`, `_start_streaming`, and `_stop_streaming`. Buffer conversion ops are `_fill_dmx_buffer` and `_fill_vb2_buffer`.

The exported DVB-facing functions are `dvb_vb2_init`, `dvb_vb2_release`, `dvb_vb2_stream_on`, `dvb_vb2_stream_off`, `dvb_vb2_is_streaming`, `dvb_vb2_fill_buffer`, `dvb_vb2_reqbufs`, `dvb_vb2_querybuf`, `dvb_vb2_expbuf`, `dvb_vb2_qbuf`, `dvb_vb2_dqbuf`, `dvb_vb2_mmap`, and `dvb_vb2_poll`.

`struct dvb_vb2_ctx` fields used here include `vb_q`, `slock`, `dvb_q`, `buf`, `buf_siz`, `buf_cnt`, `remain`, `offset`, `flags`, `count`, `nonblocking`, `state`, and `name`. `struct dvb_buffer` wraps a `vb2_buffer` plus list node.

## Control Flow

Initialization clears the context, configures a capture queue, sets mmap-only I/O, installs queue and buffer ops, points queue locking at the caller-provided mutex, initializes the DVB queued-buffer list, stores the context name and nonblocking behavior, marks the state initialized, and calls `vb2_core_queue_init`.

`REQBUFS` clamps requested buffer size to `DVB_V2_MAX_SIZE`, stores size/count in the context, and calls `vb2_core_reqbufs` with `VB2_MEMORY_MMAP`. Queue setup then exposes one plane per buffer sized to `ctx->buf_siz`. Buffer prepare verifies the plane is large enough and sets initial payload to the full configured size. Buffer queue appends the DVB buffer to `ctx->dvb_q` under `slock`.

Streaming on/off delegates to vb2 core and updates state bits. Stop streaming drains all queued DVB buffers and completes them with `VB2_BUF_STATE_ERROR`.

`dvb_vb2_fill_buffer` is the data path. It ignores null/zero source calls, captures demux buffer flags into `ctx->flags`, obtains the next queued vb2 buffer if none is active, drops data if no buffer exists, aborts the current buffer if streaming has stopped, copies as much input as fits into the current plane, completes full buffers with `VB2_BUF_STATE_DONE`, and optionally flushes a partially filled buffer as done.

## State And Persistence Behavior

State is entirely per `dvb_vb2_ctx` and volatile. Buffer ownership moves from userspace/vb2 to the driver list via `_buffer_queue`, to active `ctx->buf` during fill, and back to vb2 with DONE or ERROR completion. `ctx->flags` accumulates demux buffer flags until `dvb_vb2_dqbuf`, where they are copied to userspace and cleared; `ctx->count` increments per dequeue.

`ctx->state` tracks initialized, requested-buffers, and stream-on states. Error paths often set state to `DVB_VB2_STATE_NONE`, so callers should treat failed core vb2 operations as requiring reinitialization or careful recovery.

Synchronization uses the vb2 queue mutex supplied by the caller for core operations and `ctx->slock` for the internal DVB queue, active buffer pointer, offsets, flags, and counter.

## Dependencies And Integration Points

The file depends on `media/dvb_vb2.h`, `media/dvbdev.h`, videobuf2 core, and the vmalloc memory allocator. It is used by DVB demux/DVR implementations that need mmap-backed capture rather than older ringbuffer read paths. The demux callback passes `enum dmx_buffer_flags` to `dvb_vb2_fill_buffer`, and userspace observes those flags on dequeue.

## Risks And Edge Cases

The data path silently drops bytes when no queued buffer is available, logging only by debug level. Partial flush uses `vb2_set_plane_payload(&ctx->buf->vb, 0, ll)`, where `ll` is the last copy chunk length rather than the accumulated `ctx->offset`; this is a high-value review/test target because a flushed partial buffer may report too few bytes used after multiple copy iterations.

`_buffer_prepare` sets payload to full buffer size before data is captured, which is common for fixed-size capture buffers but can be misleading if users expect payload to reflect actual bytes until DONE. Request size has a maximum but is not rounded to 188/204-byte TS packet multiples despite a FIXME. Error paths in stream on/off and reqbufs clear the whole state, which may make recovery coarse.

The function ignores `flush` calls with null source because it returns early on `!src || !len`; if callers use a second null callback to signal end-of-frame, that signal is not enough to flush unless they pass data and `flush=true`.

## Test Signals

Tests should cover queue setup size/count propagation, prepare rejecting undersized planes, qbuf list insertion, streamoff completing all queued buffers as ERROR, fill with no queued buffers, fill across multiple queued buffers, flush of partial buffers, demux flag propagation and clearing on dqbuf, nonblocking dqbuf behavior, query/export/mmap/poll wrappers, max-size clamping, and stop-streaming while a buffer is active.
