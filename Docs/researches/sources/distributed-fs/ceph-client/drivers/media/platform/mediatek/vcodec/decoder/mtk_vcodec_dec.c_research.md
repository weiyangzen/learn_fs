# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec.c

## Purpose
This file implements the shared V4L2 mem2mem decoder ioctl and vb2 queue logic used by both stateful and stateless MediaTek decoder variants.

## Important APIs, Types, And Functions
`mtk_vcodec_dec_set_default_params()` initializes context queue defaults. `vidioc_vdec_s_fmt()`, `vidioc_vdec_g_fmt()`, try-format, enum-format, enum-framesizes, and selection handlers implement V4L2 format negotiation. `vb2ops_vdec_queue_setup()`, `vb2ops_vdec_buf_prepare()`, `vb2ops_vdec_buf_finish()`, start/stop streaming, and queue initialization implement vb2 lifecycle. `m2mops_vdec_device_run()` queues decode work; `m2mops_vdec_job_ready()` gates scheduling on header state and no pending resolution change. Decoder command helpers dispatch to stateful or stateless semantics.

## Control Flow
Open creates a context in the driver file, then this file initializes defaults and queues. Userspace sets OUTPUT codec format, which initializes the codec instance via `vdec_if_init()` from `MTK_STATE_FREE`. Stateless S_FMT also updates capture dimensions immediately. During streaming, buffers are prepared and queued through pdata-specific vb2 ops. Mem2mem scheduling queues the decode worker supplied by stateful/stateless pdata. Stop streaming flushes, completes queued buffers as errors, and updates resolution state.

## State, Persistence, And Dependencies
It mutates `struct mtk_vcodec_dec_ctx`: queue data, state, colorspace, current codec, capture fourcc, picinfo, last decoded picinfo, and buffer error state. No persistence. Dependencies include V4L2 mem2mem, media requests, vb2 DMA-contig, decoder interface `vdec_if_*`, and platform pdata.

## Integration Points
Driver probe exposes `mtk_vdec_ioctl_ops` and `mtk_vdec_m2m_ops`. Stateful/stateless files provide pdata-specific workers and queue callbacks. Codec implementations provide `vdec_if_*`.

## Risks
State transitions are subtle around `MTK_STATE_INIT`, `HEADER`, `FLUSH`, and `ABORT`. `vidioc_try_fmt_vid_cap_mplane()` and output fallback write `f->fmt.pix.pixelformat` while operating on mplane formats, which merits review. `m2mops_vdec_job_ready()` blocks while resolution change is pending until userspace acknowledges with capture streamoff. Request completion must be paired on error paths.

## Test Signals
V4L2 compliance for stateful and stateless APIs, dynamic resolution change streams, streamoff on both queues with requests, buffer size validation, abort state qbuf/dqbuf behavior, and enum-format filtering for 10-bit capture formats.
