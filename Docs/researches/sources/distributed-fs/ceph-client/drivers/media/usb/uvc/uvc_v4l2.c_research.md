# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_v4l2.c

## Purpose
`uvc_v4l2.c` is the UVC driver's V4L2 userspace API layer. It implements file operations and ioctl callbacks for format negotiation, frame interval selection, input selection, controls, event subscription, dynamic extension-unit control mapping, and runtime PM wrapping for hardware-touching operations.

## Important APIs, types, and functions
The exported operation tables are `uvc_ioctl_ops` and `uvc_fops`. Runtime PM helpers `uvc_pm_get()` and `uvc_pm_put()` pair USB autosuspend references with status endpoint references. Format negotiation is centered on `uvc_v4l2_try_format()`, `uvc_ioctl_g_fmt()`, `uvc_ioctl_s_fmt()`, and `uvc_ioctl_try_fmt()`. Frame interval handling uses `uvc_ioctl_g_parm()`, `uvc_ioctl_s_parm()`, `uvc_try_frame_interval()`, and `v4l2_fraction_to_interval()`. Control ioctls use `uvc_ioctl_g_ext_ctrls()`, `uvc_ioctl_s_try_ext_ctrls()`, `uvc_ctrl_begin()`, `uvc_ctrl_get()`, `uvc_ctrl_set()`, `uvc_ctrl_commit()`, and rollback. UVC-specific extension ioctls are handled by `uvc_ioctl_xu_ctrl_map()`, `uvc_control_add_xu_mapping()`, and `uvc_ioctl_default()`.

## Control flow
Opening a node allocates `struct uvc_fh`, initializes a V4L2 file handle, and attaches the current chain and stream. Release cleans pending controls and delegates buffer cleanup to vb2. `S_FMT` calls the shared try-format helper, refuses changes while the vb2 queue is busy, then commits `stream->ctrl`, `cur_format`, and `cur_frame`. `S_PARM` refuses active streaming, finds the closest supported interval among matching-size frames, probes the device, and updates current frame/stream control state. Hardware-dependent ioctls are routed through `uvc_v4l2_unlocked_ioctl()`, which takes runtime PM and status references, calls `video_ioctl2()`, and releases them afterward.

## State and persistence behavior
Per-open state lives in `struct uvc_fh` and includes the V4L2 file handle, chain, stream, and pending async control count. Per-stream negotiated state is in memory in `struct uvc_streaming`: `ctrl`, `cur_format`, `cur_frame`, and queue state. Dynamic XU mappings alter in-kernel control mapping state through `uvc_ctrl_add_mapping()` but are not persisted to disk. Runtime PM references are transient and scoped to ioctl execution.

## Dependencies and integration points
The file sits between V4L2 core (`video_ioctl2`, v4l2 events, v4l2 controls), videobuf2 file/ioctl helpers, USB runtime PM, and the UVC control/video implementation. Format probing calls `uvc_probe_video()` from `uvc_video.c`; control requests call into UVC control code; selector-unit input switching uses `uvc_query_ctrl()`. It also supplies compat ioctl translation for 32-bit userspace when `CONFIG_COMPAT` is enabled.

## Risks and edge cases
Format selection trusts device probe responses but falls back when devices return unknown format/frame indexes. `uvc_try_frame_interval()` assumes descriptor intervals are ordered well enough for distance comparison. XU mapping copies user-provided menu values/names and therefore must bound counts and clean temporary allocations on all exits. Runtime PM wrapping must include every ioctl that touches the device; missing one can access suspended hardware, while unnecessary wrapping can wake devices. Busy checks around format/input changes prevent stream-time reconfiguration bugs.

## Test signals
Exercise `VIDIOC_ENUM_FMT`, `TRY_FMT`, `S_FMT`, `G/S_PARM`, stream-on busy rejection, selector input get/set, control get/set/try, XU mapping/query, 32-bit compat ioctls, and event subscription. Hardware tests should include devices with invalid probe responses, multiple frame intervals at the same size, extension controls with menus, and autosuspend enabled.
