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
