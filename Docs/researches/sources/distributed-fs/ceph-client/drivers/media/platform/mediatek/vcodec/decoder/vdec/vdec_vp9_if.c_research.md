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
