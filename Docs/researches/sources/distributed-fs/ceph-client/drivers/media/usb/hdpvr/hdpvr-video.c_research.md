<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-video.c

Purpose: V4L2 userspace interface and MPEG transport streaming engine for HD-PVR. It exposes a read/poll video capture node, encoder start/stop commands, input/audio/timing ioctls, and V4L2 controls for MPEG and picture settings.

Important APIs/types/functions: `struct hdpvr_fh` tracks per-file legacy DV-timing mode. Buffer management uses `hdpvr_alloc_buffers()`, `hdpvr_free_buffers()`, `hdpvr_cancel_queue()`, `hdpvr_submit_buffers()`, and `hdpvr_transmit_buffers()`. Streaming is controlled by `hdpvr_start_streaming()` and `hdpvr_stop_streaming()`. User I/O is in `hdpvr_read()` and `hdpvr_poll()`. V4L2 ioctls include standard/DV timing/input/audio/MPEG format/encoder command handlers. `hdpvr_register_videodev()` registers controls and the `video_device`.

Control flow: read or poll on an idle device starts streaming after validating `get_video_info()`, sends firmware start requests, sets status streaming, schedules the worker, and records the owning filehandle. The worker submits all available coherent bulk buffers as URBs and sleeps until a buffer returns to the free list. URB completion marks buffers ready and wakes readers. `hdpvr_read()` copies ready URB payloads to userspace, recycles fully consumed buffers to the free list, and restarts streaming after a one-second data timeout. Stop sends the firmware stop request, wakes/flushed the worker, kills queued URBs, drains residual device data with bulk reads, and returns status to idle.

State and persistence: stream state persists in `dev->status`, `owner`, free/in-progress lists, per-buffer status/position/URB, waitqueues, and cached width/height/std/DV timing/options/control values. Hardware encoder and low-pass/input/audio/bitrate settings persist in firmware until changed. There is no on-disk persistence.

Dependencies and integration: uses USB bulk URBs, V4L2 file/ioctl/control/event helpers, DV timing helpers, `copy_to_user()`, workqueues, and control helpers from `hdpvr-control.c`. It integrates with `hdpvr-core.c` probe and release lifecycle.

Risks: this driver is read-based, not vb2, so queue ownership and waits are manually implemented. `hdpvr_get_next_buffer()` returns a list entry after releasing `io_mutex`, so status/list transitions rely on the broader single-reader/owner discipline. `hdpvr_read()` restarts streaming after timeout without holding `io_mutex` for the second `hdpvr_start_streaming()` call, which contrasts with the function comment. `hdpvr_device_release()` unregisters I2C even though disconnect/probe failure paths may also do so. Legacy-mode behavior intentionally changes `G_FMT` semantics per filehandle.

Test signals: `v4l2-compliance` for read-only capture; `v4l2-ctl --query-dv-timings`, `--set-dv-bt-timings`, std/input/audio enumeration; read MPEG data from component and composite/S-video sources; encoder start/stop commands and owner exclusion; nonblocking read/poll; timeout recovery; disconnect during active read; control changes only while idle where required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-video.c -->
