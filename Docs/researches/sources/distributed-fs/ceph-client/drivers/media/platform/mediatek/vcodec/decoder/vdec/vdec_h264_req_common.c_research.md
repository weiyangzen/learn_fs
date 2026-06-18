# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_h264_req_common.c

## Purpose
This file provides shared H.264 request-API helpers used by the single-core and multi-core stateless H.264 decoders. It translates V4L2 H.264 controls into compact MediaTek firmware structures, resolves reference frame DMA addresses from timestamped DPB entries, maintains a stable DPB array, and provides common start-code and MV-buffer sizing helpers.

## Important APIs, types, and functions
`mtk_vdec_h264_get_ctrl_ptr()` fetches a stateless control payload from the context. `mtk_vdec_h264_get_ref_list()` converts V4L2 reference lists to firmware indices and fills unused entries with `0x20`. `mtk_vdec_h264_fill_dpb_info()` maps active DPB entries to capture vb2 buffers and writes Y/C DMA addresses and short/long reference flags. The `copy_*` helpers pack SPS, PPS, slice header, scaling matrix, and decode params into MediaTek structs. `mtk_vdec_h264_update_dpb()` adapts the Hantro DPB update strategy to keep existing slots stable by matching top and bottom POC values. `mtk_vdec_h264_find_start_code()` recognizes 3-byte and 4-byte Annex B start codes.

## Control flow
Request decoders call these helpers before firmware start. Decode params update the instance DPB, SPS/PPS/scaling controls are copied field-by-field, reference lists are generated with kernel V4L2 helpers, and `fill_dpb_info()` looks up the referenced capture buffers using `reference_ts`. For one-plane output formats, chroma DMA is derived as luma plus `ctx->picinfo.fb_sz[0]`.

## State and persistence
This file itself is stateless, but it mutates caller-provided DPB arrays and firmware parameter structs. DPB update first clears active bits in the target array, matches new active entries to existing slots by POC, then places unmatched entries in unused slots.

## Dependencies and integration points
It depends on `<media/v4l2-h264.h>`, V4L2 mem2mem queues, vb2 DMA-contig, and MediaTek decoder context format metadata. It is included by `vdec_h264_req_if.c` and `vdec_h264_req_multi_if.c`.

## Risks
DPB matching by POC ignores timestamps when preserving slots, so unusual streams with repeated POC patterns could stress reference stability. `fill_dpb_info()` logs missing references but continues, leaving the corresponding output entry unchanged except for inactive entries. Field decoding is explicitly not handled in ref-list generation. Start-code detection only checks the beginning of the buffer.

## Test signals
Stateless H.264 tests should cover P/B slices, long-term references, missing reference timestamps, one-plane versus two-plane output formats, DPB reorder and replacement, scaling matrices, and invalid start-code buffers. Field-coded streams should remain rejected or unsupported in callers.
