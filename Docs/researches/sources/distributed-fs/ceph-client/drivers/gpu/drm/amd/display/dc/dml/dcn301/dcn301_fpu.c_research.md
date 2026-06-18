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
