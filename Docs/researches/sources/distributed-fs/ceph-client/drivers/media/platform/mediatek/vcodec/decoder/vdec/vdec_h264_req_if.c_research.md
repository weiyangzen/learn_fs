# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_h264_req_if.c

## Purpose
This file implements the single-core stateless H.264 request decoder interface `vdec_h264_slice_if`. It obtains V4L2 H.264 controls for each request, packs them into a local VSI, allocates prediction and MV working buffers, gets capture buffers from the platform callback, and runs one hardware decode per submitted slice/frame.

## Important APIs, types, and functions
`struct vdec_h264_slice_inst` owns the context, VPU instance, local `vsi_ctx`, prediction buffer, 32 MV buffers, current firmware slice parameters, and persistent DPB. `get_vdec_decode_parameters()` fetches decode/SPS/PPS/scaling controls, updates DPB, copies firmware params, fills DPB DMA info, builds P/B reference lists, and copies the result into `vsi_ctx`. `vdec_h264_slice_decode()` is the main decode function. `get_pic_info()` computes aligned buffer dimensions from `ctx->picinfo` and flags resolution/MV reallocation.

## Control flow
Initialization uses `SCP_IPI_VDEC_H264`, copies the initial firmware VSI into local memory, marks resolution and MV buffers dirty, and allocates the prediction buffer. Decode on `bs == NULL` resets firmware. Otherwise it gets a capture buffer, copies source metadata to destination metadata, fills input/output DMA addresses in `vsi_ctx`, builds decode parameters, reconstructs a NAL header byte from decode params, handles resolution-triggered MV allocation, copies the local VSI to firmware memory, starts VPU decode, waits for a core interrupt, calls `vpu_dec_end()`, and refreshes local `vsi_ctx` from firmware.

## State and persistence
The instance keeps DPB state across requests, local VSI state copied to and from firmware, prediction memory, MV buffers sized by current coded dimensions, and `num_nalu`. Resolution change state lives in `vsi_ctx.dec.resolution_changed` and `realloc_mv_buf`.

## Dependencies and integration points
This path uses common H.264 request helpers, V4L2 stateless controls, V4L2 mem2mem metadata copying, vb2 DMA-contig reference lookup through helpers, MediaTek VPU APIs, and platform `get_cap_buffer()`. It supports `GET_PARAM_PIC_INFO`, `GET_PARAM_DPB_SIZE`, and `GET_PARAM_CROP_INFO`.

## Risks
The caller-provided `unused` frame argument is ignored; buffer acquisition depends entirely on platform callback state. `*res_chg` is forced false after internal MV allocation, so clients rely on separate get-param behavior for visible format changes. Errors after capture-buffer acquisition do not explicitly return the buffer in this file. Reference correctness depends on timestamped capture buffers being present.

## Test signals
Run stateless H.264 single-core decode with IDR, P, and B slices, missing controls, missing references, one-plane and two-plane destination formats, initial and changed resolutions, flush reset, and interrupt timeout. Validate metadata propagation from source to destination buffers.
