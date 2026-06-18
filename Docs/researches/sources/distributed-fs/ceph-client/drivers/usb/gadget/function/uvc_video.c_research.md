# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_video.c

## Purpose

`uvc_video.c` moves queued V4L2 video buffers into USB requests for the UVC gadget streaming endpoint. It encodes UVC payload headers, supports bulk and isochronous transfer modes, manages USB request pools, and coordinates request completion with videobuf2 buffer completion.

## Important APIs, Types, and Functions

Public functions are `uvcg_video_init()`, `uvcg_video_enable()`, and `uvcg_video_disable()`. Encoding functions are `uvc_video_encode_header()`, `uvc_video_encode_data()`, `uvc_video_encode_bulk()`, `uvc_video_encode_isoc()`, and `uvc_video_encode_isoc_sg()`. Request management uses `uvc_video_alloc_requests()`, `uvc_video_free_requests()`, `uvc_video_free_request()`, `uvc_video_prep_requests()`, `uvcg_video_usb_req_queue()`, `uvcg_video_ep_queue()`, and completion callback `uvc_video_complete()`.

Asynchronous execution is split between workqueue `uvcg_video_pump()` and kthread work `uvcg_video_hw_submit()`. Tracepoints `trace_uvcg_video_queue()` and `trace_uvcg_video_complete()` instrument queue depth.

## Control Flow

`uvcg_video_init()` initializes request lists, locks, work items, a high-priority workqueue, a FIFO kthread worker, default YUYV format state, and the vb2 queue. `uvcg_video_enable()` starts vb2 streaming, allocates USB requests sized for bulk or isochronous bandwidth, selects the encoder, resets counters, queues initial hardware submit work, and wakes the pump.

The pump repeatedly takes a free USB request under `req_lock`, takes the first queued video buffer under queue `irqlock`, encodes header and payload, and either queues directly to a bulk endpoint or places isochronous requests on `req_ready`. Completions decrement the queued count, handle USB status errors, complete any `last_buf`, recycle the request to `req_free`, wake the pump, and schedule hardware submit. The hardware-submit worker feeds isochronous endpoints from `req_ready` and may send bounded zero-length requests to keep the endpoint moving.

## State and Persistence Behavior

Streaming state includes `is_enabled`, `ureqs`, `req_free`, `req_ready`, `req_lock`, queued request count, interrupt-throttling counter, payload size, FID toggle, request sizing, and selected encode callback. Buffer progress uses `queue.buf_used`, SG cursors, and `ureq->last_buf`. State is runtime only and reset on every enable/disable cycle.

## Dependencies and Integration Points

The file depends on USB gadget endpoints/requests, UVC payload flags, unaligned endian helpers, V4L2 timestamps, the UVC queue API, and UVC tracepoints. It is driven by V4L2 STREAMON/STREAMOFF and QBUF paths and feeds the gadget endpoint selected by the UVC function bind path.

## Risks and Test Signals

Risks are concurrency-heavy: request free/ready/owned transitions cross completion context, workqueue context, and kthread context; disable must return in-flight buffers without racing completions; isochronous SG encoding mutates SG cursors under queue lock; and bulk EOF/zero-packet behavior depends on `payload_size` and `max_payload_size`. The pump tail path also re-adds `req`, so null or stale request handling should be watched. Tests should cover bulk and isochronous endpoints, SG and vmalloc memory, short/missed transfers (`-EXDEV`), disconnect (`-ESHUTDOWN`), repeated stream enable/disable, zero-length isochronous request limits, frame timestamp headers, EOF/FID toggling, and release while requests are in flight.
