# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g1_h264_dec.c

## Purpose
Programs G1 decoder registers for stateless H.264 frame or field decode.

## Important APIs, Types, And Functions
The exported entry point is `hantro_g1_h264_dec_run`. Internal helpers `set_params`, `set_ref`, and `set_buffers` map V4L2 H.264 SPS/PPS/decode controls, prepared DPB state, reference lists, bitstream DMA, destination DMA, DMV buffer offset, and auxiliary table DMA into the G1 register file.

## Control Flow And State
`hantro_g1_h264_dec_run` first calls `hantro_h264_dec_prepare_run`, which latches request controls and builds DPB/reference-list state in `ctx->h264_dec`. It then writes decoder control registers for profile, interlace/field mode, picture size, QP offsets, stream length, CABAC/scaling flags, reference counts, reference picture numbers, list indexes, and DPB DMA addresses. After `hantro_end_prepare_run`, it programs common config and enables decode interrupt/start.

## Dependencies And Integration Points
Depends on the shared H.264 helper in `hantro_h264.c`, G1 register macros, V4L2 H.264 stateless controls, VB2 DMA addresses, and core postproc-aware `hantro_get_dec_buf_addr`.

## Risks And Test Signals
Reference-list packing assumes 16 entries and directly indexes arrays in fixed groups. Field decoding adjusts destination and DMV offsets; conformance tests should include MBAFF, bottom fields, long-term refs, monochrome high profile, scaling matrices, and missing/inactive DPB entries. Buffer sizing must account for appended motion-vector data for high-profile reference frames.
