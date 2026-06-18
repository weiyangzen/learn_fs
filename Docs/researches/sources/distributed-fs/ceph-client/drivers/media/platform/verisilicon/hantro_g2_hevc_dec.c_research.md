# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g2_hevc_dec.c

## Purpose
Programs G2 decoder registers, reference address tables, tile metadata, scaling lists, stream buffer, and postprocessed/compressed output settings for stateless HEVC decode.

## Important APIs, Types, And Functions
The exported entry is `hantro_g2_hevc_dec_run`. Helpers include `prepare_tile_info_buffer`, `compute_header_skip_length`, `set_params`, `set_ref_pic_list`, `set_ref`, `set_buffers`, and `prepare_scaling_list_buffer`.

## Control Flow And State
The run path calls `hantro_hevc_dec_prepare_run`, writes SPS/PPS/decode-derived bit depths, coding-block sizes, picture dimensions, transform hierarchy, deblocking/SAO/PCM/tiles/list flags, reference list indexes, POC deltas, long-term bitmaps, current and reference luma/chroma/MV/compression addresses, stream length and tile buffer addresses, tile-size memory, and scaling lists. It then enables HEVC mode, clock gating, output, optional reference compression, bus width, swaps, and decode start.

## Dependencies And Integration Points
Relies on `hantro_hevc.c` for control latching, tile buffer allocation, reference POC-to-DMA tracking, and compression policy. Uses G2 register descriptors from `hantro_g2_regs.h`, VB2 DMA buffers, and V4L2 HEVC stateless controls.

## Risks And Test Signals
`set_ref` returns errors if referenced POCs are not known, so DPB control correctness is critical. Tile memory layout and scaling-list ordering are hardware-specific. Tests should cover IDR and non-IDR frames, long-term refs, missing refs, tiles with uniform and explicit spacing, PCM, SAO/deblock flags, 8/10-bit streams, NV12_4L4 validation, and compression enabled/disabled.
