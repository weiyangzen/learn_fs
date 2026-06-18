# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_vp8_req_if.c

## Purpose
This file implements the stateless VP8 request decoder interface `vdec_vp8_slice_if`. It allocates required hardware working buffers, resolves VP8 last/golden/alt references from V4L2 timestamps, passes current bitstream/output/reference DMA addresses to firmware, and runs a single core decode.

## Important APIs, types, and functions
`struct vdec_vp8_slice_inst` owns segmentation, wrapper-Y, wrapper-C, and VLD wrapper buffers plus the VPU instance and VSI. `struct vdec_vp8_slice_vsi` carries decode info, picture info, and three reference DPB entries. `vdec_vp8_slice_get_decode_parameters()` fetches `V4L2_CID_STATELESS_VP8_FRAME`, maps last/golden/alt timestamps to capture buffers, and fills reference DMA addresses. `vdec_vp8_slice_decode()` performs buffer acquisition, metadata copy, parameter fill, firmware start/end, timeout handling, and CRC logging.

## Control flow
Initialization uses LAT/core VPU IDs even though decode waits on `MTK_VDEC_CORE`, maps the VSI, allocates four fixed working buffers, and stores their DMA addresses in `vsi->dec`. Decode clears `*res_chg`, resets firmware on flush, gets a capture buffer via the platform callback, derives chroma DMA for one-plane outputs when needed, copies source metadata to destination, fills VP8 references and frame-header type, starts VPU decode, returns resolution-change if firmware sets it, waits up to 50 ms for core completion, calls `vpu_dec_end()`, logs CRCs, and increments decoded frame count.

## State and persistence
Working buffers persist for the instance lifetime. The VSI stores current picture info and reference DPB entries per decode. No software display/free lists are maintained in this stateless path; capture/display lifecycle is handled by the request/mem2mem framework and platform callbacks.

## Dependencies and integration points
It depends on V4L2 stateless VP8 controls, V4L2 mem2mem queues, vb2 DMA-contig, MediaTek VPU APIs, interrupt waits, and platform capture-buffer callbacks. `GET_PARAM_PIC_INFO` asks firmware for sizes and mirrors them into the VSI, while crop info is intentionally not needed.

## Risks
Missing non-key-frame references log errors but do not fail decode. Resolution-change returns without calling `vpu_dec_end()` in this path, relying on firmware/upper-layer sequencing. The variable `referenct_ts` is misspelled but functional. Decode returns `err` after timeout logging even when timeout is nonzero and `err` is zero, so timeout may not propagate as failure.

## Test signals
Run stateless VP8 key/inter streams with valid and missing last/golden/alt references, one-plane and two-plane output, resolution changes, flush reset, short timeout injection, and CRC comparison on known-good streams. Confirm key frames do not emit invalid-reference errors for absent references.
