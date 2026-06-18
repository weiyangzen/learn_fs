# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu2_hw_vp8_dec.c

## Purpose
Implements Rockchip VDPU2 VP8 stateless frame decode setup. It converts the V4L2 VP8 frame control into loop-filter, quantizer, partition, reference, probability-table, segment-map, and start registers.

## Important APIs, Types, And Functions
- Exports `rockchip_vpu2_vp8_dec_run(struct hantro_ctx *ctx)`.
- Register descriptor tables (`vp8_dec_lf_level`, `vp8_dec_quant`, `vp8_dec_dct_base`, `vp8_dec_pred_bc_tap`, etc.) drive compact `hantro_reg_write()` programming.
- Helpers `cfg_lf()`, `cfg_qp()`, `cfg_parts()`, `cfg_tap()`, `cfg_ref()`, and `cfg_buffers()` split the hardware setup by VP8 syntax area.

## Control Flow
The run path starts prepare, fetches `V4L2_CID_STATELESS_VP8_FRAME`, clears the segment map on key frames, updates probability tables, soft-resets the codec to avoid multi-instance state leakage, writes core decode/endian/AXI/mode flags, programs skip/filter disable flags, writes macroblock dimensions and boolean decoder state, sets VP8 version filter flags, configures loop filters and quantizers with segmentation handling, computes control/DCT partition aligned base addresses and start bits from source DMA, writes normal 6-tap filters when needed, resolves last/golden/alt references, writes probability/segment/output buffers, ends prepare, and starts decode.

## State And Persistence
Per-context VP8 probability and segment-map DMA buffers persist across jobs. Key frames reset the segment map. Reference resolution is timestamp-based through the Hantro decoded-buffer pool. Hardware register state is per job.

## Dependencies And Integration Points
Integrated by `rk3399_vpu_codec_ops` and other VDPU2 Rockchip variants. It depends on V4L2 VP8 stateless controls, `hantro_vp8_prob_update()`, Hantro reference tracking, and the codec reset callback from the active variant.

## Risks And Edge Cases
Partition offset arithmetic is alignment-sensitive and depends on correct userspace control values. Missing golden/alt/last references fall back to the current destination while logging debug messages. The explicit soft reset is required for multi-instance corruption avoidance, so variant reset correctness matters.

## Test Signals
Test key/inter frames, segmentation modes, loop-filter deltas, all DCT partition counts, version-dependent bilinear/tap behavior, missing-reference handling, and multi-context concurrent decode. Good signals are stable CRCs and no cross-stream corruption after repeated soft resets.
