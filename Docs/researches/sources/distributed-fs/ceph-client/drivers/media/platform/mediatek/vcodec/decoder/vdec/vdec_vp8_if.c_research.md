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
