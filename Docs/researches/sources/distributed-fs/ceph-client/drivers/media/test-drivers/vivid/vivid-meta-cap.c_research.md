# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-meta-cap.c

Purpose: implements UVC-style metadata capture for Vivid webcam mode. It exposes meta capture format operations, videobuf2 queue operations, and a buffer filler that emits timing metadata tied to the video capture clock.

Important APIs and functions: exported symbols are `vivid_meta_cap_qops`, `vidioc_enum_fmt_meta_cap`, `vidioc_g_fmt_meta_cap`, and `vivid_meta_cap_fillbuff`. Internal vb2 callbacks include `meta_cap_queue_setup`, `meta_cap_buf_prepare`, `meta_cap_buf_queue`, `meta_cap_start_streaming`, `meta_cap_stop_streaming`, and `meta_cap_buf_request_complete`.

Control flow: queue setup validates webcam mode and requires a single plane sized for `struct vivid_uvc_meta_buf`. Buffer prepare supports error injection, validates plane size, and sets payload. Queued buffers are appended to `meta_cap_active`. Streaming starts by joining the shared capture kthread with `meta_cap_streaming`; stop leaves through `vivid_stop_generating_vid_cap`. During capture ticks, `vivid_meta_cap_fillbuff` writes a UVC metadata header, optional PTS from start-of-exposure time, optional SCR from EOF time, SOF counters, flags, sequence, and debug output.

State and persistence: state is volatile in `struct vivid_dev` and queued buffers. `meta_pts` and `meta_scr` controls decide whether PTS/SCR fields are generated. Sequence comes from `meta_cap_seq_count`, divided for alternate-field capture.

Dependencies and integration points: depends on V4L2 meta formats, videobuf2, Linux UVC stream flag definitions, shared capture kthread, and Vivid core state. It is synchronized with video capture timing through the shared capture thread and `cap_frame_eof_offset`.

Risks: several multi-byte metadata values are assigned through single-byte lvalues such as `meta->buf[0] = div_u64(...)`, so only the low byte is explicitly set despite debug casts reading 32-bit fields; this is intentional-looking test data but could mislead consumers expecting full UVC values. Meta capture is rejected outside webcam mode. Timestamp is generated independently from the buffer timestamp.

Test signals: `v4l2-compliance` meta capture, webcam-mode format enumeration, buffer-size validation, PTS/SCR control toggles, concurrent video+meta capture timestamps, and UVC metadata parser checks are useful.
