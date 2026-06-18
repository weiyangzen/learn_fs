# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_vp8.c

## Purpose
`hantro_vp8.c` provides VP8 decoder support data and context allocation for the Hantro G1 path. It packs V4L2 VP8 entropy probabilities into the hardware layout, exposes the VP8 motion compensation filter taps, and allocates/frees per-context DMA buffers for the segment map and probability table.

## Important APIs, Types, And Functions
`struct vp8_prob_tbl_packed` describes the hardware probability table layout. `hantro_vp8_dec_mc_filter` exports the 8-by-6 interpolation filter coefficients. `hantro_vp8_prob_update` copies fields from `struct v4l2_ctrl_vp8_frame` into the packed probability DMA buffer. `hantro_vp8_dec_init` allocates the segment map and probability table buffers, and `hantro_vp8_dec_exit` releases them.

## Control Flow
Codec init computes macroblock dimensions from `ctx->dst_fmt`, rounds the segment map size to hardware alignment, allocates coherent DMA for the segment map, then allocates coherent DMA for the packed probability table. On allocation failure it unwinds the already allocated segment map. Before a frame is run, `hantro_vp8_prob_update` writes skip, intra, reference, segment, luma/chroma mode, motion-vector, and coefficient probabilities into fixed byte offsets in `ctx->vp8_dec.prob_tbl.cpu`.

## State And Persistence
State is per decoder context in `ctx->vp8_dec.segment_map` and `ctx->vp8_dec.prob_tbl`. Both are coherent DMA buffers used by hardware and are valid only between codec init and exit. Probability contents are refreshed from frame controls; segment map contents are initialized by coherent allocation and used across VP8 frame processing as hardware scratch/reference state.

## Dependencies And Integration Points
The file depends on `hantro.h`, V4L2 VP8 frame control definitions, Linux DMA coherent allocation, and constants such as `V4L2_VP8_MV_PROB_CNT` and `V4L2_VP8_COEFF_PROB_CNT`. It is referenced by variant codec ops, including i.MX8M G1 VP8 decode entries, and by G1 VP8 register programming code that consumes the DMA addresses.

## Risks
The packed probability layout is offset-sensitive and has explicit padding; any mismatch with hardware register expectations will produce decode corruption rather than obvious build failures. The segment map sizing depends on macroblock dimensions and 64-byte alignment. Exit assumes buffers were allocated by init; changes to partial-init behavior must preserve safe unwind and free semantics.

## Test Signals
Signals include VP8 decode conformance streams with segmentation enabled, streams that update entropy probabilities, DMA mapping diagnostics, and memory-leak/error-unwind tests around codec init failures.
