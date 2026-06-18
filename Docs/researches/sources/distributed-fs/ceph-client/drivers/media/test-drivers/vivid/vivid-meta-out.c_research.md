# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-meta-out.c

Purpose: implements Vivid metadata output for webcam mode. Metadata output buffers carry image-control values that are applied to the video test generator controls when output buffers are consumed.

Important APIs and functions: exported symbols are `vivid_meta_out_qops`, `vidioc_enum_fmt_meta_out`, `vidioc_g_fmt_meta_out`, and `vivid_meta_out_process`. Internal vb2 callbacks mirror meta capture: queue setup, prepare, queue, start/stop streaming, and request completion.

Control flow: queue setup accepts one plane sized for `struct vivid_meta_out_buf` in webcam mode. Buffer prepare validates size and supports error injection. Queued buffers enter `meta_out_active`; streaming joins the shared output kthread through `vivid_start_generating_vid_out`. Output ticks run request setup/complete, call `vivid_meta_out_process`, assign sequence/timestamp, and complete the buffer.

State and persistence: metadata output persists by changing V4L2 controls on `dev->brightness`, `dev->contrast`, `dev->saturation`, and `dev->hue`. The buffer itself is transient; the control values remain until changed again.

Dependencies and integration points: depends on V4L2 metadata output format `V4L2_META_FMT_VIVID`, videobuf2, Vivid core, shared output kthread, and user video controls created by `vivid-ctrls.c`.

Risks: metadata output assumes the image controls exist and are valid for the current device mode. Applying controls from queued metadata can race conceptually with normal userspace control changes, though V4L2 control locking handles serialization. The declared `vidioc_s_fmt_meta_out` prototype in the header is not implemented in this file.

Test signals: webcam-mode meta output format enumeration, streaming a metadata buffer and observing video control values, request completion tests, error injection, and build warnings for unused/missing prototypes are relevant.
