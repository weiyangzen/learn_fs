# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g2_vp9_dec.c

## Purpose
Implements G2 VP9 stateless decode, including register programming, probability-table upload, segmentation state, tile metadata, reference scaling, source alignment, and post-decode probability adaptation from hardware counters.

## Important APIs, Types, And Functions
Exports `hantro_g2_vp9_dec_run` and `hantro_g2_vp9_dec_done`. Major helpers include `start_prepare_run`, `get_ref_buf`, `config_output`, `config_ref_registers`, `config_tiles`, `config_segment`, `config_loop_filter`, `config_picture_dimensions`, `config_bit_depth`, `config_quant`, `config_others`, `config_compound_reference`, `config_probs`, `config_counts`, `config_seg_map`, and `config_source`.

## Control Flow And State
Preparation latches VP9 frame and compressed-header controls, resets/loads frame context state, and applies firmware-style probability updates. Register config updates the destination metadata, chooses a motion-vector reference, writes G2 VP9 mode/swap/burst settings, output and reference addresses/scales/sign biases, tile info, segmentation features, loop filter, dimensions, bit depth, quant deltas, temporal MVP/write-MV flags, compound reference registers, probability table DMA, counter DMA, segment map ping-pong addresses, and aligned stream start/length. Completion optionally adapts coefficient and non-coefficient probabilities from hardware counters and stores the refreshed frame context, then updates `last`.

## Dependencies And Integration Points
Uses V4L2 VP9 helpers, `hantro_vp9.h` probability layouts, G2 register descriptors, VB2 timestamp lookup, per-buffer `hantro_decoded_buffer.vp9` metadata, and core codec `done` callback dispatch.

## Risks And Test Signals
Stateful VP9 behavior is complex: frame contexts, segmentation feature data, active segment map, tile geometry caches, reference dimensions, and last-frame state must survive across jobs. Test signals include keyframe reset, intra-only, error-resilient, parallel decode, frame-context refresh, resolution change, segmentation update/no-update, missing refs, legacy/non-legacy registers, tiled frames, and probability adaptation conformance.
