# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu2_hw_mpeg2_dec.c

## Purpose
Programs one Rockchip VDPU2 stateless MPEG-2 decode job. It maps V4L2 MPEG-2 sequence, picture, and quantisation controls into VDPU registers and configures current, forward, and backward frame buffers.

## Important APIs, Types, And Functions
- Exports `rockchip_vpu2_mpeg2_dec_run(struct hantro_ctx *ctx)`.
- `rockchip_vpu2_mpeg2_dec_set_quantisation()` copies quant matrices into the context qtable DMA buffer.
- `rockchip_vpu2_mpeg2_dec_set_buffers()` resolves reference timestamps with `hantro_get_ref()`, writes stream/output addresses, and programs field-aware reference base registers.

## Control Flow
The run path starts prepare, reads MPEG-2 controls, writes latency/stream length/mode/endian/AXI/interlace/picture-type registers, writes macroblock dimensions and scan/DCT/f-code flags, copies quantization data, writes bitstream and output addresses, maps forward/backward references based on I/P/B picture type, handles top/bottom-field current-reference substitution, ends prepare, and sets the VDPU decode enable bit.

## State And Persistence
No persistent storage is used. The MPEG-2 context owns a coherent qtable buffer initialized elsewhere and updated per job. Reference state comes from vb2 timestamps and Hantro decoded-buffer tracking.

## Dependencies And Integration Points
Used through Rockchip VDPU2 codec ops in `rockchip_vpu_hw.c`. It depends on V4L2 stateless MPEG-2 controls, Hantro core buffer/reference helpers, DMA-contig memory, and the common Rockchip VDPU2 interrupt/reset paths.

## Risks And Edge Cases
Field-coded pictures are the main risk: output start addresses and forward-reference top/bottom pairing depend on `picture_structure` and `TOP_FIELD` flags. Missing references intentionally fall back to the current frame, which avoids null DMA programming but may conceal userspace reference mistakes as visible decode corruption.

## Test Signals
Run I/P/B pictures, progressive and interlaced streams, top-first and bottom-field sequences, alternate scan, concealment motion vectors, and custom quant matrices. Validate output CRCs and check that missing-reference debug paths do not appear in normal playback.
