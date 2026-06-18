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
