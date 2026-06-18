# subset-b-001409 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/display_rq_dlg_calc_30.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/display_rq_dlg_calc_30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/display_rq_dlg_calc_30.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/display_rq_dlg_calc_30.h

## Purpose
This header exposes the DCN 3.0 RQ/DLG calculation entry points implemented by `display_rq_dlg_calc_30.c`. It is the public interface used by tests and display code that need DML-derived request queue, display logic generator, and TTU register structures.

## Important APIs, Types, And Functions
- Includes `../display_rq_dlg_helpers.h`, which supplies the shared DML register and pipe parameter types.
- Forward-declares `struct display_mode_lib`.
- Declares `dml30_rq_dlg_get_rq_reg(struct display_mode_lib *mode_lib, display_rq_regs_st *rq_regs, const display_pipe_params_st *pipe_param)`.
- Declares `dml30_rq_dlg_get_dlg_reg(struct display_mode_lib *mode_lib, display_dlg_regs_st *dlg_regs, display_ttu_regs_st *ttu_regs, const display_e2e_pipe_params_st *e2e_pipe_param, unsigned int num_pipes, unsigned int pipe_idx, bool cstate_en, bool pstate_en, bool vm_en, bool ignore_viewport_pos, bool immediate_flip_support)`.

## Control Flow
The header has no runtime control flow. It documents the expected call shapes: one function derives RQ registers from a single pipe source configuration, while the other derives DLG and TTU registers for one indexed pipe within a compacted multi-pipe end-to-end parameter array.

## State And Persistence
No state is defined. Callers own all input and output storage. The header only establishes ABI-level dependencies between compilation units.

## Dependencies And Integration Points
This file is included by the DCN 3.0 implementation and by any code needing these calculation routines. It binds DCN 3.0-specific naming to common DML helper types, allowing versioned callers to select the correct calculator while sharing generic register structures.

## Risks And Edge Cases
- The prototypes require valid, initialized `mode_lib` and pipe structs; the implementation assumes many nested fields are populated.
- Several Boolean arguments in the DLG prototype are compatibility knobs, but the DCN 3.0 implementation currently ignores some of them internally.
- Because the header does not include full type definitions beyond helper headers, include ordering must already make `bool` and helper typedefs available through the included DML headers.

## Test Signals
Compile coverage should ensure users can include the header in both implementation and caller contexts. ABI tests or build checks should catch signature drift against call sites. Runtime tests belong with the `.c` implementation and should verify both exported functions populate nonzero, bounded register structures for representative pipes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/display_rq_dlg_calc_30.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn301/dcn301_fpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn301/dcn301_fpu.c

## Purpose
This file centralizes DCN 3.01 floating-point DML setup and watermark/DLG calculations. It defines the DCN 3.01 IP and SoC bounding boxes, board/memory watermark defaults, routines to update clock/latency bounding boxes from SMU/BIOS/debug data, and a DCN301-specific watermark calculation flow before delegating DLG programming to common DCN2 logic.

## Important APIs, Types, And Functions
- Global DML descriptors: `dcn3_01_ip`, `dcn3_01_soc`, `ddr4_wm_table`, and `lpddr5_wm_table`.
- Public functions: `dcn301_fpu_update_bw_bounding_box()`, `dcn301_fpu_set_wm_ranges()`, `dcn301_fpu_init_soc_bounding_box()`, and `dcn301_fpu_calculate_wm_and_dlg()`.
- Private helper: `calculate_wm_set_for_vlevel()` computes one `struct dcn_watermarks` set for a selected voltage level and watermark table entry.
- Key inputs are `struct dc`, `struct dc_state`, `struct clk_bw_params`, `display_e2e_pipe_params_st`, `struct wm_range_table_entry`, and BIOS-provided `struct bp_soc_bb_info`.

## Control Flow
`dcn301_fpu_update_bw_bounding_box()` copies the default clock limits into scratch storage, updates resource counts and memory channels, scans the SMU clock table for max DISPCLK/DPPCLK, maps each SMU DCFCLK entry to the closest default voltage state for inherited clocks, duplicates the final level, applies VCO/debug latency overrides, and calls `dml_init_instance()` with `DML_PROJECT_DCN30`.

`dcn301_fpu_calculate_wm_and_dlg()` chooses voltage levels for watermark sets D, C, B, and A from the requested level and clock-table maximum. Each set is calculated by temporarily overwriting DML clock and latency fields, calling DML watermark helper functions, then restoring the cached dram-clock-change latency. After watermarks are populated, it fills per-pipe DISPCLK/DPPCLK using DML calculated clocks and debug overrides, then calls `dcn20_calculate_dlg_params()`.

## State And Persistence
The file owns mutable global/static DML model data (`dcn3_01_ip`, `dcn3_01_soc`, watermark tables). Update functions persistently rewrite `dcn3_01_soc.clock_limits`, latency fields, VCO speed, `num_states`, `num_chans`, and IP resource counts. The active `dc->dml` instance is reinitialized from those globals. Temporary watermark calculations mutate `context->bw_ctx.dml.soc` and pipe clock fields but are intended to leave only the computed watermarks and clocks in `context`.

## Dependencies And Integration Points
This file depends on DC resource and clock-manager structures, the DCN301 resource pool, `dcn20_fpu.h` helper calculations, and the common DCN20 DLG parameter path. It is called from DCN301 resource/validation code while FPU access is already enabled, enforced through `dc_assert_fp_enabled()`. It integrates SMU clock limits and BIOS latency overrides into the DML instance used by mode validation.

## Risks And Edge Cases
- The clock update path assumes `clk_table->num_entries` is nonzero and that the scratch clock-limit buffer is large enough for all copied entries plus the duplicated final level.
- Mutable global bounding boxes make ordering important: BIOS/debug updates and clock-table updates affect later validations.
- `calculate_wm_set_for_vlevel()` restores only dram-clock-change latency explicitly; SR latency fields remain overwritten in the DML SoC after each set calculation until the next set or caller action.
- Voltage-level clamps for watermark sets assume at least enough clock-table entries for requested C/B levels; small tables rely on `clamp()` behavior.
- Resource counts are taken from the live resource pool, so mismatch between pool capabilities and hard-coded defaults can alter validation.

## Test Signals
Test clock-table ingestion with empty/one/many entries, max DISPCLK/DPPCLK fallback, debug dram latency override, BIOS latency initialization, DDR4 versus LPDDR5 watermark tables, WM_D retraining behavior, and forced/min clock overrides. Regression checks should compare generated watermarks and DLG registers against known DCN301 validation vectors and verify `dml_init_instance()` receives updated resource counts and clock limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn301/dcn301_fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn301/dcn301_fpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn301/dcn301_fpu.h

## Purpose
This header declares the DCN301 FPU-only bandwidth, bounding-box, watermark-range, and watermark/DLG calculation functions. It separates public call sites from the floating-point implementation file.

## Important APIs, Types, And Functions
- `dcn301_fpu_init_soc_bounding_box(struct bp_soc_bb_info bb_info)` applies BIOS latency data.
- `dcn301_fpu_update_bw_bounding_box(struct dc *dc, struct clk_bw_params *bw_params)` updates the DML SoC/IP bounding box from clock-manager data.
- `dcn301_fpu_set_wm_ranges(int i, struct pp_smu_wm_range_sets *ranges, struct _vcs_dpi_soc_bounding_box_st *loaded_bb)` fills SMU watermark range bounds for a clock state.
- `dcn301_fpu_calculate_wm_and_dlg(struct dc *dc, struct dc_state *context, display_e2e_pipe_params_st *pipes, int pipe_cnt, int vlevel_req)` computes DCN301 watermarks and DLG data.

## Control Flow
The header has no runtime behavior. It publishes functions that callers must invoke under the display core FPU protection protocol.

## State And Persistence
No state is stored in the header. The implementation mutates DCN301 global bounding-box data and `dc`/`context` state.

## Dependencies And Integration Points
The prototypes reference `struct dc`, `struct clk_bw_params`, `struct pp_smu_wm_range_sets`, `struct _vcs_dpi_soc_bounding_box_st`, `struct dc_state`, and `display_e2e_pipe_params_st`. The file is intended for DCN301 resource and clock-management code that already has the relevant type definitions in scope.

## Risks And Edge Cases
The header does not itself enforce FPU entry/exit discipline; callers must follow the implementation contract and call only while FPU access is enabled. Signature drift would break DCN301 resource wiring and SMU watermark range programming.

## Test Signals
Build tests should include this header from DCN301 resource code and ensure all prototypes match definitions. Runtime tests should verify that each declared function asserts or behaves correctly when used in the expected FPU-enabled context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn301/dcn301_fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn302/dcn302_fpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn302/dcn302_fpu.c

## Purpose
This file defines the DCN 3.02 DML IP/SoC bounding boxes and updates them from BIOS and clock-manager bandwidth parameters. Its main job is to synthesize DCFCLK/UCLK voltage states for DCN302, fill dependent display/PHY clocks, and reinitialize DML for bandwidth validation.

## Important APIs, Types, And Functions
- Global descriptors: `dcn3_02_ip` and `dcn3_02_soc`.
- Private helper: `dcn302_get_optimal_dcfclk_fclk_for_uclk()` estimates optimal DCFCLK/FCLK from UCLK, channel count, channel width, return bus width, fabric data path width, and normal-use bandwidth percentages.
- Public functions: `dcn302_fpu_update_bw_bounding_box()` and `dcn302_fpu_init_soc_bounding_box()`.
- Key arrays in the update path include `dcfclk_sta_targets`, `optimal_dcfclk_for_uclk`, `optimal_uclk_for_dcfclk_sta_targets`, `dcfclk_mhz`, and `dram_speed_mts`.

## Control Flow
The update function first pulls memory channel count and channel width from BIOS when present, updates VCO speed from the clock manager, and proceeds only if the first clock-table entry has a memory clock. It scans up to `MAX_NUM_DPM_LVL` entries for maximum DCFCLK, DISPCLK, DPPCLK, and PHYCLK. It adjusts the static DCFCLK STA target list to include or cap at the maximum DCFCLK, computes optimal DCFCLK per UCLK state, computes the UCLK needed for each DCFCLK target, merges the target and UCLK-derived sequences into final voltage states, rejects more than `MAX_NUM_DPM_LVL` states, fills `dcn3_02_soc.clock_limits`, and reinitializes both `dc->dml` and `dc->current_state->bw_ctx.dml` when present.

`dcn302_fpu_init_soc_bounding_box()` applies BIOS-provided latency overrides for DRAM clock change and stutter enter/exit values.

## State And Persistence
`dcn3_02_ip` and `dcn3_02_soc` are mutable global DML model data. The update path persistently changes channel topology, VCO speed, `num_states`, and per-state clock limits. It also writes into the live `dc->dml` SoC before full DML reinitialization. No heap allocations or external persistence are used.

## Dependencies And Integration Points
The file depends on DC resource/clock-manager headers, DCN302 resource declarations, and `dcn20_fpu.h` for DML initialization support. It integrates BIOS VRAM information, SMU clock tables, and debug/clock-manager VCO data into the DCN302 DML model. The DML project selected is `DML_PROJECT_DCN30`, matching the DCN3.0-style model used for 3.02.

## Risks And Edge Cases
- The loop scanning `MAX_NUM_DPM_LVL` entries can read default/zero entries beyond `clk_table.num_entries`; this is intentional in local style but makes table initialization important.
- The function returns without reinitializing DML if final synthetic states exceed `MAX_NUM_DPM_LVL`.
- `optimal_uclk_for_dcfclk_sta_targets` may remain zero for a target if no UCLK state satisfies the comparison, producing a low/zero DRAM speed in some corner inputs.
- The implementation assumes memory clock units convert to MTS with `memclk_mhz * 16`, unlike later DCN31 paths that use `2 * wck_ratio`.
- Mutable global SoC data means BIOS/debug/clock-manager updates persist into later validations.

## Test Signals
Tests should cover max DCFCLK above, equal to, and below the static target list; single and multiple UCLK states; absent memory clocks; BIOS channel-width overrides; state-count overflow; zero DTBCLK/SOCCLK carry-forward; and reinitialization of both current and active DML contexts. Golden bandwidth validation vectors should compare generated `clock_limits` and downstream mode validation outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn302/dcn302_fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn302/dcn302_fpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn302/dcn302_fpu.h

## Purpose
This header declares the two DCN302 FPU bandwidth-bounding-box entry points used by DCN302 resource and initialization code.

## Important APIs, Types, And Functions
- `dcn302_fpu_init_soc_bounding_box(struct bp_soc_bb_info bb_info)` loads BIOS latency overrides into the DCN302 SoC model.
- `dcn302_fpu_update_bw_bounding_box(struct dc *dc, struct clk_bw_params *bw_params)` rebuilds DCN302 DML clock limits from runtime clock-manager data.

## Control Flow
No runtime control flow exists in the header. It provides compile-time linkage to the DCN302 FPU implementation.

## State And Persistence
The header stores no state. The implementation mutates global DCN302 SoC/IP descriptors and DML contexts.

## Dependencies And Integration Points
The declarations reference `struct bp_soc_bb_info`, `struct dc`, and `struct clk_bw_params`. Callers are expected to include this from resource/clock-management code with those types already visible and to call under the display-core FPU guard.

## Risks And Edge Cases
The interface is intentionally small, so any required DCN302 behavior beyond initialization and clock-table update must be wired elsewhere. Incorrect FPU call context or missing type declarations are the main integration hazards.

## Test Signals
Build coverage should catch prototype/definition mismatch. Functional coverage should exercise both declarations through the DCN302 resource path and verify the DML instance is reinitialized after clock-table updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn302/dcn302_fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn303/dcn303_fpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn303/dcn303_fpu.c

## Purpose
This file is the DCN 3.03 counterpart to the DCN302 FPU bounding-box code. It defines DCN303 IP/SoC defaults, computes synthetic DCFCLK/UCLK states from clock-manager data, applies BIOS latency overrides, and reinitializes DML for DCN303 validation.

## Important APIs, Types, And Functions
- Global descriptors: `dcn3_03_ip` and `dcn3_03_soc`.
- Private helper: `dcn303_get_optimal_dcfclk_fclk_for_uclk()` estimates optimal DCFCLK/FCLK from memory bandwidth and SoC bus characteristics.
- Public functions: `dcn303_fpu_update_bw_bounding_box()` and `dcn303_fpu_init_soc_bounding_box()`.
- DCN303-specific constants differ from DCN302 in resource counts and capabilities: two DSC/DPP/OTG-oriented defaults and no ODM 4:1 support.

## Control Flow
`dcn303_fpu_update_bw_bounding_box()` mirrors the DCN302 sequence: update memory topology from BIOS, set VCO speed, scan clock-table maxima, adjust static DCFCLK target list, compute optimal DCFCLK per UCLK, compute optimal UCLK per DCFCLK target, merge the two sequences into final states, fill per-state clock limits, then reinitialize DML. DCN303 adds a fallback in target-to-UCLK mapping: when all optimal DCFCLK values are below a target, that target is assigned the max UCLK. It also adds a low-channel-count adjustment that forces DCFCLK/FCLK to 100 MHz for qualifying low memory-speed states.

`dcn303_fpu_init_soc_bounding_box()` applies BIOS latency overrides for DRAM clock change and stutter timing.

## State And Persistence
The global `dcn3_03_soc` is persistently changed by BIOS initialization and clock updates. `dcn3_03_ip` holds static IP capability data. The update function mutates the active `dc->dml` and optionally `dc->current_state->bw_ctx.dml` through `dml_init_instance()`.

## Dependencies And Integration Points
The file depends on common DC resource and clock-manager structures, DCN303 resource definitions, and DCN20 FPU/DML initialization helpers. It integrates BIOS VRAM topology, SMU clock tables, and clock-manager VCO into the DCN303 display-mode model using `DML_PROJECT_DCN30`.

## Risks And Edge Cases
- Like DCN302, the scan loops inspect up to `MAX_NUM_DPM_LVL` entries, so unused entries must be zero-initialized.
- State-count overflow triggers `ASSERT(0)` and returns without reinitializing DML.
- The low-channel-count 100 MHz override can intentionally reduce DCFCLK/FCLK for memory speeds between 1500 and 1700 MTS, which must match platform policy.
- Unit conversion uses `memclk_mhz * 16`; incorrect clock table units would distort bandwidth modeling.
- Mutable global SoC updates persist across calls and can be affected by call ordering.

## Test Signals
Use tests that compare DCN303 against DCN302 for the special max-UCLK fallback and low-channel-count override. Cover max DCFCLK target adjustment, state overflow, BIOS channel topology, missing memory clock, carry-forward of DTBCLK/SOCCLK, latency overrides, and DML reinitialization of current and active contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn303/dcn303_fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn303/dcn303_fpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn303/dcn303_fpu.h

## Purpose
This header declares the DCN303 FPU functions for bounding-box update and BIOS latency initialization.

## Important APIs, Types, And Functions
- `dcn303_fpu_update_bw_bounding_box(struct dc *dc, struct clk_bw_params *bw_params)` updates the DCN303 DML SoC/IP model from runtime clock-manager data.
- `dcn303_fpu_init_soc_bounding_box(struct bp_soc_bb_info bb_info)` imports BIOS-provided latency values into the DCN303 SoC model.

## Control Flow
The header contains no runtime control flow and serves as the public compile-time contract for the DCN303 FPU implementation.

## State And Persistence
No data is stored here. State changes happen inside the implementation's global DML descriptors and caller-owned `dc` state.

## Dependencies And Integration Points
The prototypes reference display-core and clock-manager structures. The header is intended for DCN303 resource initialization and validation paths that already observe the DC FPU access discipline.

## Risks And Edge Cases
The same small public surface means all DCN303 DML behavior must be reached through these two hooks or common DCN code. Calling outside an FPU-enabled section would violate the implementation contract.

## Test Signals
Build tests should ensure the header stays in sync with the implementation. Integration tests should invoke both functions through the DCN303 resource path and verify the updated DML model reflects BIOS and SMU clock inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn303/dcn303_fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/dcn31_fpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/dcn31_fpu.c

## Purpose
This file centralizes DCN 3.1, 3.1.5, and 3.1.6 floating-point DML operations. It defines versioned IP and SoC bounding boxes, updates those bounding boxes from clock-manager data, computes watermarks and DLG parameters, handles pstate/z8 behavior, and exposes utility calculations for maximum non-ODM pixel rate and DET segments needed to hide pstate latency.

## Important APIs, Types, And Functions
- Versioned IP descriptors: `dcn3_1_ip`, `dcn3_15_ip`, and `dcn3_16_ip`.
- Versioned SoC descriptors: `dcn3_1_soc`, `dcn3_15_soc`, and `dcn3_16_soc`.
- Public functions: `dcn31_zero_pipe_dcc_fraction()`, `dcn31_update_soc_for_wm_a()`, `dcn315_update_soc_for_wm_a()`, `dcn31_calculate_wm_and_dlg_fp()`, `dcn31_update_bw_bounding_box_fpu()`, `dcn315_update_bw_bounding_box_fpu()`, `dcn316_update_bw_bounding_box_fpu()`, `dcn_get_max_non_odm_pix_rate_100hz()`, and `dcn_get_approx_det_segs_required_for_pstate()`.
- Key external dependencies include DML helpers for watermarks, stutter, clocks, DET size, and `dcn20_calculate_dlg_params()`.

## Control Flow
The file starts by documenting the FPU containment pattern: public functions assert FPU access, while callers must perform the FPU begin/end wrapping. The bounding-box update functions for 3.1 and 3.1.6 copy default clock limits to scratch, update IP resource counts and channel counts, scan max DISPCLK/DPPCLK, map SMU entries to default voltage states, fill voltage-dependent and independent clocks, apply VCO/debug latency overrides, and initialize DML. The 3.1.5 update path writes directly into `dcn3_15_soc`, uses max DISPCLK/DPPCLK for all states to avoid ODM lowering voltage, derives DSCCLK from DISPCLK, and sets the DML VCO to twice max DISPCLK.

`dcn31_calculate_wm_and_dlg_fp()` selects the active DCFCLK from DML VBA state data and min DCFCLK, handles zero-pipe configs by lowering blocking clocks, updates DML SoC latency for WM_A through the resource-pool hook, calculates watermark set A including Z8 stutter timing and urgent/meta/bandwidth fractions, clones set A into B/C/D, fills per-pipe DISPCLK/DPPCLK with forced/min-clock overrides, calls `dcn20_calculate_dlg_params()`, records pstate-change support, zeros clocks when there are streams but no active HUBP planes, then updates per-pipe DET buffer size and remaining compbuf size.

## State And Persistence
The versioned SoC/IP descriptors are mutable static/global state. Update functions persistently rewrite clock limits, resource counts, memory topology, VCO speed, and latency overrides before reinitializing `dc->dml`. `dcn31_calculate_wm_and_dlg_fp()` mutates `context->bw_ctx`, `pipes`, per-pipe `det_buffer_size_kb`, and clock fields. It does not allocate memory or persist data outside display-core state.

## Dependencies And Integration Points
This file integrates DCN31/315/316 resource definitions, clock-manager bandwidth parameters, DML VBA-calculated voltage-level data, debug knobs, and common DCN20 DLG calculation. It is the FPU boundary for DCN31x resource validation. Resource pools provide `update_soc_for_wm_a()` so DCN315 can use dummy pstate latency unless vactive pstate change is supported.

## Risks And Edge Cases
- All public functions require an active FPU context; misuse can violate kernel FPU rules.
- `dcn31_zero_pipe_dcc_fraction()` indexes `pipes[pipe_cnt]`, which appears to expect a current pipe index despite the parameter name and could be risky if passed a count.
- The zero-pipe path sets only DCFCLK and returns early; callers must tolerate partial clock updates.
- WM sets B/C/D are copied from set A rather than independently calculated, which is a deliberate DCN31x policy but differs from DCN301.
- Active stream without active plane forces several clocks to zero and enables pstate change; this is power-sensitive behavior that needs validation for blanking/phantom streams.
- DET buffer sizes over 384 KiB are halved before total DET subtraction, so compbuf accounting depends on DML DET outputs and hardware limits.
- Clock-table assertions require nonzero entries; state arrays must fit the DML voltage-state capacity.

## Test Signals
Test DCN31, DCN315, and DCN316 clock-table ingestion separately, including max clock fallback, WCK ratio memory-speed conversion, debug latency overrides, min/forced display clocks, zero-pipe validation, active stream with no active plane, WM_A latency update differences, Z8 residency clamping, pstate-change support, DET/compbuf accounting, and utility functions. Golden vectors should compare watermarks, clocks, and DLG parameters across DCN31x variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/dcn31_fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/dcn31_fpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/dcn31_fpu.h

## Purpose
This header declares the public DCN31x FPU entry points and shared constants for DET and compbuf sizing. It is the versioned interface used by DCN31, DCN315, and DCN316 resource code.

## Important APIs, Types, And Functions
- Constants: `DCN3_1_DEFAULT_DET_SIZE`, `DCN3_15_DEFAULT_DET_SIZE`, `DCN3_15_MIN_COMPBUF_SIZE_KB`, `DCN3_16_DEFAULT_DET_SIZE`, and `DCN3_16_MIN_COMPBUF_SIZE_KB`.
- Watermark/DLG functions: `dcn31_zero_pipe_dcc_fraction()`, `dcn31_update_soc_for_wm_a()`, `dcn315_update_soc_for_wm_a()`, and `dcn31_calculate_wm_and_dlg_fp()`.
- Bounding-box update functions: `dcn31_update_bw_bounding_box_fpu()`, `dcn315_update_bw_bounding_box_fpu()`, and `dcn316_update_bw_bounding_box_fpu()`.
- Utility functions: `dcn_get_max_non_odm_pix_rate_100hz()` and `dcn_get_approx_det_segs_required_for_pstate()`.
- Pipe population hook: `dcn31x_populate_dml_pipes_from_context()`, declared here but implemented elsewhere.

## Control Flow
The header has no runtime control flow. It groups all DCN31x FPU APIs behind one include so resource code can select version-specific update functions and shared calculation helpers.

## State And Persistence
No state is stored in this header. The implementation updates DML SoC/IP descriptors and caller-owned display-core state.

## Dependencies And Integration Points
The declarations depend on DML pipe types, `struct dc`, `struct dc_state`, clock bandwidth parameters, DML SoC bounding-box structs, and `enum dc_validate_mode`. It bridges DCN31x resource construction/validation code to the FPU implementation and to the pipe-population helper.

## Risks And Edge Cases
- FPU discipline is not encoded in the type system; callers must invoke these functions only inside the required DC FPU section.
- Shared constants influence hardware buffer partitioning and must stay aligned with the versioned IP descriptors in the `.c` file.
- `dcn31x_populate_dml_pipes_from_context()` being declared but not defined in this file means integration depends on another compilation unit.

## Test Signals
Build checks should ensure all declared functions resolve for DCN31x configurations. Runtime coverage should exercise each versioned bounding-box update function, WM_A update variant, DLG calculation entry, and utility calculations through resource validation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/dcn31_fpu.h -->
