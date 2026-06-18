# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_h264.c

## Purpose
Maintains H.264 decoder auxiliary memory and per-context DPB/reference-list state shared by H.264 hardware backends.

## Important APIs, Types, And Functions
Exports `hantro_h264_dec_init`, `hantro_h264_dec_exit`, `hantro_h264_dec_prepare_run`, `hantro_h264_get_ref_buf`, and `hantro_h264_get_ref_nbr`. Internal helpers assemble scaling lists, prepare CABAC/POC/scaling auxiliary table data, update the persistent DPB, and deduplicate field reference lists.

## Control Flow And State
Initialization allocates a coherent private table and copies the static CABAC initialization table. Each prepare run applies request controls, validates required controls are present, updates the context DPB by matching V4L2 DPB entries by `reference_ts`, computes valid and long-term bitmaps, stores current POC fields, copies scaling matrices if present, builds P and B reference lists with V4L2 helpers, and deduplicates field references to hardware-sized lists.

## Dependencies And Integration Points
Uses V4L2 H.264 stateless controls and reflist builder helpers, VB2 timestamp-based reference lookup through `hantro_get_ref`, postprocessor-aware decoded-buffer addresses, and the G1 H.264 runner that consumes prepared fields and auxiliary DMA.

## Risks And Test Signals
DPB matching by timestamp is central; bad timestamps produce fallback current-buffer references. Field deduplication is explicitly trial-and-error based and should be guarded by conformance tests. Test vectors should include frame/field pictures, MBAFF, long-term refs, reordered refs, scaling matrices, CABAC/CAVLC, missing refs, and stream sequences that reuse DPB slots.
