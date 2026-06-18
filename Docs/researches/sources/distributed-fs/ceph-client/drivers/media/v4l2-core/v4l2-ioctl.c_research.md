# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-ioctl.c

## Purpose
`v4l2-ioctl.c` is the generic V4L2 ioctl framework for video devices. It translates userspace ioctl calls into driver `struct v4l2_ioctl_ops` callbacks, validates command availability and buffer types, sanitizes user-visible structs, integrates controls/events/priority/media-source handling, supports compat/time32 translation, copies array arguments safely, and emits optional debug traces.

## Important APIs, Types, and Functions
Exported helpers include `v4l2_norm_to_name`, `v4l2_video_std_frame_period`, `v4l2_video_std_construct`, `v4l_video_std_enumstd`, `v4l_printk_ioctl`, `v4l2_translate_cmd`, and `video_ioctl2`. Important internal components are `struct v4l2_ioctl_info`, the `v4l2_ioctls[]` dispatch table, `check_ext_ctrls`, `check_fmt`, `v4l_sanitize_format`, per-command wrappers such as `v4l_querycap`, `v4l_enum_fmt`, `v4l_g_fmt`, `v4l_s_fmt`, `v4l_try_fmt`, buffer/streaming wrappers, control wrappers, crop/selection shims, debug register handlers, event wrappers, `__video_do_ioctl`, `check_array_args`, `video_get_user`, `video_put_user`, and `video_usercopy`.

## Control Flow
The top-level entry is `video_ioctl2`, which calls `video_usercopy` with `__video_do_ioctl`. `video_usercopy` translates the command for compat/time32, allocates a stack or heap argument buffer, copies in only the needed input bytes, zeros uncopied fields, detects secondary user arrays such as multiplanar planes, EDID bytes, extended controls, and subdev routes, copies those arrays to kernel memory, invokes the ioctl function, traces QBUF/DQBUF on success, copies arrays and the main struct back when needed, and frees temporary buffers.

`__video_do_ioctl` obtains `video_device`, ioctl ops, file handle, optional request queue lock for STREAMON/STREAMOFF/REQBUFS, and the correct serialization lock. Queue ioctls prefer mem2mem queue locks or vb2 queue locks; otherwise the video-device lock is used. It rejects unregistered devices, checks whether a known command is enabled in `valid_ioctls` unless a file-handle control handler can satisfy a control ioctl, enforces priority for flagged commands, calls the dispatch-table wrapper or driver default handler, and prints debug output if requested.

Per-command wrappers normalize V4L2 API behavior before calling drivers. Format paths call `check_fmt`, sanitize colorspace/extended pixel-format fields, zero reserved tails, map single vs multiplanar ops according to capabilities, and fill known format descriptions. Buffer paths validate buffer type and expose remove-buffer capabilities. Control paths prefer file-handle or video-device control handlers and fall back to ioctl ops. Selection shims map old crop APIs onto selection targets and handle the inverted-crop quirk. Input/output/frequency/std/tuner wrappers enforce media-controller and device-type rules. Event wrappers use `v4l2_event_dequeue` and driver subscribe/unsubscribe hooks. Advanced debug register handlers require `CAP_SYS_ADMIN` and can target bridge or subdevices.

## State and Persistence Behavior
The framework mutates per-open priority state, request queue serialization, control values, event queues, buffer queues, and driver/device state through callbacks. It maintains no on-disk persistence. The `valid_ioctls` bitmap on `struct video_device` is the command availability state. User-copy paths zero reserved fields and always-copy certain ioctls even on failure, which defines ABI-visible state transfer.

## Dependencies and Integration Points
This file ties together V4L2 devices, file handles, controls, events, videobuf2, mem2mem, media controller request queues, subdevices, compat ioctl support, tracepoints, and the Linux usercopy APIs. It is the primary ABI boundary for userspace tools, camera stacks, codecs, tuners, SDR, VBI, metadata, and touch devices.

## Risks
This is high-blast-radius ABI code. Risks include usercopy size mistakes, array bounds mistakes, compat/time32 translation regressions, incorrect lock selection causing queue deadlocks or races, priority bypass, stale `valid_ioctls`, leaking uninitialized reserved fields, incorrect format sanitization, buffer type confusion, and mismatch between generic shims and driver expectations. Many wrappers deliberately emulate older APIs, so changing them can break legacy userspace.

## Test Signals
Test with v4l2-compliance across video capture/output, mplane, metadata, SDR, VBI, touch, mem2mem, and media-controller devices. Exercise all usercopy array paths, compat ioctls, request queue locking, debug logging, priority checks, control handlers and fallback ops, event dequeue/subscribe/unsubscribe, crop-selection compatibility, pixel format enumeration, EDID always-copy behavior, and negative cases for invalid buffer types, excessive array counts, unregistered devices, and disabled ioctls.
