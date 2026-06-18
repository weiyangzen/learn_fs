# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_queue.c

Purpose: implements shared videobuf2 queue management for UVC video and metadata buffers. It initializes queues, validates buffer sizes, manages the IRQ-side buffer list consumed by streaming URB callbacks, handles stream start/stop, disconnect cancellation, and delayed buffer completion through krefs.

Important APIs and functions: public functions are `uvc_queue_init`, `uvc_queue_cancel`, `uvc_queue_get_current_buffer`, `uvc_queue_next_buffer`, and `uvc_queue_buffer_release`. Core vb2 callbacks are `uvc_queue_setup`, `uvc_buffer_prepare`, `uvc_buffer_queue`, `uvc_buffer_finish`, `uvc_start_streaming_video`, `uvc_stop_streaming_video`, and `uvc_stop_streaming_meta`. Internal helpers return or requeue buffers and complete them when references drop.

Control flow: queue initialization sets type, io modes, buffer struct size, vmalloc memory ops, timestamp flags, and selects video or metadata vb2 ops. Buffer preparation checks output payload bounds, rejects disconnected queues, records memory pointer/length, and initializes bytes-used state. Queued buffers are added to `irqqueue` under `irqlock` unless disconnected. Video stream start gets a runtime PM reference, clears `buf_used`, and starts USB video streaming; failure returns queued buffers. Stop halts USB streaming, drops PM, and returns queued buffers as errors. Metadata queues have no start callback and rely on video streaming. Streaming code obtains the current buffer, advances with `uvc_queue_next_buffer`, and releases references when async work completes.

State and persistence: `struct uvc_video_queue` owns a vb2 queue, mutex, IRQ spinlock, `irqqueue`, flags such as `UVC_QUEUE_DISCONNECTED`, stream pointer, and per-stream buffer-use accounting. `struct uvc_buffer` stores state, error flag, memory pointer, length, bytes used, list node, and kref. All state is runtime-only.

Dependencies and integration points: depends on videobuf2-v4l2/vmalloc, UVC streaming functions from `uvc_video.c`, runtime PM helpers, global `uvc_no_drop_param`, and V4L2 timestamp clock update. It is used by video nodes from `uvc_driver.c` and metadata nodes from `uvc_metadata.c`.

Risks: disconnect handling must set `UVC_QUEUE_DISCONNECTED` under the IRQ lock to avoid races with QBUF and blocking dequeue. Buffer completion can requeue erroneous buffers when `nodrop` is disabled, changing userspace-visible frame loss behavior. Metadata queues do not start hardware, so userspace can stream metadata without receiving data if video is idle. Buffer lifetime relies on kref pairing between synchronous decode and asynchronous copy paths.

Test signals: run mmap/userptr/dmabuf capture, queue too-small buffers, stream video and metadata together, disconnect while dequeues are pending, inject URB errors with `nodrop` on/off, test output payload bounds if output devices are present, and verify timestamps are updated on completed video buffers.
