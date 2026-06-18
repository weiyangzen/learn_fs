# sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-v4l.h

Purpose: exposes the small cross-file V4L/VBI interface between `em28xx-video.c` and `em28xx-vbi.c`.

Important APIs/types/functions: declares `em28xx_start_analog_streaming()`, `em28xx_stop_vbi_streaming()`, and `extern const struct vb2_ops em28xx_vbi_qops`. These let the VBI queue reuse the analog streaming engine while keeping VBI queue setup and buffering in `em28xx-vbi.c`.

Control flow: `em28xx-vbi.c` assigns `em28xx_start_analog_streaming` and `em28xx_stop_vbi_streaming` into its `vb2_ops`; `em28xx-video.c` owns the implementations and initializes the VBI queue with `em28xx_vbi_qops`.

State and persistence: no state is stored in this header. The functions operate on `vb2_queue` driver-private `struct em28xx` state at runtime.

Dependencies and integration points: relies on videobuf2 types being visible through included implementation files. It is the compile-time contract between analog video and VBI support.

Risks: because the header is minimal, signature drift between video and VBI code would break compilation. Behavioral risk is in the shared streaming refcount/resource logic: VBI and video queues both affect `streaming_users` and USB URBs. Test signals are successful build, simultaneous/sequential video and VBI streamon/streamoff, and VBI device registration only when supported.
