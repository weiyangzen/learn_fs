# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_hevc_req_multi_if.c

## Purpose
This file implements the multi-core stateless HEVC request decoder interface `vdec_hevc_slice_multi_if`. It translates V4L2 HEVC controls into MediaTek firmware structures, manages HEVC MV and wrap working buffers, and coordinates LAT/core decode through the MediaTek message queue.

## Important APIs, types, and functions
Firmware parameter structures include `mtk_hevc_sps_param`, `mtk_hevc_pps_param`, `mtk_hevc_slice_header_param`, `slice_api_hevc_scaling_matrix`, `slice_api_hevc_decode_param`, and `mtk_hevc_dpb_info`. `struct vdec_hevc_slice_vsi` describes LAT/core shared memory for bitstream, UBE/trans/error/slice buffers, wrap buffer, output frame, MV buffers, state, and HEVC params. `vdec_hevc_slice_fill_decode_parameters()` copies controls into the LAT VSI and per-frame share info, while `vdec_hevc_slice_fill_decode_reflist()` fills decode params and DPB DMA info for core. `vdec_hevc_slice_lat_decode()` and `vdec_hevc_slice_core_decode()` perform the two hardware stages.

## Control flow
Init sets LAT/core VPU IDs, splits the firmware VSI into LAT and core regions, marks resolution dirty, and allocates a fixed `VDEC_HEVC_WRAP_SZ` wrap buffer. The LAT path initializes the message queue, handles flush, dequeues a LAT buffer, copies V4L2 request metadata, fills controls, allocates MV buffers if resolution changed, sets LAT buffer addresses, starts `vpu_dec_start()`, optionally queues core work early in inner-racing mode, waits for LAT completion, updates UBE write pointer, and queues core work. Core copies HEVC params from share info, gets a capture buffer, fills output/UBE/trans/wrap/MV addresses, copies destination metadata, fills DPB references, runs `vpu_dec_core()`, waits for the core interrupt, updates the UBE read pointer, and calls `cap_to_disp()`.

## State and persistence
The instance persists MV buffers, the wrap buffer, resolution/reallocation flags, capture plane count, and message-queue state. Per-frame share info keeps SPS and decode controls plus the trans buffer addresses between LAT and core.

## Dependencies and integration points
The file integrates with V4L2 stateless HEVC controls, vb2 DMA-contig buffer lookup, V4L2 mem2mem queues, MediaTek VPU LAT/core APIs, interrupt handling, and platform capture/display callbacks. `GET_PARAM_PIC_INFO` asks firmware for frame sizes and aligns buffer dimensions.

## Risks
The file does not implement pure single-core HEVC; `vdec_hevc_slice_decode()` rejects `MTK_VDEC_PURE_SINGLE_CORE`. HEVC PPS copy contains repeated assignments, which is harmless but raises maintenance risk. Missing DPB references are logged but leave reference entries without a hard error. LAT/core buffer-full handling must not lose LAT buffers. Single-plane chroma derivation depends on correct `picinfo` sizes.

## Test signals
Use stateless HEVC streams with tiles, long/short-term references, scaling matrices, resolution changes, missing references, one-plane and two-plane formats, LAT trans-buffer-full and slice-header-full firmware returns, inner-racing mode, missing capture buffers, and core timeout. Verify wrap-buffer allocation/free paths during init/deinit failures.
