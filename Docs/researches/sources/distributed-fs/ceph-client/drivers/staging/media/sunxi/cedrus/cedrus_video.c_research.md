# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_video.c

Purpose: V4L2 ioctl and vb2 queue implementation for Cedrus. It exposes source/capture formats, validates and applies formats, chooses codec backend ops, manages streaming lifecycle, and initializes mem2mem output/capture queues.

Important APIs/functions: `cedrus_formats[]` lists encoded source and decoded capture pixelformats with direction/capability masks. `cedrus_find_format()` picks requested or first valid format. `cedrus_prepare_format()` clamps dimensions and computes bytesperline/sizeimage for encoded, tiled NV12, and untiled YUV formats. `cedrus_try/s/g_fmt_*` implement format negotiation. `cedrus_s_fmt_vid_out_p()` sets source format, toggles `VB2_V4L2_FL_SUPPORTS_M2M_HOLD_CAPTURE_BUF` for H264/HEVC, selects `ctx->current_codec`, propagates colorimetry, and resets capture format. Queue ops validate buffer sizes, queue mem2mem buffers, complete request controls, start codec/PM on OUTPUT streamon, and stop/free on OUTPUT streamoff. `cedrus_queue_init()` creates OUTPUT and CAPTURE vb2 queues, with OUTPUT requiring media requests.

Control flow: open initializes default output format, which selects a default codec and capture format. Userspace sets OUTPUT then CAPTURE. Streamon OUTPUT resumes runtime PM and calls codec `start()`. Jobs are scheduled by mem2mem; streamoff calls codec `stop()`, runtime PM put, and marks queued buffers error.

State and persistence: per-context `src_fmt`, `dst_fmt`, `current_codec`, and bit depth. Queue state persists during streaming. Capture `sizeimage` can include codec-specific extra size, notably H265 10-bit extra 2-bit data.

Dependencies/integration: integrates V4L2 ioctl core, events, mem2mem, vb2 DMA-contig, runtime PM, Cedrus codec ops, and hardware output format programming.

Risks: format changes are constrained by busy/streaming queues and capture buffer allocation; mistakes can break dynamic resolution. OUTPUT queue `requires_requests = true`, so non-request userspace will fail. H264/HEVC hold-capture-buffer support is enabled only for those codecs. Capture format defaults to the first capability-valid output, which differs by untiled capability.

Test signals: V4L2 compliance for enum/try/set/get formats, busy queue format-change rejection, request-required behavior, streamon failure cleanup, H265 10-bit `sizeimage`, dynamic resolution with same source pixfmt, and queue cleanup completing outstanding requests.
