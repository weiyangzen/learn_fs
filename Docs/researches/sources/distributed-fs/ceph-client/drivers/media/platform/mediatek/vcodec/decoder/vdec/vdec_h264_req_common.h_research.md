# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_h264_req_common.h

## Purpose
This header defines the shared firmware-facing H.264 request structures, constants, and helper prototypes consumed by MediaTek stateless H.264 decoder implementations. It is the ABI-like bridge between V4L2 H.264 controls and the layout expected by MediaTek VPU/SCP firmware.

## Important APIs, types, and functions
Key constants include NAL type helpers, `BUF_PREDICTION_SZ`, `MB_UNIT_LEN`, `HW_MB_STORE_SZ`, and `H264_MAX_MV_NUM`. Firmware structures include `mtk_h264_dpb_info`, `mtk_h264_sps_param`, `mtk_h264_pps_param`, `mtk_h264_slice_hd_param`, `slice_api_h264_scaling_matrix`, `slice_h264_dpb_entry`, `slice_api_h264_decode_param`, and `h264_fb`. The prototypes cover reference-list conversion, control lookup, DPB DMA filling, SPS/PPS/slice/scaling/decode parameter copy, DPB update, start-code detection, and MV-buffer sizing.

## Control flow and integration
Request decoders include this header before building per-frame VSIs. The V4L2 controls are copied into these narrower structs, then the structs are embedded in single-core and LAT/core VSIs. Firmware consumes these layouts directly through shared memory.

## State and persistence
The header defines data containers rather than owning state. Persistence is imposed by embedding these structs in decoder instances, per-frame share-info structures, and firmware VSIs. Layout stability matters because these structs cross the AP/firmware boundary.

## Dependencies and integration points
The header includes Linux module/slab headers, V4L2 H.264 controls, V4L2 mem2mem, vb2 DMA-contig, and `mtk_vcodec_dec_drv.h`. It integrates tightly with `vdec_h264_req_common.c`, `vdec_h264_req_if.c`, and `vdec_h264_req_multi_if.c`.

## Risks
Any field reorder, type-width change, or constant change can break firmware interpretation. Some documentation comments contain typos, but the main risk is ABI drift against firmware. `slice_api_h264_decode_param` carries fixed 32-entry reference lists and assumes firmware's unused-entry sentinel of `0x20` through the helper implementation.

## Test signals
Build coverage should catch declaration mismatch. Runtime validation comes from stateless H.264 streams that exercise all copied SPS/PPS flags, scaling matrices, reference lists, long-term DPB entries, one-plane chroma address derivation, and MV-buffer reallocation.
