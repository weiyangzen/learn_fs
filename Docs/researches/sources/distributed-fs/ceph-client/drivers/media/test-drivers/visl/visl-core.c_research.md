# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-core.c

## Purpose
`visl-core.c` is the module and device core for VISL, a virtual stateless V4L2 decoder used to exercise userspace stateless-codec flows without decoder hardware. It registers a platform device/driver pair, creates a V4L2 mem2mem video node, wires the media-controller request callbacks, allocates per-open decoder contexts, and defines the stateless codec control sets that other VISL files consume.

## Important APIs, types, and functions
The file exports module parameters controlling diagnostics and timing: `visl_debug`, `visl_transtime_ms`, `visl_dprintk_frame_start`, `visl_dprintk_nframes`, `keep_bitstream_buffers`, `bitstream_trace_frame_start`, `bitstream_trace_nframes`, and `tpg_verbose`. It defines `visl_fwht_ctrls`, `visl_mpeg2_ctrls`, `visl_vp8_ctrls`, `visl_vp9_ctrls`, `visl_h264_ctrls`, `visl_hevc_ctrls`, and `visl_av1_ctrls` as codec-specific arrays of `struct v4l2_ctrl_config`.

`visl_find_control()`, `visl_find_control_data()`, and `visl_control_num_elems()` are helper APIs used by the decode path to retrieve current request/control payloads from `ctx->hdl`. `visl_init_ctrls()` builds one V4L2 control handler containing the controls required by every coded format in `visl_coded_fmts`.

`visl_open()` allocates `struct visl_ctx`, initializes the V4L2 file handle, control handler, mem2mem context through `visl_queue_init()`, mutexes, and default formats. `visl_release()` tears down TPG data, V4L2 fh/control state, mem2mem context, and the text buffer. `visl_probe()` registers the V4L2 device, mem2mem device, media device, video node, media controller entity, and optional debugfs tree. `visl_remove()` unregisters media and video nodes. `visl_device_release()` is the final release hook for the embedded `video_device`.

## Control flow
Module initialization registers a synthetic platform device and platform driver. Probe allocates a single `struct visl_dev`, registers V4L2/mem2mem/media-controller objects, then registers the video device. Each file open creates an independent decoding context and default queue formats. The mem2mem scheduler calls `visl_device_run()` from `visl-dec.c` through `visl_m2m_ops`. Request validation is delegated to `visl_request_validate()` while request queuing uses `v4l2_m2m_request_queue`.

## State and persistence
Global module parameters persist for the module lifetime and affect all contexts. Device state lives in `struct visl_dev`, while stream format, codec selection, queue sequence counters, controls, and TPG state live per `struct visl_ctx`. No decoded media is persisted; optional bitstream debugfs blobs are retained only when the module parameter requests it.

## Dependencies and integration points
This file depends on V4L2 device/ioctl/control APIs, V4L2 mem2mem, media-controller request APIs, platform-driver registration, and VISL-local `visl-dec`, `visl-debugfs`, and `visl-video` helpers. Codec controls depend on the kernel stateless codec uAPI IDs and structures.

## Risks and test signals
Important risks are lifetime ordering across `video_unregister_device()` and `visl_device_release()`, missing or mismatched stateless controls when new formats are added, and global module parameters affecting concurrent users. Test signals include successful `/dev/video*` registration, `v4l2-compliance` mem2mem/request results, expected control enumeration for every coded format, probe behavior when debugfs fails, and clean open/close under repeated streaming.
