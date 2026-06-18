# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-dec.c

## Purpose
`visl-dec.c` is the virtual decode execution path. It does not decode video; it consumes one coded OUTPUT buffer and one CAPTURE buffer, applies request controls, renders diagnostic text into the CAPTURE image with the V4L2 test pattern generator, emits tracepoints for stateless codec controls, optionally dumps the bitstream, and completes the mem2mem job.

## Important APIs, types, and functions
`visl_device_run()` is the mem2mem `device_run` callback. It gets the next source/destination buffers, applies request controls with `v4l2_ctrl_request_setup()`, copies metadata, increments source/capture sequence counters, fills a codec-specific `struct visl_run` union by reading controls via `visl_find_control_data()`, renders TPG text, emits trace events, optionally calls `visl_trace_bitstream()`, completes request controls, applies simulated processing delay through `visl_transtime_ms`, and finishes the job with `v4l2_m2m_buf_done_and_job_finish()`.

`visl_tpg_fill()` fills the CAPTURE buffer planes with a colorbar test pattern and overlays sequence, timestamp, codec-specific POC fields for H.264/HEVC, reference-frame information, OUTPUT/CAPTURE format metadata, and verbose queue status. `visl_get_ref_frames()` formats codec-specific reference timestamps and optionally vb2 indexes. `visl_trace_ctrls()` dispatches to tracepoints in the codec trace headers.

## Control flow
For each scheduled job, source request controls are made current before any control payloads are read. The current codec selected by `visl-video.c` determines which union members are populated and which trace functions run. After TPG and trace/debugfs work, request controls are completed and both buffers are completed as `VB2_BUF_STATE_DONE`.

## State and persistence
State changes are limited to queue sequence counters, destination field metadata, the per-context TPG text buffer, and optional debugfs blob state in `visl-debugfs.c`. It reads DPB/reference timestamps from controls but does not maintain decoder reference pictures itself; references are resolved against queued capture buffers with `vb2_find_buffer()`.

## Dependencies and integration points
The file depends on V4L2 mem2mem, vb2, request controls, the TPG library, debugfs helpers, and all VISL tracepoint headers. It consumes `struct visl_run` from `visl-dec.h` and codec selection from `struct visl_ctx`.

## Risks and test signals
Risks include null control payloads if request validation/control setup misses a required control, text buffer truncation for verbose queue dumps, AV1 reference index assumptions, and latency from trace/debugfs output. Test signals include frame completion under all supported codecs, correct request-control lifetime, tracepoint events appearing for codec controls, expected TPG overlay text, and no leaked/incomplete requests on streamoff.
