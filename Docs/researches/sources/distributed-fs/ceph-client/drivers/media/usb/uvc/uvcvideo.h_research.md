# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvcvideo.h

## Purpose
`uvcvideo.h` is the internal header for the UVC kernel driver. It defines driver constants, quirk bits, core device/stream/entity/control/buffer structures, debug helpers, and internal function prototypes shared across UVC source files.

## Important APIs, types, and functions
Key types are `struct uvc_device`, `struct uvc_streaming`, `struct uvc_video_chain`, `struct uvc_entity`, `struct uvc_control`, `struct uvc_control_mapping`, `struct uvc_format`, `struct uvc_frame`, `struct uvc_video_queue`, `struct uvc_buffer`, `struct uvc_urb`, `struct uvc_status`, and statistics/clock structs. Macros classify entities (`UVC_ENTITY_IS_*`), define transfer sizing (`UVC_URBS`, `UVC_MAX_PACKETS`), expose quirk flags, and implement debug logging (`uvc_dbg`, `uvc_warn_once`). It declares the V4L2 operation tables, video functions, status functions, control functions, queue functions, media-controller hooks, PM helpers, metadata registration, debugfs support, and utility helpers.

## Control flow
The header does not execute control flow directly, but it shapes module interactions. `uvc_device` owns the global USB/V4L2/media state and lists of streams/chains/entities. `uvc_streaming` owns a stream's negotiated parameters, queue, URBs, decode callback, metadata queue, bulk accumulator, sequence/FID tracking, statistics, and timestamp clock. `uvc_video_chain` groups entities and control priority/mutex state for V4L2-facing file handles. Function prototypes define the flow from probe/registration through V4L2 ioctls, queue streaming, USB transfer, status events, controls, suspend/resume, and cleanup.

## State and persistence behavior
All structures are runtime kernel objects. Important state boundaries include device lifetime (`uvc_device`), streaming-interface lifetime (`uvc_streaming`), open-file lifetime (`uvc_fh`), queued buffer lifetime (`uvc_buffer`), and URB lifetime (`uvc_urb`). Synchronization fields include `status_lock`, `ctrl_mutex`, queue mutex/spinlock, clock spinlock, krefs, atomics, and work structs. There is no persistent storage; descriptor-derived data and dynamic mappings live until cleanup.

## Dependencies and integration points
The header binds UVC code to Linux USB, input, media controller, V4L2 device/event/fh/subdev APIs, and videobuf2. It includes public UVC and videodev2 headers while keeping internal declarations private to the driver. It also provides the interface between UVC-specific code and generic V4L2 core files through operation tables and ioctl callbacks.

## Risks and edge cases
Because this header defines shared structure layouts, small changes can have wide blast radius across controls, video, queueing, status, and registration code. Bitfields and flags such as buffer state, `frozen`, `flush_status`, and quirks must remain consistent with locking expectations. The `uvc_status` and related structs are packed to match USB payloads; alignment or size changes would break parsing. Function prototype changes require coordinated updates across the driver.

## Test signals
Any change should trigger broad UVC build coverage across configurations: media controller on/off, input evdev on/off, metadata, compat, and multiple architectures. Runtime tests should cover open/close, streaming, controls, status events, suspend/resume, metadata, and disconnect because this header connects all those paths.
