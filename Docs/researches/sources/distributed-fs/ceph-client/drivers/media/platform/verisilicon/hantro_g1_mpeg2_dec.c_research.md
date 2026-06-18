# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g1_mpeg2_dec.c

## Purpose
Programs G1 decoder registers for stateless MPEG-2 decode.

## Important APIs, Types, And Functions
`hantro_g1_mpeg2_dec_run` is the backend entry point. `hantro_g1_mpeg2_dec_set_quantisation` copies the V4L2 quantisation control into the coherent hardware qtable buffer. `hantro_g1_mpeg2_dec_set_buffers` chooses forward/backward/current reference addresses and writes stream, output, reference, and qtable base registers.

## Control Flow And State
The run path applies request controls, fetches sequence and picture controls, writes G1 decode config, picture type/interlace/field flags, macroblock dimensions, MPEG-2 syntax options, stream length, f-code values, error-concealment start MB, APF threshold, quant table DMA, and buffer addresses. Missing forward/backward references fall back to the current destination buffer to keep hardware inputs valid.

## Dependencies And Integration Points
Integrates with `hantro_mpeg2_dec_copy_qtable` and `ctx->mpeg2_dec.qtable` allocation from `hantro_mpeg2.c`, plus core timestamp reference lookup through `hantro_get_ref`.

## Risks And Test Signals
Field-picture reference selection is branchy and depends on `TOP_FIELD_FIRST`; tests should cover I/P/B frames, top/bottom fields, progressive/interlaced sequences, alternate scan, concealment motion vectors, and absent reference timestamps. Stream payload length is masked to 24 bits by macros, so oversized inputs rely on higher-level format constraints.
