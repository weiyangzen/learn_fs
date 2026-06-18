# subset-b-004189 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-core.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-debugfs.c

## Purpose
`visl-debugfs.c` implements optional debugfs dumping of submitted OUTPUT bitstream buffers. It gives stateless decoder developers a way to inspect raw encoded payloads for selected frame ranges, similar in spirit to userspace media API trace buffers.

## Important APIs, types, and functions
`visl_debugfs_init()` creates `/sys/kernel/debug/visl`, initializes `dev->bitstream_blobs`, initializes `dev->bitstream_lock`, and calls `visl_debugfs_bitstream_init()` to create the `bitstream` directory. `visl_trace_bitstream()` copies the current source buffer payload from `vb2_plane_vaddr()` into a `vzalloc()`-backed `debugfs_blob_wrapper`, creates a read-only `bitstream%d` file keyed by the OUTPUT sequence, and appends the wrapper to `dev->bitstream_blobs`. `visl_debugfs_clear_bitstream()` removes all tracked blobs under `bitstream_lock`. `visl_debugfs_bitstream_deinit()` and `visl_debugfs_deinit()` clear blobs and remove directories recursively.

## Control flow
The core probe calls `visl_debugfs_init()`. During `visl_device_run()`, the decoder calls `visl_trace_bitstream()` only if the current destination sequence is inside the configured `bitstream_trace_frame_start`/`bitstream_trace_nframes` window. Stream stop calls `visl_debugfs_clear_bitstream()` unless `keep_bitstream_buffers` is set. Device release always deinitializes debugfs.

## State and persistence
The persistent state is the `struct visl_blob` list held by `struct visl_dev`. Each blob owns a copied payload buffer and a debugfs dentry. Blobs may survive streamoff if `keep_bitstream_buffers` is true, but module/device teardown removes them unconditionally.

## Dependencies and integration points
The file depends on debugfs, vb2 payload access, V4L2 mem2mem buffer structures, `struct visl_run`, and the `CONFIG_VISL_DEBUGFS` members in `struct visl_dev`. It is called from core probe/release and decode/streamoff paths.

## Risks and test signals
The main risks are memory growth when large payloads are preserved, silent loss of trace data when allocations or debugfs creation fail, and reliance on a valid plane virtual address. Test signals include blob creation with expected byte contents for traced frames, cleanup on streamoff, persistence when `keep_bitstream_buffers=1`, and absence of leaks under repeated tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-debugfs.h

## Purpose
`visl-debugfs.h` declares the debugfs bitstream tracing interface and provides no-op inline fallbacks when `CONFIG_VISL_DEBUGFS` is disabled.

## Important APIs, types, and functions
When debugfs support is enabled, it declares `visl_debugfs_init()`, `visl_debugfs_bitstream_init()`, `visl_trace_bitstream()`, `visl_debugfs_clear_bitstream()`, `visl_debugfs_bitstream_deinit()`, and `visl_debugfs_deinit()`. The declarations depend on `struct visl_dev`, `struct visl_ctx`, and `struct visl_run` from `visl.h` and `visl-dec.h`.

When debugfs support is disabled, all APIs remain available as inline stubs. Initialization stubs return success and action stubs do nothing, allowing callers in core, video, and decode paths to avoid preprocessor branching.

## Control flow
The header does not execute logic directly. Its compile-time branch decides whether VISL links real debugfs behavior or no-op behavior. This keeps the runtime control flow in `visl-core.c`, `visl-video.c`, and `visl-dec.c` identical across configurations.

## State and persistence
The header defines no state. With the disabled branch, VISL has no bitstream debugfs state. With the enabled branch, state is owned by `struct visl_dev` fields compiled under `CONFIG_VISL_DEBUGFS`.

## Dependencies and integration points
It integrates the optional debugfs implementation with the rest of the VISL driver and is included by the core, video, and decoder implementation files.

## Risks and test signals
The main risk is API drift between the real functions and no-op stubs. Build coverage should include both `CONFIG_VISL_DEBUGFS=y` and disabled configurations. Runtime test signals are successful VISL operation with debugfs absent and visible bitstream dump files when enabled and tracing is configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-dec.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-dec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-dec.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-dec.h

## Purpose
`visl-dec.h` defines the per-job control payload container used by the virtual decode path.

## Important APIs, types, and functions
The header declares one small run structure per supported codec: `visl_fwht_run`, `visl_mpeg2_run`, `visl_vp8_run`, `visl_vp9_run`, `visl_h264_run`, `visl_hevc_run`, and `visl_av1_run`. Each stores typed pointers to the stateless V4L2 control structs needed by that codec. `struct visl_run` combines source and destination `vb2_v4l2_buffer` pointers with a union of those codec-specific structures.

It also declares `visl_dec_start()`, `visl_dec_stop()`, `visl_job_ready()`, and `visl_device_run()`. In this source set only `visl_device_run()` is implemented and wired into the mem2mem ops.

## Control flow
`visl_device_run()` fills the relevant union member based on `ctx->current_codec`, then passes the run object to TPG, tracepoint, and debugfs routines. The header is the typed contract that keeps those consumers from manually re-fetching controls.

## State and persistence
The run object is stack-local for one mem2mem job and does not persist beyond a single output/capture buffer pair. It contains borrowed pointers into the active V4L2 control handler.

## Dependencies and integration points
It includes V4L2 stateless control definitions and `visl.h`. It is included by decoder and debugfs code because bitstream tracing needs access to the source buffer in `struct visl_run`.

## Risks and test signals
The header must be kept synchronized with the controls registered in `visl-core.c` and the trace dispatch in `visl-dec.c`. New codec controls need new fields or updated trace paths. Build warnings and per-codec request tests are the best signals for mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-dec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-av1.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-av1.h

## Purpose
`visl-trace-av1.h` defines Linux tracepoints for AV1 stateless V4L2 controls submitted to VISL.

## Important APIs, types, and functions
The header sets `TRACE_SYSTEM` to `visl_av1_controls` and declares event classes for `v4l2_ctrl_av1_sequence`, `v4l2_ctrl_av1_tile_group_entry`, `v4l2_ctrl_av1_frame`, and `v4l2_ctrl_av1_film_grain`. Each event copies the entire control struct into the trace entry and prints important scalar fields, flags, and arrays with `__print_flags()` and `__print_array()`.

The frame trace covers tile layout, quantization, super-resolution, segmentation, loop filter, CDEF, skip mode, restoration, frame flags, dimensions, frame IDs, buffer removal time, order hints, reference timestamps, reference indices, and refresh flags. The film-grain trace covers grain flags, points, AR coefficients, scaling, and chroma multipliers/offsets.

## Control flow
The header contributes tracepoint definitions that are instantiated by `visl-trace-points.c`. `visl_trace_ctrls()` in `visl-dec.c` calls the generated `trace_v4l2_ctrl_av1_*()` functions for the current AV1 request.

## State and persistence
Trace events copy control data at the time of tracing. They do not modify decoder state and are retained only by the kernel tracing infrastructure according to tracing configuration.

## Dependencies and integration points
It depends on `linux/tracepoint.h`, AV1 V4L2 stateless control structs and constants, and `TRACE_INCLUDE_PATH` pointing back to the VISL source directory for trace generation.

## Risks and test signals
Risks include large trace payloads, stale field lists if AV1 control structs evolve, and reference-index values being printed without semantic validation. Test signals include successful tracepoint compilation and readable events under `trace-cmd`/ftrace while decoding AV1 requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-av1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-fwht.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-fwht.h

## Purpose
`visl-trace-fwht.h` defines the VISL tracepoint for the FWHT stateless parameter control.

## Important APIs, types, and functions
It sets `TRACE_SYSTEM` to `visl_fwht_controls` and declares `v4l2_ctrl_fwht_params_tmpl`, instantiated as `v4l2_ctrl_fwht_params`. The event stores individual FWHT fields: backward reference timestamp, version, width, height, flags, colorspace, transfer function, YCbCr encoding, and quantization. FWHT flags are decoded with `__print_flags()`.

## Control flow
`visl_trace_ctrls()` calls `trace_v4l2_ctrl_fwht_params()` when the current codec is `VISL_CODEC_FWHT`. `visl-trace-points.c` provides the single translation unit that creates the tracepoint symbols.

## State and persistence
No driver state is changed. The tracepoint snapshots a control payload for kernel tracing.

## Dependencies and integration points
It depends on the V4L2 FWHT control struct and the kernel tracepoint macro system. Its integration point is the decode trace dispatch in `visl-dec.c`.

## Risks and test signals
The tracepoint is small, so the main risk is field drift if the FWHT control changes. Test signals are successful module build and ftrace output showing FWHT parameters during FWHT stateless requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-fwht.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-h264.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-h264.h

## Purpose
`visl-trace-h264.h` defines tracepoints for H.264 stateless V4L2 controls and reference structures.

## Important APIs, types, and functions
The trace system is `visl_h264_controls`. Event classes cover SPS, PPS, scaling matrix, prediction weights, slice parameters, reference-list entries, decode parameters, and DPB entries. Defined events include `v4l2_ctrl_h264_sps`, `v4l2_ctrl_h264_pps`, `v4l2_ctrl_h264_scaling_matrix`, `v4l2_ctrl_h264_pred_weights`, `v4l2_ctrl_h264_slice_params`, `v4l2_h264_ref_pic_list0`, `v4l2_h264_ref_pic_list1`, `v4l2_ctrl_h264_decode_params`, and `v4l2_h264_dpb_entry`.

The print logic decodes constraint/PPS/SPS/slice/decode flags, slice type symbols, reference fields, DPB validity/activity flags, order counts, frame numbers, and matrix/weight arrays.

## Control flow
During an H.264 VISL job, `visl_trace_ctrls()` emits SPS, PPS, scaling matrix, slice params, every ref list entry, decode params, every DPB entry, and prediction weights. Trace symbols are generated by including this header from `visl-trace-points.c` with `CREATE_TRACE_POINTS`.

## State and persistence
Trace events snapshot the submitted controls. There is no H.264 decoder state machine; DPB and reference-list data are printed from the userspace-provided request controls.

## Dependencies and integration points
The header depends on V4L2 H.264 stateless structs/constants, tracepoint macros, and the VISL trace instantiation file. It complements TPG reference rendering in `visl-dec.c`.

## Risks and test signals
Risks are verbose trace volume, stale struct-field coverage as the uAPI changes, and trace output that can expose malformed but unvalidated request data. Tests should decode H.264 samples through a stateless userspace stack and confirm all expected trace events appear with DPB/reference-list entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-h264.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-hevc.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-hevc.h

## Purpose
`visl-trace-hevc.h` defines tracepoints for HEVC stateless V4L2 controls, reference picture sets, prediction weights, and DPB entries.

## Important APIs, types, and functions
The trace system is `visl_hevc_controls`. Event classes cover HEVC SPS, PPS, slice parameters, prediction weight tables, scaling matrices, decode parameters, long-term RPS extension, short-term RPS extension, and DPB entries. Defined events include `v4l2_ctrl_hevc_sps`, `v4l2_ctrl_hevc_pps`, `v4l2_ctrl_hevc_slice_params`, `v4l2_hevc_pred_weight_table`, `v4l2_ctrl_hevc_scaling_matrix`, `v4l2_ctrl_hevc_decode_params`, `v4l2_ctrl_hevc_ext_sps_lt_rps`, `v4l2_ctrl_hevc_ext_sps_st_rps`, and `v4l2_hevc_dpb_entry`.

The print logic decodes many HEVC flags and arrays: SPS/PPS feature flags, slice reference indices, weighted prediction arrays, scaling lists, decode POC sets, RPS fields, DPB timestamps, and long-term-reference flags.

## Control flow
`visl_trace_ctrls()` invokes these trace events for HEVC jobs after request controls are applied. The header is instantiated only through `visl-trace-points.c`.

## State and persistence
The tracepoints copy submitted control payloads and do not maintain any decoder state. Persistence is entirely in the kernel trace buffer.

## Dependencies and integration points
It depends on `linux/v4l2-controls.h`, `linux/tracepoint.h`, V4L2 HEVC stateless definitions, and VISL's trace include path. It integrates with the HEVC control descriptors in `visl-core.c` and the `visl_hevc_run` union in `visl-dec.h`.

## Risks and test signals
HEVC has large nested control data, so trace volume and field drift are the main risks. Tests should build with tracing enabled and run HEVC stateless requests that include slice params, decode params, RPS controls, and DPB entries, confirming all event printers compile and produce readable output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-hevc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-mpeg2.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-mpeg2.h

## Purpose
`visl-trace-mpeg2.h` defines tracepoints for MPEG-2 stateless controls submitted to VISL.

## Important APIs, types, and functions
The trace system is `visl_mpeg2_controls`. It declares event classes for sequence, picture, and quantisation controls and defines `v4l2_ctrl_mpeg2_sequence`, `v4l2_ctrl_mpeg2_picture`, and `v4l2_ctrl_mpeg2_quantisation`. The sequence event prints dimensions, VBV buffer size, profile/level, chroma format, and progressive flag. The picture event prints reference timestamps, picture flags, f-code bytes, coding type, structure, and intra DC precision. The quantisation event prints quantizer matrices.

## Control flow
`visl_trace_ctrls()` emits all three MPEG-2 events for `VISL_CODEC_MPEG2`. `visl-trace-points.c` instantiates the tracepoints.

## State and persistence
The header creates trace snapshots only. MPEG-2 reference behavior remains in request controls and TPG reference text.

## Dependencies and integration points
It depends on V4L2 MPEG-2 stateless control structs and tracepoint helpers. It is paired with the MPEG-2 control descriptors in `visl-core.c`.

## Risks and test signals
Risks are small but include stale field coverage and high output from matrix arrays. Test signals include trace output for sequence/picture/quantisation controls when MPEG-2 requests are queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-mpeg2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-points.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-points.c

## Purpose
`visl-trace-points.c` is the tracepoint instantiation unit for VISL codec-control tracing.

## Important APIs, types, and functions
The file includes `visl.h`, defines `CREATE_TRACE_POINTS`, and includes the FWHT, MPEG-2, VP8, VP9, H.264, HEVC, and AV1 trace headers. This causes the Linux tracepoint framework to generate the concrete tracepoint definitions once.

## Control flow
There is no runtime control flow in this file. Its build-time role is to ensure that `trace_v4l2_ctrl_*()` functions referenced by `visl-dec.c` have storage and metadata.

## State and persistence
No VISL state is owned here. Tracepoint state is managed by the kernel tracing subsystem.

## Dependencies and integration points
It depends on all VISL trace headers and must remain in the module build whenever those trace functions are called. It is the central integration point between declarative trace headers and decoder runtime calls.

## Risks and test signals
The key risk is duplicate or missing tracepoint instantiation if headers are included incorrectly elsewhere. Test signals include successful module link and visible trace events under `/sys/kernel/tracing/events/visl_*_controls`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-points.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-vp8.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-vp8.h

## Purpose
`visl-trace-vp8.h` defines tracepoints for VP8 stateless frame and entropy controls.

## Important APIs, types, and functions
The trace system is `visl_vp8_controls`. It declares `v4l2_ctrl_vp8_entropy_tmpl` and `v4l2_ctrl_vp8_frame_tmpl`, instantiated as `v4l2_ctrl_vp8_entropy` and `v4l2_ctrl_vp8_frame`. The entropy event prints coefficient probabilities, Y/UV mode probabilities, and motion-vector probabilities. The frame event prints segmentation, loop filter, quantization, coder state, dimensions, scale, partition sizes, reference timestamps, and VP8 frame flags.

## Control flow
`visl_trace_ctrls()` emits both VP8 events for a VP8 job. The tracepoints are generated by `visl-trace-points.c`.

## State and persistence
The events copy a `struct v4l2_ctrl_vp8_frame` snapshot and do not modify state.

## Dependencies and integration points
It depends on V4L2 VP8 stateless definitions and trace macros. It integrates with `visl_vp8_ctrls` and `struct visl_vp8_run`.

## Risks and test signals
The largest risk is trace verbosity from probability arrays. Test signals include readable VP8 frame and entropy events under ftrace while processing VP8 stateless requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-vp8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-vp9.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-vp9.h

## Purpose
`visl-trace-vp9.h` defines tracepoints for VP9 stateless frame controls, compressed header probabilities, coefficient probabilities, and motion-vector probabilities.

## Important APIs, types, and functions
The trace system is `visl_vp9_controls`. Event classes cover `struct v4l2_ctrl_vp9_frame`, `struct v4l2_ctrl_vp9_compressed_hdr`, coefficient arrays within the compressed header, and `struct v4l2_vp9_mv_probs`. Defined events are `v4l2_ctrl_vp9_frame`, `v4l2_ctrl_vp9_compressed_hdr`, `v4l2_ctrl_vp9_compressed_coeff`, and `v4l2_vp9_mv_probs`.

The frame event prints loop filter, quantization, segmentation, flags, headers, dimensions, reference timestamps, sign bias, reset context, profile, bit depth, interpolation filter, tile geometry, and reference mode. Header and coefficient events dump probability arrays.

## Control flow
For `VISL_CODEC_VP9`, `visl_trace_ctrls()` emits frame, compressed-header, coefficient, and motion-vector probability events.

## State and persistence
The header creates trace snapshots only. It does not track VP9 frame contexts or probability updates beyond the submitted control values.

## Dependencies and integration points
It depends on V4L2 VP9 stateless controls and the Linux tracepoint framework. It is tied to `visl_vp9_ctrls` and `struct visl_vp9_run`.

## Risks and test signals
Risks include very large trace output and stale probability-array formatting if the uAPI changes. Test signals are successful tracepoint compilation and expected VP9 events during stateless VP9 request playback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-vp9.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-video.c

## Purpose
`visl-video.c` implements VISL's V4L2 stateless interface: format enumeration/negotiation, ioctl dispatch, vb2 queue setup, streaming lifecycle, and request validation.

## Important APIs, types, and functions
`visl_coded_fmts` maps supported coded formats to frame-size limits, stateless control sets, and allowed decoded formats. Supported coded formats are FWHT, MPEG-2 slice, VP8 frame, VP9 frame, H.264 slice, HEVC slice, and AV1 frame; decoded formats are primarily NV12/YUV420 with P010 exposed only under `V4L2_FMTDESC_FLAG_ENUM_ALL`.

`visl_set_current_codec()` translates the OUTPUT fourcc into `enum visl_codec`. `visl_tpg_init()` initializes the V4L2 test pattern generator for the current CAPTURE format. `visl_s_fmt_vid_out()` validates OUTPUT format, updates `ctx->coded_format_desc`, resets CAPTURE format, propagates colorimetry, and updates `ctx->current_codec`. `visl_s_fmt_vid_cap()` validates CAPTURE format and reinitializes the TPG.

`visl_ioctl_ops` exposes core format, buffer, streaming, decoder command, and event ioctls. `visl_queue_init()` creates OUTPUT and CAPTURE vb2 queues using vmalloc memory; OUTPUT supports requests and m2m hold-capture-buffer behavior. `visl_request_validate()` enforces exactly one buffer per media request before delegating to `vb2_request_validate()`.

## Control flow
A new context starts with FWHT OUTPUT and matching CAPTURE defaults. Userspace sets OUTPUT to choose the codec; CAPTURE is reset to a compatible decoded format and TPG state is rebuilt. Queue setup validates plane counts/sizes. Start streaming resets per-queue sequence counters and records CAPTURE stream time. Buffer queueing goes into the V4L2 mem2mem scheduler. Stop streaming drains queued buffers as errors and clears debugfs bitstreams unless configured to keep them.

## State and persistence
Per-context state includes coded/decoded `v4l2_format`, selected codec, sequence counters, TPG state, and capture stream start jiffies. The file also controls debugfs bitstream persistence through streamoff behavior.

## Dependencies and integration points
It depends on V4L2 ioctl/event APIs, videobuf2-vmalloc, mem2mem, V4L2 TPG, VISL core structures, and debugfs cleanup helpers. It is wired into the video device in `visl-core.c`.

## Risks and test signals
Risks include incorrect plane-size calculations due to use of `fmt.pix` aliases on multiplanar formats, codec/control mismatch when adding formats, request validation that is intentionally narrow, and TPG init failure if the VGA font or fourcc support is unavailable. Test signals include `v4l2-compliance`, format enumeration by codec, request queue tests with zero/one/multiple buffers, streamoff cleanup behavior, and generated CAPTURE frames in all decoded formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-video.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-video.h

## Purpose
`visl-video.h` declares the public video-interface hooks exported by `visl-video.c` to the VISL core.

## Important APIs, types, and functions
The header exports `visl_ioctl_ops`, all codec control-set descriptors (`visl_fwht_ctrls` through `visl_av1_ctrls`), `visl_queue_init()`, `visl_set_default_format()`, and `visl_request_validate()`.

## Control flow
`visl-core.c` consumes `visl_ioctl_ops` when defining the `video_device`, passes `visl_queue_init()` to `v4l2_m2m_ctx_init()` during open, calls `visl_set_default_format()` for new contexts, and registers `visl_request_validate()` as the media-device request validator.

## State and persistence
The header owns no state. It exposes operations that initialize and validate per-context state.

## Dependencies and integration points
It includes V4L2 mem2mem and `visl.h`. It is the narrow interface between device lifecycle code and V4L2/vb2 implementation code.

## Risks and test signals
The main risk is declaration drift from `visl-video.c` or missing exports when codec control sets change. Build coverage is the primary test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl.h

## Purpose
`visl.h` is the central VISL header. It defines driver constants, global module-parameter declarations, debug-print helpers, device/context structures, codec/format descriptors, and shared control lookup APIs.

## Important APIs, types, and functions
Key constants include `VISL_NAME`, `VISL_M2M_NQUEUES`, and `TPG_STR_BUF_SZ`. `struct visl_ctrls` and `struct visl_coded_format_desc` describe registered controls and coded-format capabilities. `enum visl_codec` identifies the currently selected codec.

`struct visl_dev` owns the V4L2 device, video device, optional media device, device mutex, mem2mem device, and optional debugfs state. `struct visl_ctx` owns a V4L2 file handle, control handler, vb2 mutex, source/capture queue data, current codec, coded/decoded formats, TPG state, stream timing, and text buffer. `struct visl_blob` describes a debugfs bitstream blob. `visl_file_to_ctx()` maps a file to its context.

## Control flow
The header provides the shared types used by open/release, format negotiation, decode execution, debugfs, and tracepoints. Runtime behavior is implemented in the corresponding `.c` files.

## State and persistence
`struct visl_dev` is device-lifetime state; `struct visl_ctx` is per-open state; `struct visl_q_data.sequence` is per-queue streaming state. Global module parameters are declared here and defined in `visl-core.c`.

## Dependencies and integration points
It depends on Linux list/debugfs headers, V4L2 controls/device APIs, and the V4L2 TPG API. Every VISL implementation file includes or depends on it.

## Risks and test signals
Risks include conditional debugfs fields requiring matching stubs, global module-parameter effects across contexts, and structure changes affecting many files. Build coverage across debugfs/media-controller configurations and open/stream/close tests are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/Kconfig

## Purpose
`vivid/Kconfig` defines build-time configuration options for the VIVID virtual video test driver.

## Important APIs, types, and functions
`VIDEO_VIVID` is a tristate driver option depending on `VIDEO_DEV`, non-SPARC architectures, and `HAS_DMA`. It selects font support, `FONT_8x16`, vmalloc and dma-contig vb2 allocators, the V4L2 TPG, and media-controller support. `VIDEO_VIVID_CEC` enables HDMI CEC emulation and selects `CEC_CORE`. `VIDEO_VIVID_OSD` enables framebuffer support for output overlay testing and selects framebuffer I/O-memory helpers. `VIDEO_VIVID_MAX_DEVS` configures the maximum number of instances, defaulting to 64.

## Control flow
These options decide which source files are built by the Makefile and which fields/code paths are compiled in VIVID core and CEC/OSD support.

## State and persistence
Kconfig state persists in the kernel configuration. It affects module shape, selected dependencies, and maximum instance array sizes.

## Dependencies and integration points
It integrates VIVID with kernel media, CEC, framebuffer, font, and vb2 subsystems. The configured symbols are consumed by the Makefile and conditional code in `vivid-core.c`, `vivid-core.h`, and `vivid-cec.h`.

## Risks and test signals
Risks include unmet selected dependency combinations, overly large `VIDEO_VIVID_MAX_DEVS`, and missing coverage for optional CEC/OSD builds. Test signals are kernel config/build combinations for base, CEC, and OSD variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/Makefile

## Purpose
`vivid/Makefile` defines the object composition for the VIVID kernel module.

## Important APIs, types, and functions
`vivid-objs` includes core, controls, common video, VBI, capture/output kthreads, radio RX/TX, RDS, SDR, metadata, and touch capture components. It conditionally adds `vivid-cec.o` when `CONFIG_VIDEO_VIVID_CEC=y` and `vivid-osd.o` when `CONFIG_VIDEO_VIVID_OSD=y`. `obj-$(CONFIG_VIDEO_VIVID) += vivid.o` ties the aggregate object to the Kconfig driver symbol.

## Control flow
The Makefile affects build composition only. Runtime control flow is determined by the compiled objects and module parameters in `vivid-core.c`.

## State and persistence
No runtime state is stored here. Build configuration state controls which symbols are linked.

## Dependencies and integration points
It integrates all VIVID source modules into one `vivid` module and mirrors optional Kconfig features.

## Risks and test signals
Risks are missing object entries for newly added source files or conditional objects getting out of sync with Kconfig. Test signals are successful builds with `VIDEO_VIVID=m/y`, with and without CEC/OSD.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-cec.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-cec.c

## Purpose
`vivid-cec.c` emulates HDMI CEC adapters and a shared CEC bus for VIVID HDMI inputs/outputs.

## Important APIs, types, and functions
`vivid_cec_alloc_adap()` creates a CEC adapter with monitor capabilities and VIVID CEC ops. `vivid_cec_bus_thread()` is the kernel thread that models signal-free-time readiness, bus arbitration, ACK/NACK status, timing delays, transmit completion, and delivery to destination adapters. `vivid_cec_adap_transmit()` queues a pending transfer in the receiver-side device's `xfers[]` slot indexed by initiator. `find_dest_adap()` checks whether a destination logical address exists on the local HDMI input adapter or on connected HDMI output adapters. `vivid_received()` implements test responses for `CEC_MSG_SET_OSD_STRING` and `CEC_MSG_VENDOR_COMMAND_WITH_ID`.

## Control flow
CEC adapters call `adap_transmit`, which records message bytes, length, adapter, and desired signal-free time under `cec_xfers_slock`, then wakes the bus thread. The thread selects ready transfers, marks simultaneous losers as arbitration lost, checks destination validity, sleeps to emulate bus time, calls `cec_transmit_attempt_done()`, and delivers successful messages via `cec_received_msg()` to all relevant virtual adapters except the sender.

## State and persistence
CEC state lives in `struct vivid_dev`: receive/transmit adapters, `xfers[]`, signal-free time, last initiator, waitqueue, and OSD text. OSD text may persist until cleared or replaced depending on the CEC display-control value.

## Dependencies and integration points
The file depends on the kernel CEC framework, VIVID connection maps from `vivid-core.h`, HDMI-to-output menu state, and the VIVID core thread lifecycle. It is compiled only when `CONFIG_VIDEO_VIVID_CEC` is enabled.

## Risks and test signals
Risks include simplified arbitration that uses initiator-level rather than bit-level precision, one pending transfer per initiator slot, connection-map races if topology changes, and incorrect timing under scheduler delays. Test signals include CEC compliance tests, successful OSD string handling on sink adapters, vendor-command reply behavior, expected arbitration-lost statuses, and NACKs for unconfigured destinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-cec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-cec.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-cec.h

## Purpose
`vivid-cec.h` declares VIVID CEC hooks when CEC emulation is enabled.

## Important APIs, types, and functions
Under `CONFIG_VIDEO_VIVID_CEC`, it declares `vivid_cec_alloc_adap()` and `vivid_cec_bus_thread()`. The adapter allocator creates CEC adapters for HDMI capture/output endpoints; the bus thread runs the virtual shared bus.

## Control flow
`vivid-core.c` includes this header, allocates adapters during instance creation, starts the bus thread when CEC endpoints exist, registers adapters during video-node creation, and unregisters/stops them during teardown.

## State and persistence
The header owns no state. CEC state is in `struct vivid_dev`.

## Dependencies and integration points
It depends on `struct vivid_dev` from `vivid-core.h` and the CEC framework types included there. The declarations are unavailable when CEC is not configured, matching conditional call sites.

## Risks and test signals
The primary risk is conditional-build drift. Build tests with `CONFIG_VIDEO_VIVID_CEC=y` and disabled are required, along with runtime adapter registration tests for HDMI-enabled VIVID instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-cec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-core.c

## Purpose
`vivid-core.c` is the central module and instance lifecycle implementation for the VIVID virtual video test driver. It creates configurable virtual capture/output/radio/SDR/VBI/metadata/touch devices, exposes shared V4L2 ioctl dispatch, initializes queues/controls/media entities, and tears everything down.

## Important APIs, types, and functions
The file defines many module parameters controlling instance count, device-node numbers, crop/compose/scale modes, planar API, node-type bitmask, input/output counts and types, debug level, allocator choice, cache hints, request support, and error-injection availability.

`vidioc_querycap()` reports aggregate capabilities. Many wrapper ioctls dispatch to subsystem-specific implementations depending on `video_device` type/direction, such as video capture/output, radio, SDR, touch, VBI, and metadata handlers. `vivid_ioctl_ops` collects the broad V4L2 ioctl surface; `vivid_fops` and `vivid_radio_fops` provide file operations.

Lifecycle helpers include `vivid_create_queue()` for vb2 queue initialization, `vivid_detect_feature_set()` for interpreting module parameters into `struct vivid_dev` feature booleans, `vivid_set_capabilities()`, `vivid_disable_unused_ioctls()`, `vivid_init_dv_timings()`, `vivid_create_queues()`, `vivid_create_devnodes()`, and `vivid_create_instance()`. Module probe creates requested instances; remove unregisters every created node and adapter.

## Control flow
`vivid_init()` prebuilds HDMI/S-Video output menu labels, registers a platform device/driver, and creates workqueues. Probe verifies the font, clamps `n_devs`, and calls `vivid_create_instance()` for each instance. Instance creation registers the V4L2/media device, detects enabled features, initializes TPG/EDID/timings/default formats/controls/locks/lists/queues, optionally allocates CEC adapters and starts the CEC thread, sets up controls, creates device nodes, and stores the instance in `vivid_devs`.

Runtime ioctls enter the common operation table and dispatch to the correct subsystem. File release handles disconnect-error reconnection and RDS ownership cleanup before delegating to vb2 or V4L2 fh release.

## State and persistence
Global state includes `vivid_devs[]`, `n_devs`, HDMI/S-Video connection menu strings, output skip masks, and update workqueues. Per-instance state is the large `struct vivid_dev`: controls, device nodes, capabilities, inputs/outputs, vb2 queues, active lists, stream counters, TPG, EDID, timings, framebuffer state, error injection flags, radio/RDS state, CEC state, and connection mappings.

## Dependencies and integration points
The file integrates V4L2 core, media controller, videobuf2 vmalloc/dma-contig allocators, V4L2 TPG, platform devices, font support, CEC, framebuffer OSD, and many VIVID subsystem files. Request validation is media-controller based and can inject validation errors.

## Risks and test signals
Risks are high because module parameters can create many feature combinations; cleanup paths must unregister partially created devices correctly; `vivid_init()` error handling includes a suspicious `platform_driver_register()` call in the `unreg_driver` path where unregister would be expected; and dynamic menu/workqueue updates require careful locking. Test signals include `v4l2-compliance` across node-type combinations, probe/remove loops, CEC/OSD optional builds, request-support modes, allocator/cache-hint combinations, disconnect error injection, and leak checks after partial probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-core.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-core.h

## Purpose
`vivid-core.h` defines the central data model and shared constants for the VIVID virtual video test driver.

## Important APIs, types, and functions
The header defines maximum counts, geometry limits, tuner frequency ranges, SDR buffer sizes, HDMI/S-Video menu constants, and `VIVID_MAX_DEVS`. It declares global output-connection menu state, workqueues, device arrays, and shared rectangles.

`struct vivid_fmt` describes pixel formats, color encoding, overlay support, plane/buffer layout, offsets, and bit depth. `struct vivid_buffer` wraps `vb2_v4l2_buffer` for active-list use. Enums describe input types, signal modes, and colorspaces. `struct vivid_cec_xfer` stores one pending CEC transfer.

`struct vivid_dev` is the driver’s main per-instance object. It embeds V4L2/media/video devices, many control handlers and controls, capability flags, input/output topology, connection mappings, framebuffer/overlay state, error injection state, current capture/output formats and rectangles, vb2 queues and active lists, stream-generation thread state, SDR/radio/RDS state, CEC adapters/thread/transfer queue, OSD string, and metadata flags. Inline helpers classify the current input/output type.

## Control flow
The header does not implement the lifecycle, but its fields are initialized and consumed across `vivid-core.c` and all subsystem files. The inline helpers guide ioctl behavior and format/timing decisions.

## State and persistence
Nearly all VIVID runtime state is represented here. Per-instance state persists from `vivid_create_instance()` until `vivid_dev_release()`. Global arrays and workqueues persist for the module lifetime.

## Dependencies and integration points
It depends on framebuffer, workqueue, CEC, vb2, V4L2 device/control, TPG, RDS, and VBI generator headers. It is the shared contract for the full VIVID module.

## Risks and test signals
Risks include structure bloat and cross-file coupling, conditional fields under media-controller/CEC/OSD configs, and shared global topology state that must be synchronized. Test signals are broad build coverage, static analysis for uninitialized fields, and runtime tests that exercise each node class and topology link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-core.h -->
