# subset-b-004142 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_av1_req_lat_if.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_av1_req_lat_if.c

## Purpose
This file implements the MediaTek stateless AV1 decoder interface for LAT/core hardware. It exposes `vdec_av1_slice_lat_if` as a `struct vdec_common_if`, translating V4L2 AV1 controls and source/capture buffers into the firmware-visible VSI layout, managing AV1 reference slots, allocating per-resolution working buffers, and coordinating LAT-to-core decode through `vdec_msg_queue`.

## Important APIs, types, and functions
The central state object is `struct vdec_av1_slice_instance`, which owns the VPU instance, init/core VSIs, global AV1 slot state, CDF/IQ tables copied from firmware, per-slot MV/CDF/segmentation buffers, the tile buffer, and flags such as `inneracing_mode`. `struct vdec_av1_slice_vsi` is the host/firmware contract for bitstream, working buffers, tile metadata, reference frame buffers, current frame syntax, slots, and decode state. `struct vdec_av1_slice_pfc` is the per-frame context passed from LAT to core.

Initialization flows through `vdec_av1_slice_init()`, `vpu_dec_init()`, `vdec_av1_slice_init_cdf_table()`, and `vdec_av1_slice_init_iq_table()`. Decode enters `vdec_av1_slice_lat_decode()`, then `vdec_av1_slice_setup_lat()`, `vpu_dec_start()`, and finally `vdec_av1_slice_core_decode()` via the message queue. Parameter packing is split across helpers such as `vdec_av1_slice_setup_seq()`, `vdec_av1_slice_setup_uh()`, `vdec_av1_slice_setup_gm()`, `vdec_av1_slice_setup_seg()`, `vdec_av1_slice_setup_quant()`, `vdec_av1_slice_setup_lr()`, `vdec_av1_slice_setup_lf()`, `vdec_av1_slice_setup_cdef()`, and `vdec_av1_slice_setup_tile()`.

## Control flow
The LAT path lazily initializes `ctx->msg_queue`, dequeues a LAT buffer, builds a per-frame VSI from V4L2 controls, validates tile group entries, allocates or reuses working buffers for FHD or 4K resolution classes, writes hardware tile descriptors, copies the VSI to remote firmware memory, starts LAT decode, waits for the LAT interrupt if enabled, updates the UBE write pointer, and queues the LAT buffer to the core queue. In inner-racing mode, the LAT buffer is queued to core before LAT completion.

The core path obtains a capture buffer, copies timestamp/request metadata to the destination buffer, fills current and reference DMA addresses by looking up reference timestamps in the capture vb2 queue, copies the VSI to `core_vsi`, runs `vpu_dec_core()`, waits for the core interrupt, updates the UBE read pointer, and calls `cap_to_disp()`.

## State and persistence
AV1 reference persistence lives in `instance->slots`, an array of `AV1_MAX_FRAME_BUF_COUNT` timestamped frame-info slots with reference counts. `vdec_av1_slice_cleanup_slots()` drops slots not referenced by the new frame controls, while `vdec_av1_slice_get_new_slot()` reserves a slot for the current frame. CDF, IQ, MV, segmentation, tile, and temporary CDF buffers persist across frames until deinit or resolution-level change. Flush waits for LAT buffers to return, clears slot frame info, and resets firmware.

## Dependencies and integration points
The file depends on V4L2 stateless AV1 controls, vb2 DMA-contig buffer lookup, MediaTek VPU APIs, codec message queues, firmware memory mapping, interrupt waits, and platform callbacks such as `get_cap_buffer()` and `cap_to_disp()`. It integrates with `GET_PARAM_PIC_INFO`, `GET_PARAM_DPB_SIZE`, and `GET_PARAM_CROP_INFO` from the common decoder interface.

## Risks
Tile group validation is critical because tile offsets and counts directly program hardware descriptors. Reference lookup failures zero the corresponding reference buffer, which avoids invalid DMA but can cause decode errors. `vdec_av1_slice_setup_core_buffer()` assumes a destination buffer is available after `next_dst_buf()` metadata handling. Slot fallback to zero after allocation failure prevents a crash but risks corrupt reference state. Buffer-full handling returns either `0`, `-EBUSY`, or retries depending on UBE space, so regressions can deadlock the LAT/core queue.

## Test signals
Useful tests include stateless AV1 conformance streams with key/inter/intra-only frames, tile counts at max limits, malformed tile group entries, dynamic resolution changes, reference reuse/drop patterns, single-plane and two-plane capture formats, LAT buffer-full stress, flush during queued LAT work, and IRQ timeout paths. Debug CRC logs from LAT and core provide hardware result signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_av1_req_lat_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_h264_if.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_h264_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_h264_req_common.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_h264_req_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_h264_req_common.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_h264_req_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_h264_req_if.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_h264_req_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_h264_req_multi_if.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_h264_req_multi_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_hevc_req_multi_if.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_hevc_req_multi_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_vp8_if.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_vp8_if.c

## Purpose
This file implements the older stateful VP8 decoder interface `vdec_vp8_if`. It manages a VPU VSI, hardware register-table save/restore, segmentation state, a working buffer, and software frame-buffer lists for display/free/reference lifecycle.

## Important APIs, types, and functions
`struct vdec_vp8_inst` owns the current frame buffer, list nodes, use/free/display/available lists, working buffer, hardware register bases, context, VPU instance, and VSI. The VSI carries decode DMA addresses, picture info, decoder probability table, segmentation data, and a `load_data` flag. Register helpers include `get_hw_reg_base()`, `write_hw_segmentation_data()`, `read_hw_segmentation_data()`, `enable_hw_rw_function()`, `store_dec_table()`, and `load_dec_table()`. `vdec_vp8_decode()` is the main decode path.

## Control flow
Init creates the instance, initializes firmware with `IPI_VDEC_VP8`, initializes frame-buffer lists, allocates a fixed working buffer, and records hardware register bases. Decode reset on `bs == NULL` moves all in-use buffers to free and resets firmware. Normal decode writes current bitstream and output DMAs to the VSI, restores segmentation and decoder tables into hardware, extracts width/height header bits for VPU start, handles VPU-reported wait-key-frame and resolution-change states, waits for hardware completion, reloads decoder tables if requested, updates frame-buffer lists in `vp8_dec_finish()`, reads segmentation back, and ends VPU decode.

## State and persistence
VP8 probability and segmentation state persist across frames in `vsi->dec_table` and `vsi->segment_buf`. Frame buffers move among available, use, free, and display lists. The working buffer persists for the instance lifetime.

## Dependencies and integration points
This path depends on direct MMIO register access, MediaTek VPU APIs, interrupt waits, MediaTek memory helpers, and common frame-buffer status flags. It supports display/free frame retrieval, picture info, crop info, and fixed DPB size 4 through `get_param`.

## Risks
The list logic assumes an available node exists when adding buffers. Direct register programming is platform-sensitive and has duplicate `VP8_WO_VLD_SRST` defines. Decode does not check the return from `mtk_vcodec_wait_for_done_ctx()`. Header byte reads assume the bitstream has at least 10 bytes. Resolution-change returns the submitted frame to free without ending decode.

## Test signals
Stateful VP8 playback should verify key-frame wait behavior, inter-frame segmentation persistence, probability table save/load, resolution change, flush, display/free list cycling, short malformed bitstreams, and interrupt timeout behavior on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_vp8_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_vp8_req_if.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_vp8_req_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_vp9_if.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_vp9_if.c

## Purpose
This file implements the older stateful VP9 decoder interface `vdec_vp9_if`. It manages VP9 reference-counted frame buffers, super-frame sub-frame handling, segmentation and MV working buffers, VPU-provided reference maps, and display/free buffer lists.

## Important APIs, types, and functions
`struct vdec_vp9_inst` owns MV and segmentation buffers, frame-buffer list nodes, current buffer, VPU instance, VSI, total frame count, and DMA-backed instance memory. `struct vdec_vp9_vsi` is the shared VPU contract containing super-frame metadata, current bitstream/output buffer copies, picture and compressed buffer sizes, show-frame flags, reference maps, frame buffers, current refs, and working buffer descriptors. `vp9_alloc_work_buf()` sizes and allocates MV/segmentation buffers after resolution changes. `vp9_ref_cnt_fb()`, `vp9_swap_frm_bufs()`, and list helpers maintain references and display/free queues. `vdec_vp9_decode()` drives super-frame and normal decode loops.

## Control flow
Init allocates the instance through `mtk_vcodec_mem_alloc()`, initializes `IPI_VDEC_VP9`, sets `show_frame BIT(3)` to ask firmware to manage show bits, and initializes buffer lists. Decode handles EOS by resetting. For each frame or sub-frame, it copies the bitstream and optional output frame into the VSI, preserves or copies super-frame payload sections, clears segmentation state unless firmware asks to preserve it, starts VPU parsing/decode, optionally triggers hardware, validates VPU-provided indexes, allocates work buffers on resolution change, selects either caller output or internal super-frame reference output, records the new frame buffer, rewires VPU frame-ref pointers to AP addresses, handles show-existing-frame by reference-count remap, and completes decode through `vp9_decode_end_proc()`.

## State and persistence
Reference persistence is explicit: `frm_bufs` have reference counts, `ref_frm_map` maps VP9 reference slots, super-frame scratch buffers are allocated and reused, and software lists track use/free/display states. Reset moves all use-list buffers to free, frees super-frame refs, reinitializes the next super-frame reference buffer, resets VPU, and restores MV/seg buffer addresses into the VSI.

## Dependencies and integration points
The file depends on VPU APIs, MediaTek memory allocation, interrupt status, common list-based `vdec_fb_node` management, and the common decoder interface. It returns display/free buffers, picture info, fixed DPB size 9, and crop info via `get_param`.

## Risks
Many indexes are firmware-provided; `validate_vsi_array_indexes()` guards `sf_frm_idx`, `frm_to_show_idx`, and `new_fb_idx`, but other indices such as `frm_refs[i].idx` also need firmware correctness. Super-frame reference allocation failure returns `-1`, but later code may use the index if not checked at every call site. Show-existing-frame copies frame memory in software and depends on destination size checks. Bitstream header reads assume at least 12 bytes. Error cleanup returns only the submitted `fb` to free, not necessarily internal super-frame buffers.

## Test signals
Test VP9 key/inter streams, show-existing-frame, super-frames with multiple sub-frames, resolution changes across super-frames, invalid VPU indexes, segmentation reset/preserve flags, reference-count churn, EOS reset, display/free list draining, and timeout paths. Memory tests should cover repeated resolution changes and super-frame scratch allocation/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_vp9_if.c -->
