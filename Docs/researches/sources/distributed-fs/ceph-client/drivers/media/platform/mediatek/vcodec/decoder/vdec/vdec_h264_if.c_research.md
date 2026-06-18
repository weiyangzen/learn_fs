# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_h264_if.c

## Purpose
This file implements the older stateful MediaTek H.264 decoder interface exported as `vdec_h264_if`. It parses Annex B start codes, passes NAL metadata and DMA addresses to VPU firmware, manages VPU-owned display/free ring lists, allocates prediction and motion-vector working buffers, and reports picture, crop, DPB, display, and free-buffer state through the common decoder API.

## Important APIs, types, and functions
`struct vdec_h264_inst` owns the context, VPU instance, prediction buffer, MV buffers, and `struct vdec_h264_vsi`. The VSI includes an AP-written PPS/header buffer, prediction/MV DMA addresses, VPU-written decode information, picture/crop information, and two `h264_ring_fb_list` rings. `vdec_h264_init()` initializes firmware with `IPI_VDEC_H264`, maps the VSI, and allocates the prediction buffer. `vdec_h264_decode()` handles reset on `bs == NULL`, finds the NAL start code, copies PPS bytes into `hdr_buf`, starts the VPU, waits for slice decode interrupts, and handles resolution-change MV allocation. `vdec_h264_get_fb()` drains display/free rings.

## Control flow
For non-flush decode, the AP writes bitstream, output frame DMA addresses, and the `vdec_fb` pointer into `vsi->dec`, then calls `vpu_dec_start()` with the input size and NAL header byte. PPS NALs are copied into a fixed 1024-byte parsing buffer before VPU start. On resolution change, the driver reads `vsi->pic` and allocates one MV buffer per possible frame buffer when firmware requests reallocation. Slice NALs wait on `MTK_INST_IRQ_RECEIVED` and finish with `vpu_dec_end()`. Errors push the submitted frame back to the free ring.

## State and persistence
Persistent state includes `num_nalu`, the prediction buffer, up to 17 MV buffers, VPU ring lists, and the VPU-maintained picture/crop/decode fields. Ring-list validity is checked before use, but list contents are trusted to be firmware-produced `vdec_fb` virtual addresses.

## Dependencies and integration points
This path depends on `vdec_vpu_if`, `mtk_vcodec_mem_alloc/free`, interrupt wait helpers, `vdec_drv_if`, and MediaTek decoder context structures. It integrates with stateful frame-buffer lifecycle through `GET_PARAM_DISP_FRAME_BUFFER` and `GET_PARAM_FREE_FRAME_BUFFER`.

## Risks
The fixed PPS parsing buffer rejects large PPS payloads with `-EILSEQ`. Ring-list corruption from firmware can drop buffers or return invalid `vdec_fb` pointers, although count/index validation reduces the blast radius. MV buffer allocation can leak partially allocated buffers until deinit if a later allocation in the loop fails. Decode only waits for non-IDR/IDR slices, so unusual NAL sequencing relies on firmware behavior.

## Test signals
Exercise PPS-only and slice NALs, invalid start codes, large PPS rejection, resolution changes that toggle MV reallocation, IRQ timeout, firmware error code `H264_ERR_NOT_VALID`, and display/free ring draining. Stateful H.264 playback with reorder-heavy streams should verify buffer status transitions.
