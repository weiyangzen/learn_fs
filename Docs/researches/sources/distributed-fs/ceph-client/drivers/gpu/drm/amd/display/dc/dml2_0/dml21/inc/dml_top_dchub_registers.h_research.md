# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top_dchub_registers.h

## Purpose
`dml_top_dchub_registers.h` defines the DML21 output structures that carry calculated DC hub, HUBP, DLG, TTU, request queue, MCache, arbitration, and watermark register values from the DML core to the display driver. The file is data-only: it has no functions and exists as a stable typed contract between the calculation code in `src/dml2_core/dml2_core_dcn4_calcs.c`, the programming aggregate in `dml_top_types.h`, and wrapper/translation code that copies the results into DC pipe and watermark structures.

## Important APIs, Types, And Data Shapes
The main per-pipe register payload is `struct dml2_dchub_per_pipe_register_set`, which groups `dml2_display_rq_regs`, `dml2_display_ttu_regs`, `dml2_display_dlg_regs`, and a segment-count style `det_size`. `dml2_display_dlg_regs` holds timing and prefetch register values such as `refcyc_h_blank_end`, `dst_y_prefetch`, VM/PTE row request timings, line delivery timings, cursor offset timing, dynamic metadata timing, and MRQ metadata timing fields. `dml2_display_ttu_regs` carries QoS watermarks, request delivery timing, fixed QoS levels, and ramp-disable flags for luma, chroma, and cursor.

Request queue programming is split into `dml2_display_plane_rq_regs` for plane-local chunk, PTE, swath, and metadata chunk sizing, and `dml2_display_rq_regs` for luma/chroma plane RQ registers plus expansion modes, plane base selection, unbounded requesting, PTE buffer mode, one-row-for-frame, and MRQ expansion. MCache output is represented by `dml2_display_mcache_regs` and `dml2_hubp_pipe_mcache_regs`, with separate main and MALL entries for plane0 and plane1.

Global outputs use `dml2_display_arb_regs` for arbitration and compression-buffer policy, `dml2_dchub_watermark_regs` for watermark and QoS timing, `enum dml2_dchub_watermark_reg_set_index` for sets A through D, and `dml2_dchub_global_register_set` for one arbitration set plus up to four watermark sets.

## Control Flow And Integration
This header does not execute control flow. It is populated by calculation helpers such as `dml2_core_calcs_get_pipe_regs()`, `dml2_core_calcs_get_watermarks()`, and `dml2_core_calcs_get_arb_params()` in `dml2_core_dcn4_calcs.c`. `dml2_core_dcn4.c` stores per-pipe values in `dml2_display_cfg_programming.pipe_regs` and points each `dml2_per_plane_programming.pipe_regs[]` entry at the correct slot. Wrapper code later copies these structures into hardware-facing DC structures: for example, `dml21_program_dc_pipe()` copies a selected `dml2_dchub_per_pipe_register_set` into `pipe_ctx->hubp_regs`, and `dml21_extract_watermark_sets()` copies `dml2_dchub_watermark_regs` into DCN4 watermark sets.

## State And Persistence Behavior
The structures are transient programming state for a mode validation/programming pass. They are not persisted to disk and do not own memory. Pointer ownership is managed outside this header, primarily by `dml2_display_cfg_programming`, which contains backing arrays and per-plane pointers into them. Register values are `uint32_t` because the file models actual calculated hardware register fields; only a few booleans appear for software decisions such as `pte_buffer_mode` and `force_one_row_for_frame`.

## Dependencies
The file includes `dml2_external_lib_deps.h` for integer and boolean types. It is included by `dml_top_types.h`, which embeds these register sets in public programming outputs. Its field names must stay aligned with generated/ported DML calculations and DC wrapper expectations.

## Risks And Edge Cases
Most fields are unvalidated plain integers, so calculation-side unit conversion and fixed-point scaling errors can silently become bad register programming. `det_size` is stored as a segment count in DML programming but later multiplied by 64 KB by the wrapper; mismatched segment sizing would corrupt DET allocation. Watermark indexing relies on `DML2_DCHUB_WATERMARK_SET_NUM` remaining four and matching DCN4 set layout. MRQ fields are present beside legacy fields, so code paths must keep DCN4/DCN42 feature checks correct before consuming metadata request registers.

## Test Signals
Useful signals are mode-programming tests that inspect DLG/RQ/TTU fields for known display configurations, DC pipe programming tests that verify `pipe_ctx->hubp_regs` and `det_buffer_size_kb`, and watermark extraction tests that verify sets A through D are copied only up to `num_watermark_sets`. Boundary cases should include cursor-enabled planes, chroma planes, DCC/MRQ-enabled formats, SubVP phantom pipes, immediate flip, and unbounded request overrides.
