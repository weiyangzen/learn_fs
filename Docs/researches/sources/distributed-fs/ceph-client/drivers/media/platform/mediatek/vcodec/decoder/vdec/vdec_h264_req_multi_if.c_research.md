# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_h264_req_multi_if.c

## Purpose
This file implements the multi-core and pure-single-core stateless H.264 request decoder interface `vdec_h264_slice_multi_if`. It supports both legacy and extended VSI layouts, LAT/core split decode through `vdec_msg_queue`, inner-racing operation, and single-core fallback selected by hardware architecture and capability flags.

## Important APIs, types, and functions
`struct vdec_h264_slice_inst` holds the VPU LAT/core IDs, either normal or extended LAT/core VSI pointers, per-instance MV buffers, DPB, field-bitstream rejection state, resolution flags, and a selected decode function pointer. Decode parameter preparation is split into `vdec_h264_slice_fill_decode_parameters()` for LAT setup, `vdec_h264_slice_fill_decode_reflist()` for core-time DPB/reference list updates, and `get_vdec_sig_decode_parameters()` for single-core. LAT paths are `vdec_h264_slice_lat_decode()` and `_ext()`. Core callbacks are `vdec_h264_slice_core_decode()` and `_ext()`. Single-core paths are `vdec_h264_slice_single_decode()` and `_ext()`.

## Control flow
Init uses `SCP_IPI_VDEC_LAT` and `SCP_IPI_VDEC_CORE`, records codec/capture type, splits the firmware VSI memory into LAT and core regions, selects normal versus extended layouts, then selects LAT/core or pure-single-core decode. LAT decode initializes the message queue, handles flush by waiting for LAT buffers and resetting firmware, dequeues a LAT buffer, copies source request/metadata, rejects field pictures, optionally appends a small CAVLC start-code workaround for MT8192/MT8195, allocates MV buffers on resolution change, fills LAT buffer addresses, starts firmware, updates the UBE write pointer, and queues work to core. Core decode gets the capture buffer, writes output and shared LAT buffer addresses, rebuilds DPB/ref lists from shared controls, runs `vpu_dec_core()`, updates the UBE read pointer, and calls `cap_to_disp()`.

## State and persistence
Persistent state includes DPB entries, MV buffers, resolution/reallocation flags, `is_field_bitstream`, selected decode function, and message-queue state. Per-frame shared info carries SPS/decode controls, firmware parameters, trans start/end, and NAL info from LAT to core.

## Dependencies and integration points
The file depends on common H.264 request helpers, V4L2 controls and mem2mem metadata, vb2 DMA-contig, device-tree compatible checks for the CAVLC workaround, VPU LAT/core APIs, interrupt waits, and platform callbacks. It reports picture info, a fixed DPB size of 6, and crop as full picture dimensions.

## Risks
Field decoding is explicitly unsupported and permanently marks the instance as rejecting subsequent frames after a field bitstream is seen. LAT buffer-full errors must return buffers to the correct queue depending on inner-racing mode. Extended and non-extended VSIs duplicate logic and can drift. The MT8192/MT8195 start-code workaround mutates the source buffer and increases `bs->size`, so callers must provide writable tailroom.

## Test signals
Cover normal and extended VSI platforms, pure-single-core and LAT/core architectures, inner-racing on/off, CAVLC small-frame workaround devices, field-picture rejection, trans/slice-header-full firmware returns, missing capture buffers, resolution changes with MV reallocation, and P/B reference reconstruction in core.
