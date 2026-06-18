# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c

## Purpose

`dcn30_resource.c` is the DCN 3.0 resource-pool implementation for Navi2x/Sienna Cichlid-class display hardware. It extends the DCN20 resource model with DCN3 register lists, DML 3.0 validation, up to six pipes, HPO-adjacent stream encoder support through common resource construction, VPG/AFMT ownership on stream encoders, MALL/cache-related caps, MPC 3D LUT resources, DMUB PSR/ABM, firmware-assisted mclk switching logic, and DCN3 writeback arbitration.

## Important APIs, Types, And Functions

- `dcn30_create_resource_pool()` and `dcn30_resource_construct()` allocate and initialize the DCN30 resource pool.
- `dcn30_resource_destruct()` and `dcn30_destroy_resource_pool()` free DCN30-owned stream encoder VPG/AFMT, DPPs, HUBPs, OPPs, TGs, DSCs, DWB/MCIF_WB, ABMs, MPC LUT/shaper resources, PSR, DCCG, DIO, clocks, DDC, audio, and OEM DDC service.
- Factories create DCN30 DPP/HUBP/OPP/TG/MPC/HUBBUB/DIO/link encoder/stream encoder/VPG/AFMT/DSC/DWB/MCIF_WB/AUX/I2C/clock resources.
- `dcn30_internal_validate_bw()` is the core validation and topology mutation routine.
- `dcn30_validate_bandwidth()` allocates DML pipes, calls internal validation, and calculates watermarks/DLG when in programming mode.
- `dcn30_populate_dml_pipes_from_context()` reuses DCN20 population then forces 16-line-buffer depth.
- `dcn30_populate_dml_writeback_from_context()`, `dcn30_calculate_wm_and_dlg()`, and `dcn30_update_soc_for_wm_a()` wrap DCN30 FPU helpers.
- `dcn30_set_mcif_arb_params()` and `dcn30_calc_max_scaled_time()` handle DCN3 writeback arbitration.
- `dcn30_acquire_post_bldn_3dlut()` and `dcn30_release_post_bldn_3dlut()` manage MPC post-blending LUT/shaper resources and RMU mux state.
- `dcn30_update_bw_bounding_box()` derives DCFCLK/UCLK voltage states from clock tables and updates the DCN3 bounding box.
- Firmware-assisted mclk-switch helpers include `dcn30_can_support_mclk_switch_using_fw_based_vblank_stretch()`, `dcn30_setup_mclk_switch_using_fw_based_vblank_stretch()`, and refresh-rate helpers.

## Control Flow

Construction validates pipe-fuse recipes, enters an FPU section, sets BIOS registers and `dcn30_res_pool_funcs`, initializes DC caps for up to six pipes, MALL size, cursor cache, color pipeline, LTTPR VBIOS caps, debug/check defaults, VM helper, six PLL clock sources plus DP DTO, DCCG, SoC bounding box, fused DPP/OTG counts, DML 3.0 instance, IRQ service, HUBBUB, DIO, HUBPs, DPPs, OPPs, TGs, DMUB PSR, per-pipe DMUB ABMs, MPC with 3D LUT support, DSCs, DWB/MCIF_WB, AUX/I2C engines, common resources through `resource_construct()`, hardware sequencer, plane caps, ODM factor, cap functions, and optional OEM DDC service. Failure exits the FPU section, destructs partially initialized state, and returns false.

`dcn30_internal_validate_bw()` resets selected DML state, updates watermark-A SoC data, populates pipes, logs DML input, tries p-state-friendly validation for programming mode, optionally falls back to self-refresh-only validation, applies DCN20 split flags, rejects unsupported windowed MPO ODM when disabled, merges pipes flagged for merge, creates two-way or four-way MPC/ODM splits using `dcn30_split_stream_for_mpc_or_odm()`, preserves preferred previous pipe indices through `dcn30_find_split_pipe()`, rebuilds mapped stream resources for ODM, rebuilds scaling for all plane pipes, validates DSC, optionally repopulates DML pipes, and returns selected voltage and pipe count.

`dcn30_validate_bandwidth()` wraps internal validation, logs failure using DML status, skips watermark/DLG calculation for non-programming validation, and calls `calculate_wm_and_dlg` for programming commits. Firmware-assisted mclk switching checks single-display, panel/debug/capability flags, shutdown state, refresh rate at current and max-stretched vblank, FreeSync/VRR policy, stream status, and marks `fpo_in_use`.

## State And Persistence Behavior

The file has no disk persistence. It mutates DC caps/debug/check state, DML SoC/IP and selected validation state, watermark and DLG outputs, `bw_ctx` clocks/watermarks, resource pool arrays, pipe topology, DSC acquisition, MPC 3D LUT acquisition and RMU mux state, stream status `fpo_in_use`, writeback MCIF arbitration slots, MALL/cache-related caps, and optional OEM DDC service ownership.

The global `dcn3_0_soc` and `dcn3_0_ip` objects are patched from VBIOS VRAM info, clock tables, and fuse count. `dcn30_update_bw_bounding_box()` builds a dynamic voltage-state table from DCFCLK targets and UCLK states, so validation results depend on runtime clock data.

## Dependencies And Integration Points

The file depends on DCN30 register headers, Sienna Cichlid offsets, DCN30 DML/FPU helpers, `display_mode_vba_30`, DCN20 common helpers, generic DC resource code, DCE AUX/I2C/audio/clock helpers, DMUB PSR/ABM service, IRQ service, link service, VBIOS LTTPR queries, VM helper, amdgpu SoC bounding-box data, and kernel allocation/logging. The resource function table exports DCN30 validation, watermark/DLG calculation, SoC update, DML population, stream add/remove, pipe acquisition/release, writeback population, MCIF arbitration, 3D LUT acquire/release, bounding-box update, panel defaults, and tiling defaults.

## Risks And Edge Cases

- Pipe-fuse validation only expects all pipes or a single-pipe recipe; unexpected fuses are forced to single pipe after a debug break.
- The constructor wraps a long allocation sequence in an FPU section; every failure path must call `DC_FP_END()`.
- Four-way MPC/ODM splitting has complex old-index preservation and new split tracking; pointer mistakes can corrupt chains or cause transient underflow.
- Dynamic bounding-box construction depends on clock-table ordering, nonzero memclk, VRAM channel data, and array bounds for `DC__VOLTAGE_STATES`.
- Firmware-assisted mclk switching depends on single-stream, FreeSync, VRR policy, DMUB capability, refresh-rate math, and panel patches; false positives can harm timing stability.
- MPC LUT acquisition mutates LUT state bits and resource-context bitmaps; release must clear both LUT and shaper consistently.
- DCN3 writeback arbitration assumes packed 444/FP16 output and computes `time_per_pixel` from stream `phy_pix_clk`; invalid or zero clocks are hazardous.
- Destruction covers more nested resources than DCN20, including VPG/AFMT and multiple ABMs, making ownership drift easy.

## Test Signals

Tests should cover full and single-pipe fuse recipes, constructor failure cleanup, DML3 validation, p-state fallback, two-way and four-way MPC/ODM, DSC validation, watermark/DLG calculation only in programming mode, dynamic bounding-box updates from clock tables, firmware-assisted mclk-switch eligibility and setup, MPC 3D LUT acquire/release exhaustion, DWB/MCIF arbitration, LTTPR VBIOS cap reads, MALL/cursor caps, DMUB PSR/ABM creation, and stream encoder VPG/AFMT teardown. Runtime signals include `DC_FAIL_BANDWIDTH_VALIDATE`, DML validation messages, bandwidth trace markers, assertions in split allocation, underflow during topology updates, and FAMS/FPO flags in stream status.
