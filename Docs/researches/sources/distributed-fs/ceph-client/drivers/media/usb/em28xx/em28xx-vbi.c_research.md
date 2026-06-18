# sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-vbi.c

Purpose: implements raw VBI videobuf2 queue operations for em28xx analog capture.

Important APIs/types/functions: `vbi_queue_setup()` computes VBI buffer size as `vbi_width * vbi_height * 2` and enforces at least two buffers. `vbi_buffer_prepare()` validates plane size and sets payload. `vbi_buffer_queue()` maps the vmalloc plane, stores buffer length, and enqueues the buffer on `dev->vbiq.active` under `dev->slock`. `em28xx_vbi_qops` wires these callbacks to the shared analog start/stop functions.

Control flow: the V4L2 init path in `em28xx-video.c` initializes `vb_vbiq` with these ops and registers a VBI video device when `em28xx_vbi_supported()` is true. Userspace queues VBI buffers; queued buffers are consumed by the analog URB parser in `em28xx-video.c` when VBI headers/data arrive. Stream start/stop is delegated back to the analog engine so VBI and video share URBs and decoder stream state.

State and persistence: modifies per-buffer `mem`/`length` and the active VBI DMA queue. Buffer completion and field placement are handled in `em28xx-video.c`, while dimensions live in `dev->v4l2`.

Dependencies and integration points: depends on videobuf2, `struct em28xx`, `struct em28xx_buffer`, the shared spinlock, and the V4L header contract. It integrates with V4L2 raw VBI ioctls implemented in `em28xx-video.c`.

Risks: the VBI buffer size depends on correct norm-derived dimensions; stale dimensions can reject valid buffers or overrun payload assumptions. Queue operations do not independently check disconnect state. VBI and video sharing `streaming_users` means imbalance in start/stop can leave URBs running or stop them early. Test signals include `VIDIOC_G_FMT`/`REQBUFS`/streaming on VBI devices for NTSC and PAL, concurrent video+VBI streaming, buffer underrun/short plane rejection, and streamoff returning queued buffers with expected states.
