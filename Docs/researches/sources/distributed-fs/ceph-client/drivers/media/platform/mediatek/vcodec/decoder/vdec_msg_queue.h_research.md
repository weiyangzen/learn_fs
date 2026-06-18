## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_msg_queue.h

Purpose: declares the data structures and public API for MediaTek decoder LAT/core message queues.

Important APIs/types/functions: `NUM_BUFFER_COUNT` fixes the LAT pool at three buffers. `core_decode_cb_t` is the codec-specific callback executed by core work. `enum core_ctx_status` tracks empty, queued, and decode-done status. `struct vdec_msg_queue_ctx` models one hardware queue. `struct vdec_lat_buf` carries per-frame LAT output, V4L2 timestamp/request metadata, codec-private data, list nodes, and the core callback. `struct vdec_msg_queue` owns the buffer pool, WDMA/UBE pointers, work item, counts, flush sentinel, waitqueue, and decoder context pointer.

Control flow: callers initialize the queue once, dequeue available LAT buffers from `lat_ctx`, enqueue completed LAT buffers to `core_ctx`, and use read/write pointer update functions to synchronize UBE consumption. Core work returns buffers to `lat_ctx` after callback completion. Deinit releases all queue resources.

State and persistence behavior: all state is per decoder context and persists across frames. The `src_buf_req` media request and `ts_info` timestamp snapshot are stored in `vdec_lat_buf` so core completion can preserve userspace buffer metadata even though decode is split across hardware stages.

Dependencies and integration points: depends on Linux lists, waitqueues, spinlocks, VB2 V4L2 buffers, MediaTek decoder memory structs, and codec-specific callbacks. It is shared by stateless LAT backends such as VP9 and AV1.

Risks: the fixed three-buffer pool constrains throughput and is assumed by flush logic. `private_data` is untyped, so caller and callback must agree on size and layout. List heads for LAT/core are embedded in the same buffer, so a buffer must never be enqueued to both contexts simultaneously. Media requests stored in `src_buf_req` must remain valid until core completion.

Test signals: static checks for correct private size at queue initialization; runtime tests for list/counter balance under decode, EAGAIN, errors, and flush; V4L2 request API tests verifying metadata propagation.
