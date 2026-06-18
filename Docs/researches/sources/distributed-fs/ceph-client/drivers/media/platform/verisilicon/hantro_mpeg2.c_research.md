# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_mpeg2.c

## Purpose
Provides shared MPEG-2 decoder auxiliary quantization-table handling.

## Important APIs, Types, And Functions
Exports `hantro_mpeg2_dec_copy_qtable`, `hantro_mpeg2_dec_init`, and `hantro_mpeg2_dec_exit`. The file includes a MPEG-style zigzag permutation table used to place four 64-entry quantizer matrices into hardware memory.

## Control Flow And State
Initialization allocates a coherent 256-byte qtable buffer in `ctx->mpeg2_dec.qtable`. Each run-side caller copies intra, non-intra, chroma-intra, and chroma-non-intra matrices from the V4L2 quantisation control into zigzag-addressed regions. Exit frees the coherent buffer.

## Dependencies And Integration Points
Used by G1 and Rockchip VPU2 MPEG-2 runners. Depends on V4L2 MPEG-2 stateless quantisation controls and DMA coherent allocation through `ctx->dev`.

## Risks And Test Signals
`hantro_mpeg2_dec_copy_qtable` silently returns if buffer or control is null, so caller-side control validation is important. Tests should cover default and custom quant matrices, all four matrix regions, init allocation failure, and decode conformance with alternate scan streams.
