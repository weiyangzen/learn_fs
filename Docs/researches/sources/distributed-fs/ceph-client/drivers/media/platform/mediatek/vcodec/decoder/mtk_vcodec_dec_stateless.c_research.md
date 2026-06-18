# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_stateless.c

## Purpose
This file implements the stateless/request-API decoder behavior for newer MediaTek platforms. It defines supported stateless codec controls, media-request operations, dynamic format exposure from firmware capability, request-based decode workers, and platform pdata for single-core and LAT/core architectures.

## Important APIs, Types, And Functions
`mtk_stateless_controls` defines H.264, VP8, VP9, HEVC, and AV1 controls plus profile/level/decode-mode/start-code limits. `mtk_vdec_worker()` consumes one OUTPUT request buffer, applies request controls, decodes, completes source and capture buffers, and manages request refcounts. `vdec_get_cap_buffer()` returns the current capture framebuffer to codec implementations. `mtk_vdec_s_ctrl()` validates bit depth/subsampling and switches capture format for 10-bit streams. Media request ops allocate, validate exactly one buffer, mark manual completion, and queue via `v4l2_m2m_request_queue()`. `mtk_vcodec_get_supported_formats()` populates global format tables from firmware capability bits. Pdata symbols cover MT8183, LAT single-core, and subdevice single-core variants.

## Control Flow
Probe selects stateless pdata and registers a media controller. On first open, firmware capability bits populate capture and coded formats. OUTPUT queues require media requests. Queueing the first OUTPUT buffer moves the context from INIT to HEADER. The worker applies request controls, increments request refcount, calls `vdec_if_decode()`, completes source controls/buffer, and either completes capture immediately or leaves LAT/core paths to complete later through `cap_to_disp()`. Request completion is manual and tied to kref release.

## State, Persistence, And Dependencies
State includes global static format arrays/defaults, per-context request/control state, 10-bit bitstream flag, capture format, picinfo, and message queue/VPU instance data used by codec implementations. No persistence. Dependencies include media requests, V4L2 stateless controls, vb2 DMA-contig, decoder interface, firmware capability bits, and optional LAT/core message queues.

## Integration Points
Selected by MT8183/MT8186/MT8188/MT8192/MT8195 pdata. Shared decoder ioctls use this file's controls, media ops, vb2 ops, worker, `get_cap_buffer`, and `cap_to_disp`.

## Risks
`mtk_video_formats`, defaults, and `num_formats` are global static state initialized once from the first context's firmware capability, which can be risky if multiple devices differ. `fops_media_request_alloc()` does not check allocation failure before returning `&req->req`. Request completion has multiple paths and must avoid double completion or leaks. 10-bit format switching depends on SPS/frame controls arriving before capture negotiation expectations.

## Test Signals
Stateless V4L2/media-request compliance, one-buffer request validation, H.264/VP8/VP9/HEVC/AV1 control coverage, 8-bit and 10-bit streams, LAT/core delayed capture completion, VP8 immediate completion, request error paths, and multi-device capability tests.
