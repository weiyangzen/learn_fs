# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_v4l2.c

## Purpose
`hantro_v4l2.c` implements the V4L2 mem2mem ioctl and vb2 queue-facing contract for the Hantro VPU driver. It mediates format enumeration, try/set/get format operations, crop/selection, encoder stop/start commands, buffer setup, buffer validation, queueing, and stream lifecycle initialization for encoder and stateless decoder contexts.

## Important APIs, Types, And Functions
The file exports `hantro_ioctl_ops`, `hantro_queue_ops`, `hantro_reset_raw_fmt`, `hantro_reset_fmts`, `hantro_get_format_depth`, and `hantro_get_default_fmt`. Format selection is centered on `hantro_get_formats`, `hantro_get_postproc_formats`, `hantro_find_format`, `hantro_check_depth_match`, `hantro_try_fmt`, `hantro_set_fmt_out`, and `hantro_set_fmt_cap`. Queue lifecycle is handled by `hantro_queue_setup`, `hantro_buf_prepare`, `hantro_buf_queue`, `hantro_start_streaming`, `hantro_stop_streaming`, and request completion helpers.

## Control Flow
Applications enter through V4L2 ioctl callbacks. Enumeration filters formats by encoder/decoder direction, coded/raw side, bit depth, and optional postprocessor formats. `TRY_FMT` normalizes unsupported fourcc values to defaults, applies frame-size constraints, fills raw multi-plane layout, and adds codec-specific motion-vector side data to capture buffers when no postprocessor is used. `S_FMT` validates busy/streaming restrictions, commits source or destination format state, propagates colorimetry, resets the peer raw format when codec/depth changes, and updates request/hold-capture-buffer flags. Streaming start selects codec ops from the hardware variant based on the coded queue, runs codec init, and optionally initializes postprocessing; streaming stop tears down postprocessing and codec state and returns queued buffers with error status.

## State And Persistence
State is per `struct hantro_ctx`: source, destination, reference, VPU source/destination format pointers, bit depth, postprocessing need, codec ops pointer, and capture/output sequence counters. vb2 queue flags are updated to express request requirements and H264 hold-capture-buffer support. No state is persistent across device close; DMA and codec-private state are initialized and released through codec ops during streaming.

## Dependencies And Integration Points
The file integrates Linux V4L2, v4l2-ctrls, v4l2-event, v4l2-mem2mem, and videobuf2 APIs. It depends on Hantro core definitions from `hantro.h`, hardware sizing helpers from `hantro_hw.h`, postprocessor helpers such as `hantro_needs_postproc`, and codec motion-vector size helpers for H264, VP9, HEVC, and AV1. Hardware variants provide format tables, postprocessor format tables, and `codec_ops` arrays.

## Risks
Format state is highly order-sensitive: changing coded formats resets raw formats, and decoder dynamic resolution changes only allow pixelformat stability while streaming. Incorrect `sizeimage` calculation can underallocate buffers, especially for non-postprocessed capture formats carrying motion-vector data. Bit-depth filtering must stay aligned with variant format tables, because postprocessed formats currently allow only downconversion unless `match_depth` is set. Request and hold-capture-buffer flags are codec-specific and can break stateless decoding if updated incompletely for new formats.

## Test Signals
Useful signals include V4L2 compliance on mem2mem devices, format enumeration and `TRY_FMT`/`S_FMT` tests for encoder and decoder directions, streaming tests for EOS behavior, dynamic resolution change tests on decoder OUTPUT, and codec decode/encode tests that verify capture buffer sizing for H264, VP9, HEVC, and AV1 with and without postprocessing.
