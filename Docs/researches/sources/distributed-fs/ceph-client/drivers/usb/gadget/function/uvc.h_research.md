## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc.h

Purpose: declares internal runtime structures, constants, tracing helpers, and function entry points for the USB Video Class gadget driver.

Important APIs and types:
- Trace flags (`UVC_TRACE_*`) and `uvc_trace()` gate debug logging via `uvc_gadget_trace_param`; `uvcg_dbg/info/warn/err` log through the gadget device.
- Constants define request size/event limits, UVC request header length, interrupt/zero counters, and minimum streaming buffers.
- `struct uvc_request` wraps a USB request, request buffer, owning `uvc_video`, scatterlist table, UVC payload header, last video buffer, and list linkage.
- `struct uvc_video` owns the streaming endpoint, pump work/workqueues, kernel worker submission, queued counter, current frame parameters protected by `mutex`, request counts/sizes/lists, request lock, encoder callback, payload sizing, video queue, and frame ID.
- `enum uvc_state` tracks disconnected, connected, and streaming states.
- `struct uvc_device` combines `video_device`, `v4l2_device`, state, `usb_function`, `uvc_video`, release completion, function connection/unbound locking, descriptor pointers, control/streaming interface numbers, interrupt endpoint/control request/buffer state, and event setup state.
- `struct uvc_file_handle` embeds `v4l2_fh`, points to `uvc_video`, and marks whether a handle is the UVC application handle.
- Helpers convert from `usb_function` or file handles to UVC containers.
- Declares `uvc_function_setup_continue()`, `uvc_function_connect()`, and `uvc_function_disconnect()`.

Control flow and integration:
- Composite bind creates a `uvc_device` and fills descriptor pointers from `f_uvc_opts`.
- V4L2 userspace opens the video node, configures frame parameters, queues buffers, and handles UVC events.
- When the host completes class-specific setup negotiation, `uvc_function_setup_continue()` resumes EP0 control handling.
- USB connect/disconnect transitions use `uvc_function_connect()` / `uvc_function_disconnect()` to notify state and wake waiting userspace.
- Streaming uses `uvc_video` request lists: free requests are encoded from queued V4L2 buffers, moved to ready, submitted to the endpoint, and recycled on completion.

State and persistence:
- Runtime state persists while the UVC function is bound and the video device exists.
- Frame format/size/interval are mutable under `uvc_video.mutex`.
- Request lists and payload counters reset with stream enable/disable.
- `func_unbound` and `func_connected` coordinate teardown and userspace waiters.

Dependencies:
- Linux list/mutex/spinlock/wait APIs, USB composite, V4L2 device/file-handle APIs, videodev2, and `uvc_queue.h`.

Risks:
- Streaming request lists are split across free/ready/all lists with both workqueue and completion contexts; locking mistakes can lose requests.
- UVC setup event length/direction state must match EP0 control continuation or hosts can stall.
- V4L2 buffer availability and USB request availability must be balanced to avoid underruns or deadlocks.
- Descriptor pointers are owned by UVC option/configfs code; lifetime must outlive the bound function.

Test signals:
- Enumerate UVC gadget, open V4L2 node, negotiate probe/commit, stream frames, disconnect/reconnect, and run with dynamic format changes.
- Exercise request pool exhaustion, zero-length/short payload edge cases, and host setup cancellation.
- Use trace flags to confirm descriptor, control, streaming, suspend, and status paths.
