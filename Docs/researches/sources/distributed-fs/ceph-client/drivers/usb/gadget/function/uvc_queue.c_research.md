# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_queue.c

## Purpose

`uvc_queue.c` implements UVC gadget video-buffer management using videobuf2. It translates V4L2 buffer operations into a queue consumed by the USB video pump and provides IRQ-safe access to the current buffer list.

## Important APIs, Types, and Functions

The vb2 callbacks are `uvc_queue_setup()`, `uvc_buffer_prepare()`, and `uvc_buffer_queue()`, collected in `uvc_queue_qops`. Public helpers include `uvcg_queue_init()`, `uvcg_free_buffers()`, `uvcg_alloc_buffers()`, `uvcg_query_buffer()`, `uvcg_queue_buffer()`, `uvcg_dequeue_buffer()`, `uvcg_queue_poll()`, `uvcg_queue_mmap()`, `uvcg_queue_cancel()`, `uvcg_queue_enable()`, `uvcg_complete_buffer()`, and `uvcg_queue_head()`.

## Control Flow

`uvcg_queue_init()` sets up a single-plane V4L2 output queue supporting MMAP, USERPTR, and DMABUF. It uses scatter-gather memory ops when the gadget reports SG support and falls back to vmalloc otherwise. `uvcg_alloc_buffers()` calls `vb2_reqbufs()` and retries in non-SG mode if SG allocation fails.

When userspace queues a buffer, `uvc_buffer_prepare()` validates payload size, records either SG or virtual-memory backing, initializes byte counters, and computes per-request payload sizing for isochronous transfer when `reqs_per_frame` is known. `uvc_buffer_queue()` appends the prepared buffer to `irqqueue` under `irqlock`, or immediately returns it with error if the queue has been disconnected. The video path calls `uvcg_queue_head()` to fetch the first active buffer and `uvcg_complete_buffer()` to return it to vb2 when a frame has been transmitted.

## State and Persistence Behavior

Queue state is in `struct uvc_video_queue`: vb2 queue, `flags`, sequence number, current `buf_used`, SG mode flag, `irqlock`, and IRQ-side buffer list. Per-buffer state is in `struct uvc_buffer`: state enum, backing pointer/SG cursor, current offset, length, bytes used, and request payload size. State is transient and reset across stream enable/disable.

## Dependencies and Integration Points

The file depends on videobuf2 core, V4L2 buffer types, `videobuf2-dma-sg`, `videobuf2-vmalloc`, USB composite gadget capabilities, and UVC video state from `struct uvc_video`. It is called by `uvc_v4l2.c` for ioctl operations and by `uvc_video.c` for streaming completion and cancellation.

## Risks and Test Signals

Important risks are lock ordering between vb2 mutexes and `irqlock`, stale buffers on disconnect, incomplete-frame handling through `UVC_QUEUE_DROP_INCOMPLETE`, SG fallback behavior, and correctness of `req_payload_size` for isochronous transfers. Tests should cover REQBUFS in SG and vmalloc modes, QBUF after disconnect, streamon/streamoff cycles, nonblocking DQBUF, mmap/poll, dropped incomplete frames, and buffer sequence/timestamp propagation.
