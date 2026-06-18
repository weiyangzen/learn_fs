# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/display_rq_dlg_calc_32.c

## Purpose
This file converts DCN32 DML/VBA-derived pipe timing and request parameters into RQ, DLG, and TTU register field structures. It is the DCN32 implementation behind the `display_mode_lib` v2 request/dialog callbacks and is used after validation/recalculation has filled the helper-accessible VBA values.

## Important APIs, Types, And Functions
The private `is_dual_plane()` helper treats 4:2:0 formats and RGBE alpha as dual-plane. `dml32_rq_dlg_get_rq_reg()` fills `display_rq_regs_st` fields for luma and chroma/plane1 chunk sizes, meta chunk sizes, DPTE/MPTE group sizes, PTE row height, swath height, expansion modes, and detile plane split address. `dml32_rq_dlg_get_dlg_reg()` fills `display_dlg_regs_st` and `display_ttu_regs_st` with fixed-point refclk/pixel ratios, vblank/prefetch line counts, VM/PTE/meta timings, line/request delivery times, cursor delivery, QoS levels, min TTU vblank, and register-range guarded values.

## Control Flow And State
Both public functions clear output structs with `memset`, query many `get_*` helper values from `display_rq_dlg_helpers.h`/VBA state, pack those values into register encodings, print debug traces, then range-check with `ASSERT()` or saturate selected large fields to 23-bit maxima. `dml32_rq_dlg_get_rq_reg()` computes the DET plane1 base address differently for phantom pipes and for dual-plane luma/chroma storage ratios. `dml32_rq_dlg_get_dlg_reg()` handles ODM 2:1/4:1 grouping by discovering hsplit groups and offsetting horizontal blank end per ODM pipe index.

## State And Persistence Behavior
There is no persistence or global mutable state. The functions mutate only caller-provided register structs. They assume `mode_lib` and `e2e_pipe_param` already contain a coherent DML calculation for `num_pipes` and `pipe_idx`; stale or partially populated `vba` values will directly become register programming.

## Dependencies And Integration Points
Includes `display_mode_lib.h`, `display_mode_vba.h`, `dml_inline_defs.h`, and its own header. `display_mode_lib.c` installs these functions in `dml32_funcs` as `rq_dlg_get_dlg_reg_v2` and `rq_dlg_get_rq_reg_v2`. DCN32 FPU code calls those callbacks when programming pipe RQ/DLG registers. The file depends heavily on helper functions such as `get_pixel_chunk_size_in_kbyte`, `get_dst_y_prefetch`, `get_refcyc_per_*`, `get_swath_height_*`, and `print__*_regs_st`.

## Risks
Register packing is sensitive to helper units: some values are in us, some in refclk cycles, some are fixed-point with `2^2`, `2^8`, `2^10`, or `2^19` scaling. Assertions cover many hardware limits, but several fields are clamped instead, and chroma PTE row overflow logs only a warning. The file assumes at most one cursor, `ref_freq_to_pix_freq < 4.0`, valid linear PTE row height, and coherent ODM hsplit metadata. Divide-by-zero is possible if luma/chroma stored swath bytes are inconsistent.

## Test Signals
Regression signals include exact RQ/DLG/TTU register snapshots for known DCN32 modes, asserts in low-vblank or high-refclk cases, underflow during immediate flip, cursor corruption, ODM combine positioning errors, and dual-plane DET allocation errors. Tests should cover linear vs tiled, phantom pipes, RGBE alpha chunk sizing, 4:2:0 chroma paths, dynamic metadata with GPUVM, and one-cursor boundary behavior.
