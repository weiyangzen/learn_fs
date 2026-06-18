# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_v4l2.c

## Purpose

`uvc_v4l2.c` exposes the UVC gadget function as a V4L2 video-output device. It lets userspace enumerate configured UVC formats/frames, choose stream parameters, queue video buffers, receive UVC control events, and send control responses to the USB host.

## Important APIs, Types, and Functions

The exported tables are `uvc_v4l2_ioctl_ops` and `uvc_v4l2_fops`. Format helpers include `to_uvc_format()`, `uvc_v4l2_get_bytesperline()`, `uvc_get_frame_size()`, `find_format_by_index()`, `find_frame_by_index()`, `find_format_by_pix()`, and `find_closest_frame_by_size()`. Request handling uses `uvc_send_response()` for `UVCIOC_SEND_RESPONSE`.

Core ioctl handlers cover querycap, get/try/set format, get/set frame interval, enumerate formats/sizes/intervals, REQBUFS/QUERYBUF/QBUF/DQBUF, STREAMON/STREAMOFF, event subscribe/unsubscribe, and default UVC response ioctl. File operations cover open, release, mmap, poll, and no-MMU unmapped-area lookup.

## Control Flow

Open allocates a `struct uvc_file_handle`, initializes V4L2 file-handle state, and points the handle at `uvc->video`. Userspace subscribes to UVC events; the first `UVC_EVENT_SETUP` subscriber becomes the active UVC application handle and triggers `uvc_function_connect()`. Host setup events are later answered by `UVCIOC_SEND_RESPONSE`, which queues data on EP0 or stalls for negative lengths.

Format ioctls derive the supported V4L2 format list from configfs-created UVC streaming headers and formats. `S_FMT` first calls `TRY_FMT`, then updates `video->fcc`, dimensions, bpp, and `imagesize`. Queue ioctls delegate to `uvc_queue.c`; QBUF wakes the video pump if the USB side is already streaming. STREAMON enables the USB video engine, continues delayed UVC setup, and marks state streaming. STREAMOFF disables video, returns to connected state, and continues setup with failure status if needed.

## State and Persistence Behavior

Persistent-in-memory state lives in `struct uvc_video`: selected pixel format, width, height, bpp, image size, and frame interval. Per-open state lives in `struct uvc_file_handle`, especially `is_uvc_app_handle`, which controls cleanup responsibility. `uvc->func_connected` gates exclusive SETUP-event ownership. No state is stored outside kernel memory.

## Dependencies and Integration Points

This file integrates UVC configfs descriptor state, V4L2 core, videobuf2 queue helpers, libcomposite EP0 setup continuation, and UVC event definitions from `linux/usb/g_uvc.h`. It also drives `uvc_video.c` through `uvcg_video_enable()` and `uvcg_video_disable()`.

## Risks and Test Signals

Risks include format selection mismatches between configfs UVC descriptors and V4L2 pixel formats, missing locking around video format fields, exclusive event-owner handling, and cleanup on release/unsubscribe while streaming. Tests should enumerate all configured formats, set exact and closest frame sizes, reject invalid sizeimage for uncompressed formats, stream buffers through QBUF/DQBUF, send UVC control responses, enforce one setup-event owner, and release the active UVC application handle while streaming.
