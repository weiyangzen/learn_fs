# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/display_rq_dlg_calc_30.c

## Purpose
This file implements the DCN 3.0 Display Mode Library request-queue, display-logic-generator, and TTU register calculation path. It converts `display_pipe_params_st` and compacted `display_e2e_pipe_params_st` timing/source/scaler/clock descriptions into hardware-facing `display_rq_regs_st`, `display_dlg_regs_st`, and `display_ttu_regs_st` values. It is a numeric model for memory request sizing, meta/PTE row layout, DET buffer split, prefetch timing, urgent/stutter/pstate watermarks, cursor delivery, and fixed-point register packing.

## Important APIs, Types, And Functions
- Public entry points are `dml30_rq_dlg_get_rq_reg()` and `dml30_rq_dlg_get_dlg_reg()`.
- Local helpers include `is_dual_plane()`, `get_refcyc_per_delivery()`, `get_blk_size_bytes()`, `extract_rq_sizing_regs()`, `extract_rq_regs()`, `handle_det_buf_split()`, `get_meta_and_pte_attr()`, `get_surf_rq_param()`, `dml_rq_dlg_get_rq_params()`, `calculate_ttu_cursor()`, and `dml_rq_dlg_get_dlg_params()`.
- Key data contracts come from DML shared headers: `struct display_mode_lib`, `display_pipe_params_st`, `display_e2e_pipe_params_st`, `display_rq_params_st`, `display_data_rq_*_params_st`, `display_dlg_sys_params_st`, `display_dlg_regs_st`, and `display_ttu_regs_st`.
- Format and tiling decisions are driven by `enum source_format_class`, `enum source_macro_tile_size`, `enum dm_swizzle_mode`, scan direction, GPUVM/hostVM flags, ODM combine, hsplit grouping, cursor BPP, DCC metadata, and viewport/pitch/surface dimensions.

## Control Flow
`dml30_rq_dlg_get_rq_reg()` zeroes the output, builds an internal `display_rq_params_st` through `dml_rq_dlg_get_rq_params()`, and extracts register encodings with `extract_rq_regs()`. RQ construction first calculates luma surface sizing and metadata/PTE geometry with `get_surf_rq_param()` and `get_meta_and_pte_attr()`, optionally repeats for chroma/alpha dual-plane formats, then calls `handle_det_buf_split()` to choose 256B versus 128B request storage and DET plane partitioning.

`dml30_rq_dlg_get_dlg_reg()` first gathers system timing inputs from DML helper functions such as urgent watermark, deepsleep DCFCLK, extra latency, memory trip, dram-clock-change, stutter, and immediate-flip bandwidth/bytes. It then computes RQ parameters for the selected pipe and passes the RQ-derived DLG values into `dml_rq_dlg_get_dlg_params()`. The DLG path calculates OTG-dependent fixed-point values, prefetch line budgets, VM/PTE/meta row costs, ODM-adjusted hblank placement, vstartup/vready behavior, scaler delivery rates, TTU request delivery for luma/chroma/cursors, and final DLG/TTU register fields.

## State And Persistence
The file is stateless across calls. It mutates only stack-local intermediate structs and caller-provided register outputs. The persistent inputs live in `mode_lib->ip`, `mode_lib->soc`, and the pipe arrays supplied by the caller. The only global-like effects are debug printing and assertion checks through DML macros. No heap ownership, reference counting, kernel objects, or file-system state are involved.

## Dependencies And Integration Points
The implementation depends on `display_mode_lib.h`, `display_mode_vba.h`, `dml_inline_defs.h`, `display_rq_dlg_calc_30.h`, `display_mode_vba_30.h`, and the common RQ/DLG helper functions used for watermark and viewport timing calculations. It integrates into the AMD DC DML validation/programming flow: higher-level resource code populates DML pipe arrays, this file calculates register-ready DLG/RQ/TTU values, and DCN hardware programming paths consume those structs. It also depends on DCN 3.0 byte-per-pixel/block sizing through `dml30_CalculateBytePerPixelAnd256BBlockSizes()`.

## Risks And Edge Cases
- Many calculations assume nonzero row/group counts such as `dpte_groups_per_row_ub_l`, `meta_chunks_per_row_ub_l`, `req_per_swath_ub_l`, and pixel/clock rates; invalid pipe inputs can become divide-by-zero or assertion failures.
- Fixed-point register field widths are protected mostly by `ASSERT()` or ad hoc clamps, so production behavior depends on whether assertions are compiled/enforced.
- Linear-surface DPTE row height asserts `log2_dpte_row_height_linear >= 3`; unusual pitch/page-size combinations can fail validation.
- Dual-plane handling treats RGBE alpha like the chroma plane in parts of the sizing path, while several comments mention legacy 4:2:0/DCC limitations.
- ODM and hsplit logic derives pipe ordering from `hsplit_grp`; incorrect grouping or missing `full_recout_width` changes delivery timing.
- Several parameters are intentionally unused in the DLG helper (`vm_en`, `ignore_viewport_pos`, `immediate_flip_support`) in this implementation, which is important when comparing DCN versions.
- Hardware constants such as DET size, 8 KiB chunk, 2 KiB meta chunk, 512/2048 byte PTE groups, and cursor request thresholds are embedded directly.

## Test Signals
Useful tests are golden DML-vector comparisons for RQ/DLG/TTU output across linear/tiled, horizontal/vertical scan, GPUVM/hostVM, DCC metadata, dual-plane 4:2:0/RGBE, 10bpc packed surfaces, cursor sizes/BPPs, ODM 2:1/4:1, hsplit, interlaced timing, immediate flip inputs, and extreme pitches/viewports. Assertion and boundary tests should target register width limits, max/min vblank, `htotal <= 75` special handling, 4 KiB versus 64 KiB page behavior, and DPTE/meta group count divisors.
