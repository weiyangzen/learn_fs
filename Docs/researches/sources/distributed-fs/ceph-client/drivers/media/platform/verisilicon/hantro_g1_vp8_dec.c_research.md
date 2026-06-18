# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g1_vp8_dec.c

## Purpose
Programs G1 decoder registers and auxiliary buffers for stateless VP8 decode.

## Important APIs, Types, And Functions
`hantro_g1_vp8_dec_run` is the entry point. Helpers configure loop filter levels and deltas (`cfg_lf`), quantizer and segment deltas (`cfg_qp`), control/DCT partition addresses and start bits (`cfg_parts`), interpolation taps (`cfg_tap`), reference buffers (`cfg_ref`), segment/probability/output buffers (`cfg_buffers`).

## Control Flow And State
The run path applies request controls, clears the segment map on keyframes, updates VP8 probability tables through `hantro_vp8_prob_update`, writes common config and VP8 mode registers, configures dimensions and boolean decoder state, then derives aligned macroblock and DCT partition locations from userspace-provided frame control fields. It writes last/golden/alt reference addresses by timestamp, with fallback to destination when references are absent.

## Dependencies And Integration Points
Depends on V4L2 VP8 stateless frame controls, `ctx->vp8_dec.segment_map`, `ctx->vp8_dec.prob_tbl`, G1 register maps, shared MC filter table `hantro_vp8_dec_mc_filter`, and VB2 DMA-contig buffers.

## Risks And Test Signals
Partition arithmetic is sensitive to byte/bit alignment, keyframe header length, number of DCT partitions, and buffer payload correctness. Segmentation and loop-filter delta paths need regression coverage. Test vectors should include keyframes, interframes with missing refs, 1/2/4/8 DCT partitions, segmentation map updates, simple vs normal loop filters, and all interpolation versions.
