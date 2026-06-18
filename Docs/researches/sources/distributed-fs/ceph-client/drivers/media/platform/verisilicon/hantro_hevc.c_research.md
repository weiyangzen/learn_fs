# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_hevc.c

## Purpose
Manages HEVC decoder per-context auxiliary buffers, tile-buffer reallocation, control latching, SPS validation, reference-buffer tracking by POC, and reference-compression policy.

## Important APIs, Types, And Functions
Exports `hantro_hevc_dec_init`, `hantro_hevc_dec_exit`, `hantro_hevc_dec_prepare_run`, `hantro_hevc_ref_init`, `hantro_hevc_get_ref_buf`, and `hantro_hevc_add_ref_buf`. Internal helpers include `tile_buffer_reallocate` and `hantro_hevc_validate_sps`.

## Control Flow And State
Initialization zeroes the HEVC context, allocates tile-size and scaling-list buffers, resets reference tracking, and sets `use_compression` from the module parameter and postproc need. Prepare run applies request controls, fetches decode/scaling/SPS/PPS controls, validates tiled output format dimensions, and reallocates tile edge/filter/SAO/BSD buffers when PPS tile columns exceed prior allocation. Reference tracking uses `ref_bufs_poc`, `ref_bufs`, and `ref_bufs_used` to map POC values to DMA addresses across frames.

## Dependencies And Integration Points
Consumed by `hantro_g2_hevc_dec.c`, relies on V4L2 HEVC stateless controls, DMA coherent allocation, negotiated `ctx->bit_depth`, postprocessor decisions, and the optional `CONFIG_VIDEO_HANTRO_HEVC_RFC`.

## Risks And Test Signals
On init failure after tile-size allocation, scaling-list allocation failure currently returns without freeing the first buffer until context cleanup paths run. Tile reallocation frees old buffers before fully allocating replacements, so allocation failure can degrade later decode until retried. Tests should cover changing tile column counts, NV12_4L4 dimension validation, compression on/off, ref POC reuse/eviction, and 8/10-bit streams.
