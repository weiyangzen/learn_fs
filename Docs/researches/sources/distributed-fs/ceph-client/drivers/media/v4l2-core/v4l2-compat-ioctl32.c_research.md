# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-compat-ioctl32.c

## Purpose
This file implements the V4L2 compat32 ioctl bridge: it lets 32-bit userspace applications use V4L2 devices on a 64-bit kernel by translating ABI structures whose layout differs because of pointer size, timestamp layout, or architecture-specific alignment. It is used as the `.compat_ioctl` implementation from `v4l2-dev.c` and forwards standard V4L2 ioctls into the normal unlocked ioctl path after translating arguments.

## Important APIs, types, and functions
The file defines 32-bit mirror structs for V4L2 ABI structures with embedded pointers or alignment-sensitive fields: `v4l2_window32`, `v4l2_format32`, `v4l2_create_buffers32`, `v4l2_standard32`, `v4l2_plane32`, `v4l2_buffer32`, optional `v4l2_buffer32_time32`, `v4l2_framebuffer32`, `v4l2_input32`, `v4l2_ext_controls32`, `v4l2_ext_control32`, optional `v4l2_event32`, optional `v4l2_event32_time32`, and `v4l2_edid32`.

Core conversion helpers are `get_v4l2_*32()` for copying and expanding user-provided 32-bit structures into native kernel ABI structures, and `put_v4l2_*32()` for copying native results back to 32-bit layout. `v4l2_compat_translate_cmd()` maps compat ioctl command numbers such as `VIDIOC_G_FMT32`, `VIDIOC_QBUF32`, and `VIDIOC_G_EXT_CTRLS32` to their native commands. `v4l2_compat_get_user()` and `v4l2_compat_put_user()` dispatch the per-ioctl fixed-argument conversions. `v4l2_compat_get_array_args()` and `v4l2_compat_put_array_args()` handle nested arrays such as multi-planar buffers and extended controls. `v4l2_compat_ioctl32()` is the exported entry point.

## Control flow
For a compat V4L2 ioctl, `v4l2_compat_ioctl32()` first checks that an unlocked ioctl implementation exists and that the `video_device` is still registered. For standard V4L2 ioctl numbers below `BASE_VIDIOC_PRIVATE`, it forwards to `file->f_op->unlocked_ioctl(file, cmd, compat_ptr(arg))`; private ioctls are delegated to the driver's `vdev->fops->compat_ioctl32` if available. Standard ioctl dispatch then uses the conversion callbacks in this file through the V4L2 ioctl layer.

The fixed-argument conversion path is command-driven. Format ioctls copy `type` first, then switch by `V4L2_BUF_TYPE_*` to copy only the union arm that applies. Buffer ioctls convert memory-specific union fields: MMAP/OVERLAY preserve offsets, USERPTR uses `compat_ptr()`, DMABUF preserves file descriptors, and multi-planar buffers preserve a compat pointer to the plane array for later array conversion. Extended controls copy the outer array descriptor and then convert each `struct v4l2_ext_control32`; pointer payload controls are detected via `ctrl_is_pointer()` so the nested payload pointer is not confused with scalar `value64`.

## State and persistence behavior
This file does not own long-lived device state. It is a transient ABI adapter that reads from and writes to userspace buffers and fills native temporary ioctl argument structures. The only persistent effects are the effects of the native ioctl it forwards to. Conversion routines intentionally zero native or compat structures before filling selected fields to avoid leaking uninitialized padding back to userspace. Time32 support and x86_64 event alignment support are compile-time conditional.

## Dependencies and integration points
It depends on `linux/compat.h`, `linux/videodev2.h`, `media/v4l2-dev.h`, `media/v4l2-fh.h`, `media/v4l2-ctrls.h`, and `media/v4l2-ioctl.h`. `ctrl_is_pointer()` integrates with `video_devdata()`, `file_to_v4l2_fh()`, control handlers, `v4l2_ctrl_find()`, and optionally the driver's `vidioc_query_ext_ctrl` operation. The exported `v4l2_compat_ioctl32()` is wired into the global V4L2 file operations in `v4l2-dev.c` under `CONFIG_COMPAT`.

## Risks
The major risk is ABI drift: every layout-sensitive userspace structure and ioctl command must remain in sync with `videodev2.h`. Multi-planar buffer conversion trusts the validated plane count passed through the native buffer structure and must keep array-size limits aligned with the caller. Extended control conversion is subtle because pointer controls are layout-compatible except for the payload pointer; changing payload semantics or `V4L2_CTRL_FLAG_HAS_PAYLOAD` handling can corrupt scalar values or leak stale pointers. Time32 and x86_64-specific layouts need architecture coverage. Any missed zeroing of padding or reserved fields could leak kernel stack contents.

## Test signals
Useful signals are compat ioctl tests from 32-bit userspace on a 64-bit kernel: format get/set/try across all buffer types, buffer query/qbuf/dqbuf/prepare for MMAP, USERPTR, DMABUF, and multi-planar modes, extended controls with scalar, string, compound, and dynamic-array payloads, EDID get/set, event dequeue under x86_64 and time32 configurations, and private ioctl fallback. Fuzzing invalid `type`, `memory`, `count`, `size`, and nested pointer values should confirm `-EINVAL`, `-EFAULT`, or `-ENOSPC` behavior without native ioctl side effects.
