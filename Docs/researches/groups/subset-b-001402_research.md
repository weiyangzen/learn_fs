# Research: subset-b-001402

This grouped report covers AMD DC display mode library and bandwidth/FPU helpers under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml`. Each section is source-tree aligned and intended for deterministic splitting into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/calcs/dcn_calcs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/calcs/dcn_calcs.c

## Purpose

`dcn_calcs.c` is the DCN 1.x bandwidth validation and programming bridge between display core state (`struct dc`, `struct dc_state`, `struct pipe_ctx`) and the legacy generated DCN bandwidth calculator plus DML request/DLG/TTU register calculators. It contains default DCN 1.0 SoC/IP bounding boxes, translates stream and plane state into calculator inputs, runs mode support and watermark equations, mutates pipe topology for required MPC pipe splits, programs per-pipe DLG/RQ/TTU parameter caches, updates bandwidth clock targets in `context->bw_ctx`, and notifies PPLIB/SMU about watermark ranges.

The file explicitly identifies itself as hardware-spreadsheet-derived code and warns against stylistic cleanup unless behavior is clearly wrong. That matters because many equations, magic constants, and ordering choices are compatibility constraints rather than general driver style.

## Important APIs, Types, And Data

Primary exported data:

- `dcn10_soc_defaults`: DCN 1.0 default `struct dcn_soc_bounding_box` values, including latency, DCF/DISP/DPP/PHY clocks, fabric/DRAM bandwidth, channel count, downspread, return bus width, request size, and display bandwidth limit.
- `dcn10_ip_defaults`: DCN 1.0 default `struct dcn_ip_params` values, including buffer sizes, chunk sizes, line-buffer limits, DPP/writeback counts, scaler throughput limits, tap/ratio limits, and DCFCLK cstate latency.

Primary exported functions:

- `swizzle_mode_to_macro_tile_size(enum swizzle_mode_values sw_mode)`: maps DC swizzle modes to DML macro tile sizes. Unsupported DCN swizzles assert and return zero/default.
- `dcn_validate_bandwidth(struct dc *dc, struct dc_state *context, enum dc_validate_mode validate_mode)`: central DCN1 bandwidth validation entry point. In full programming mode it also calculates watermarks, clocks, split pipes, and DLG/RQ/TTU registers.
- `dcn_bw_update_from_pplib_fclks(...)`: converts PPLIB FCLK levels into fabric/DRAM bandwidth fields on `dc->dcn_soc`.
- `dcn_bw_update_from_pplib_dcfclks(...)`: copies PPLIB DCFCLK levels into DCN voltage-state DCF clocks.
- `dcn_get_soc_clks(...)`: exposes minimum FCLK, minimum DCFCLK, and SOCCLK from the active SoC box.
- `dcn_bw_notify_pplib_of_wm_ranges(...)`: builds `pp_smu_wm_range_sets` for reader/writer watermark instances and sends them through `pp_smu->rv_funcs.set_wm_ranges`.
- `dcn_bw_sync_calcs_and_dml(struct dc *dc)`: logs DCN bounding-box values and mirrors `dc->dcn_soc` / `dc->dcn_ip` into `dc->dml.soc` / `dc->dml.ip`.

Important internal helpers:

- `tl_sw_mode_to_bw_defs`, `tl_lb_bpp_to_int`, and `tl_pixel_format_to_bw_defs` translate DC enums into legacy calculator enums and numeric line-buffer depth.
- `pipe_ctx_to_e2e_pipe_params` converts a single `pipe_ctx` into a DML 1.x display pipe, including DCC policy, viewport, tiling, rotation, source format, scaler taps/ratios, timing, and output defaults.
- `dcn_bw_calc_rq_dlg_ttu` prepares DML sys parameters from bandwidth variables and invokes `dml1_rq_dlg_get_rq_params`, `dml1_extract_rq_regs`, and `dml1_rq_dlg_get_dlg_params`.
- `split_stream_across_pipes` clones a primary pipe into a secondary pipe and assigns secondary hardware resources from the pool.
- `dcn_bw_apply_registry_override` applies debug latency/bandwidth overrides from `dc->debug` to `dc->dcn_soc`.
- `hack_disable_optional_pipe_split`, `hack_force_pipe_split`, and `hack_bounding_box` manipulate DPP/DISP clock limits to steer pipe split decisions for debug policy and tiny plane workarounds.
- `get_highest_allowed_voltage_level` caps validation to vmin for low-power ASICs.

## Control Flow

`dcn_validate_bandwidth` is the core flow:

1. It starts performance and bandwidth trace instrumentation, applies debug registry overrides, and resynchronizes DML state if SoC values changed.
2. It clears `context->dcn_bw_vars` and copies SoC/IP fields from `dc->dcn_soc` and `dc->dcn_ip` into the local generated-calculator variable block.
3. It initializes voltage-state arrays for fabric bandwidth, DCFCLK, DISPCLK, DPPCLK, PHYCLK, and sets high-level policy inputs such as synchronized vblank, timing assignment override, and h/v ratio behavior.
4. It iterates active pool pipes, skips inactive pipes and secondary split pipes, and fills per-plane calculator inputs from stream timing and plane/scaler state. No-plane streams are validated with capped 1920x1080 source dimensions so output timing can be accepted even without a native-sized plane.
5. It computes scaler settings, applies pipe-split debug workarounds, runs generated spreadsheet functions (`mode_support_and_system_configuration`, `display_pipe_configuration`, `dispclkdppclkdcfclk_deep_sleep_prefetch_parameters_watermarks_and_performance_calculation`), and derives read bandwidth.
6. In full programming mode and on successful voltage selection, it chooses consumed bandwidth, writes watermarks A-D, computes required FCLK/DCFCLK/DISPCLK/DPPCLK/PHYCLK fields, handles debug clock minimums/maximums, and sets max-supported DPPCLK for the selected voltage.
7. It iterates active primary pipes again, writes DLG timing offsets to `pipe_dlg_param`, marks full plane updates, splits or merges hsplit pipes to match `v->dpp_per_plane`, and calculates DML RQ/DLG/TTU registers for both primary and split pipes.
8. It restores DML SoC SR timing for voltage level 0, enforces a total display bandwidth limit based on `percent_disp_bw_limit`, and returns true only if the bandwidth limit passes and the selected voltage is allowed for the ASIC.

The PPLIB helper flow is separate: FCLK/DCFCLK updates mutate `dc->dcn_soc`, `dcn_get_soc_clks` reads minimum clocks from that state, and `dcn_bw_notify_pplib_of_wm_ranges` creates four watermark ranges, although DCN1 effectively mirrors set A across all instances due to a noted hardware bug.

## State And Persistence Behavior

This file has no file or disk persistence. Its persistent effects are in kernel/display driver objects:

- Mutates `dc->dcn_soc` when debug overrides or PPLIB clock updates are applied.
- Mutates `dc->dml.soc` and `dc->dml.ip` in `dcn_bw_sync_calcs_and_dml`.
- Clears and repopulates `context->dcn_bw_vars` on each validation.
- Updates `context->bw_ctx.bw.dcn.watermarks`, `context->bw_ctx.bw.dcn.clk`, and selected `context->bw_ctx.dml.soc` latency fields.
- Mutates `context->res_ctx.pipe_ctx[]` in programming validation by splitting/merging pipe chains, assigning secondary pipe resources, clearing merged secondary pipes, and writing DLG/RQ/TTU register cache fields.
- Marks `pipe->plane_state->update_flags.bits.full_update` when a programmed plane participates in validation.
- Calls into PPLIB/SMU to persist watermark range policy in firmware-managed power logic.

The function asserts that split resources exist but does not allocate memory. State lifetime follows the owning `dc`, `dc_state`, resource pool, and SMU objects.

## Dependencies And Integration Points

Direct includes connect this file to display core, DCN1 resources, hubbub DCC support, generated DCN calculator code, and DML1 RQ/DLG calculation. The key integration points are:

- `dc`, `dc_state`, `pipe_ctx`, stream timing, plane state, scaler data, and resource pool structures from display core/resource code.
- Generated calculator functions and constants from `dcn_calc_auto.h` and `dcn_calc_math.h`.
- DML1 register calculation APIs in `dml/dml1_display_rq_dlg_calc.h`.
- HUBBUB DCC capability callback `dcc_support_pixel_format`.
- Resource helpers such as `resource_build_scaling_params` and `resource_find_free_secondary_pipe_legacy`.
- ASIC revision macros such as `ASICREV_IS_RV1_F0` and `dc->config.is_vmin_only_asic`.
- Debug options on `dc->debug`, including watermark latency overrides, pipe split policy, min/max clocks, optimized watermark behavior, and PPLIB watermark report mode.
- SMU/PPLIB `pp_smu_funcs_rv.set_wm_ranges`.

Downstream consumers are the DCN1 resource validation/commit paths that rely on `context->bw_ctx` and `pipe_ctx` register caches before programming hardware.

## Risks And Edge Cases

- The code dereferences `pipe->plane_state` in helper paths that are only safe when the caller has already filtered no-plane cases. Changes to helper call sites can introduce null dereferences.
- Unsupported swizzle modes call `ASSERT`/`BREAK_TO_DEBUGGER` but still return fallback values in some mapping helpers. Release builds may continue with pessimistic or invalid assumptions.
- Pipe splitting mutates linked pipe chains in place. Bugs can leave stale `top_pipe`/`bottom_pipe` relationships, stale resource pointers, or uncleared secondary pipe state.
- `split_stream_across_pipes` shallow-copies the primary `pipe_ctx` before replacing hardware-resource pointers; any future embedded ownership fields in `pipe_ctx` would need review.
- Chroma tap values of 1 are forcibly bumped to 2 for spreadsheet behavior. This is an intentional model workaround that can surprise tests comparing against raw scaler state.
- Clock and bandwidth unit conversions mix MHz, kHz, GB/s, MB/s, nanoseconds, and microseconds. The code often casts float/double values to integer fields; rounding behavior affects watermark and clock votes.
- Debug overrides mutate shared SoC state and trigger DML sync. Bad override values can produce persistent validation changes across later modes.
- The code special-cases no-plane validation by capping source dimensions to 1080p; this accepts timing feasibility rather than validating full native source bandwidth.
- The DCN1 watermark range setup mirrors a writer set into reader set slots for B-D, which is unusual but consistent with the code. Any cleanup should verify SMU range struct semantics.
- `phyclk_khz` is assigned from `v->phyclk_per_state[v->voltage_level]` without multiplying by 1000, unlike other clock fields; because this is existing code, changing it requires hardware validation.

## Test Signals

Useful validation signals include:

- Mode validation tests across no-plane, single-plane, multi-plane, stereo, rotated, YUV420, high-bpp RGB, DCC-enabled/disabled, and split-pipe cases.
- Debug policy tests for `MPC_SPLIT_AVOID`, `MPC_SPLIT_AVOID_MULT_DISP`, `force_single_disp_pipe_split`, tiny plane dimensions, and min/max DISP/DPP clock overrides.
- ASIC-specific tests for RV1 F0, RV2/DCN_VERSION_1_01, single-channel memory, and vmin-only ASIC behavior.
- Watermark regression checks comparing `context->bw_ctx.bw.dcn.watermarks` and `pipe_ctx` DLG/RQ/TTU registers against known-good DML/spreadsheet results.
- SMU/PPLIB integration tests verifying FCLK/DCFCLK updates and submitted watermark ranges.
- Kernel warning/assert coverage for unsupported swizzles, missing secondary split pipes, and invalid scaler identity assumptions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/calcs/dcn_calcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dc_features.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dc_features.h

## Purpose

`dc_features.h` is a compile-time feature and capacity definition header for AMD display core/DML. It enumerates the local DC hardware feature shape visible to DML and related display code: counts of DPP/OPP/OTG/DIG/AUX/audio/PHY resources, maximum array dimensions, feature-presence booleans, sync cell parameters, memory power-gating flags, and top-block presence flags.

The header has no executable logic. Its purpose is to give DML and generated display-mode code fixed preprocessor constants for sizing arrays and compiling feature-specific branches.

## Important APIs, Types, And Macros

There are no functions or types. Important macro groups include:

- Core presence/capacity: `DC__PRESENT`, `DC__NUM_DPP`, `DC__NUM_DPP__MAX`, `DC__NUM_OPP`, `DC__NUM_OTG`, `DC__NUM_PIPES`, `DC__VOLTAGE_STATES`.
- Display engine resources: DPP, OPP, DSC, ABM, ODM, OTG, DWB/CWB, DIG, AUX, HPD, DDC, cursor, PHY, and low-power PHY/DIG variants.
- Audio resources: `DC__NUM_AUDIO_STREAMS`, `DC__NUM_AUDIO_ENDPOINTS`, input stream/endpoint counts, audio PLL count.
- Link/output feature flags: HDMI, DP, MST, low-power DP/HDMI/MST, DSI, DAC/DVO, TMDS link type, PHY broadcast, UNIPHY presence, UNIPHY voltage/stagger flags.
- FIFO/sync parameters: digital/DAC/DVO resync FIFO sizes, sync cell choice, latch counts for DISPCLK, DVOCLK, PIXCLK, SYMCLK, DPPCLK, DPREFCLK, REFCLK, PCIE_REFCLK, MVPCLK, SCLK, DCEFCLK, AMCLK, DSICLK, BYTECLK, ESCCLK, and DB clock.
- Memory power-gating flags: `DC__MEM_PG`, block-specific `*_MEM_PG` definitions for DP, AFMT, HDMI, I2C, DSCL, CM, OBUF, WBIF, VGA, FMT, ODM, DSI, AZ, WBSCL memories, DMCU memory, and HUBBUB/HUBPREQ/HUBPRET memories.
- Top block presence: `DC__TOP_BLKS__DCCG`, `DCHUBBUB`, `DCHUBP`, `HDA`, `DIO`, `DCIO`, `DMU`, `DPP`, `MPC`, `OPP`, `OPTC`, `MMHUBBUB`, `WB`, plus max count.
- DML sizing constants consumed elsewhere: `DC__VOLTAGE_STATES` is used for clock-limit arrays, and `DC__NUM_DPP__MAX`, `DC__NUM_CURSOR__MAX`, and `DC__NUM_PIPES__MAX` are used heavily in DML/VBA arrays.

The header also emits value-specific macros such as `DC__NUM_DPP__4`, `DC__NUM_DPP__0_PRESENT`, and `DC__NUM_DPP__MAX__8`, allowing generated code to test either a current value or a supported maximum.

## Control Flow

There is no runtime control flow. Inclusion of this header affects compilation by:

1. Defining exact local feature values, such as four DPPs and four pipes.
2. Defining maximum limits, such as eight maximum DPPs and forty voltage states.
3. Enabling or disabling generated branches through `*_PRESENT` and value-specific macros.
4. Sizing static arrays in DML structures and utility code.

## State And Persistence Behavior

This header holds no runtime state and performs no persistence. The macros become compile-time constants in any translation unit that includes them directly or indirectly. Any change requires recompilation and can alter ABI-like assumptions for structs containing macro-sized arrays.

## Dependencies And Integration Points

`dc_features.h` is an input to DML and display-mode generated code. Repository references show these macros in:

- `dc.h` and `display_mode_structs.h` for `clock_limits[DC__VOLTAGE_STATES]`.
- DML VBA headers and source for arrays sized by `DC__NUM_DPP__MAX`, `DC__NUM_CURSOR__MAX`, `DC__NUM_PIPES__MAX`, and `DC__VOLTAGE_STATES`.
- DCN resource/FPU code that constructs clock tables bounded by `DC__VOLTAGE_STATES`.

The header must stay consistent with hardware resource pools and generated DML model expectations. If hardware support grows, both the current counts and max dimensions may need coordinated updates.

## Risks And Edge Cases

- These macros size stack and struct arrays. Lowering max values can create compile errors or memory corruption if loops elsewhere still assume larger generated limits.
- Raising current resource counts without matching real resource-pool construction can make validation accept configurations the driver cannot program.
- Raising max counts can increase stack usage in generated DML functions with large local arrays.
- Value-specific flags such as `DC__NUM_DPP__4` and `DC__NUM_DPP__MAX__8` can become inconsistent with the base numeric macro if hand-edited.
- Several feature flags are zero despite corresponding max counts being nonzero. Code must distinguish "present now" from "maximum supported by generated model."
- Because this header is broad and generated-looking, unrelated display code can acquire hidden dependencies on specific values; small changes should be treated as platform-wide.

## Test Signals

Useful validation signals include:

- Full display driver build coverage after any macro change, especially DML generated sources that instantiate macro-sized arrays.
- Static analysis for loops bounded by resource pool counts versus macro max counts.
- Boot/display smoke tests confirming the resource pool count matches macro-advertised current counts.
- Mode validation stress tests with maximum DPP/pipe/cursor paths after increasing any max macro.
- ABI/structure layout checks for DML structs if out-of-tree or firmware-facing code consumes the same definitions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dc_features.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn10/dcn10_fpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn10/dcn10_fpu.c

## Purpose

`dcn10_fpu.c` centralizes DCN1.0 code that touches floating-point state. AMD display mode calculations use floating-point values in kernel code, so this file follows the DC FPU isolation pattern: public functions must be called while FPU access is already enabled by the caller, and they assert that condition with `dc_assert_fp_enabled()`.

Functionally, this file provides DCN1.0 DML IP and SoC bounding-box defaults and a construction-time adjustment function for Raven/DCN1 variants.

## Important APIs, Types, And Data

Exported data:

- `dcn1_0_ip`: DML `_vcs_dpi_ip_params_st` defaults for DCN1.0, including buffer sizes, chunk sizes, line-buffer limits, DPP/writeback counts, scaler throughput, scaler ratios/taps, timing delays, underscan, minimum vblank, and DCFCLK cstate latency.
- `dcn1_0_soc`: DML `_vcs_dpi_soc_bounding_box_st` defaults for DCN1.0, including SR/urgent/writeback latencies, DRAM bandwidth policy, request size, DRAM timing, channel/bank configuration, page size, clock-change latency, and return bus width.

Exported function:

- `dcn10_resource_construct_fp(struct dc *dc)`: applies construction-time floating-point DCN1 resource adjustments to `dc->dcn_soc`, `dc->dcn_ip`, `dc->dml`, and debug flags.

## Control Flow

`dcn10_resource_construct_fp` performs a small sequence of ASIC-specific adjustments:

1. It asserts FPU access is enabled.
2. For `DCN_VERSION_1_01`, it reduces the DPP count to three in both DML IP and DCN IP data, and changes DRAM clock-change latency to 23 microseconds.
3. For `ASICREV_IS_RV1_F0`, it lowers urgent latency, disables DMCU through `dc->debug.disable_dmcu`, and adjusts maximum fabric/DRAM bandwidth.
4. It derives `dc->dcn_soc->number_of_channels` from `asic_id.vram_width / ddr4_dram_width`, asserts the result is less than three, and works around old SBIOS data that reports zero channels by forcing two.
5. For single-channel memory, it rewrites fabric/DRAM bandwidth values to single-channel limits, with a separate RV1 F0 maximum.

There are no loops beyond the simple conditional flow and no calls into the generated DML equations.

## State And Persistence Behavior

The function mutates in-memory driver state during resource construction:

- `dc->dml.ip.max_num_dpp`
- `dc->dcn_soc->dram_clock_change_latency`
- `dc->dcn_ip->max_num_dpp`
- `dc->dcn_soc->urgent_latency`
- `dc->debug.disable_dmcu`
- `dc->dcn_soc->fabric_and_dram_bandwidth_*`
- `dc->dcn_soc->number_of_channels`

The file has no disk persistence and allocates no memory. The global `dcn1_0_ip` and `dcn1_0_soc` structures are mutable globals by type, though this file itself only writes through the `dc` instance passed into the function.

## Dependencies And Integration Points

Direct dependencies:

- `dcn10/dcn10_resource.h` for DCN1 resource definitions, ASIC revision helpers, and constants such as `ddr4_dram_width`.
- `resource.h` and `struct dc` state.
- `amdgpu_dm/dc_fpu.h` for `dc_assert_fp_enabled`.

Integration points:

- Called from DCN1 resource construction code after the caller has entered the DC FPU critical section.
- The DML and legacy bandwidth paths later consume the adjusted `dc->dml`, `dc->dcn_soc`, and `dc->dcn_ip` values during mode validation and watermark calculation.
- Debug behavior is affected through `dc->debug.disable_dmcu`.

## Risks And Edge Cases

- The function assumes the caller enabled FPU access. Calling it outside the FPU-protected region triggers a warning/assert path and risks illegal kernel FPU use.
- `number_of_channels` depends on firmware-reported `vram_width`; bad firmware is partly handled for zero channels but not for other unexpected values except an assert for values >= 3.
- The DCN_VERSION_1_01 branch changes both DML and legacy DCN IP DPP counts; missing one would desynchronize DML validation from resource programming.
- The RV1 F0 and single-channel bandwidth tables are hard-coded. Incorrect ASIC revision detection directly changes mode validation capacity.
- The file-level FPU isolation comment says FPU users should be static/noinline, but the visible public function itself uses floating-point assignments. The actual protection relies on caller-side FPU enable plus `dc_assert_fp_enabled()`.

## Test Signals

Useful validation signals include:

- Construction tests for DCN 1.0, DCN 1.01, RV1 F0, single-channel, dual-channel, and zero-channel firmware cases.
- Assertions/warnings when invoking without DC FPU protection in debug kernels.
- Mode validation comparisons before and after construction to confirm DPP count, latency, and bandwidth values reach DML and legacy calculators.
- Display bring-up on Raven variants that rely on DMCU disable or adjusted urgent latency.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn10/dcn10_fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn10/dcn10_fpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn10/dcn10_fpu.h

## Purpose

`dcn10_fpu.h` declares the public DCN1 FPU-protected helper exported by `dcn10_fpu.c`. It is a narrow interface used by resource construction code that needs the DCN1 floating-point bounding-box adjustment logic without exposing the implementation details or global DML tables through this header.

## Important APIs, Types, And Functions

Declared API:

- `void dcn10_resource_construct_fp(struct dc *dc);`

The header does not include `struct dc` definitions itself, so callers must include an appropriate DC core/resource header before or alongside this header. It uses a conventional include guard `__DCN10_FPU_H__`.

## Control Flow

There is no runtime control flow in the header. It only makes the function prototype visible to translation units that perform DCN1 resource construction or related setup.

## State And Persistence Behavior

The header holds no state and performs no persistence. The declared function mutates `struct dc` state in its implementation, but the header itself does not describe or own that state.

## Dependencies And Integration Points

Integration is intentionally minimal:

- Included by `dcn10_fpu.c` for prototype consistency.
- Expected to be included by DCN1 resource construction code that calls `dcn10_resource_construct_fp`.
- The caller is responsible for ensuring FPU access is enabled before calling, as documented in the `.c` file.

## Risks And Edge Cases

- Because the header does not include or forward-declare `struct dc`, include ordering matters. Existing callers likely already include broader DC headers; new callers must do the same.
- The function name suffix `_fp` communicates FPU requirements but does not enforce them at compile time. Misuse is only caught at runtime by `dc_assert_fp_enabled()` in the implementation.
- Adding more prototypes here should preserve the FPU boundary convention: callers enter/exit FPU protection outside this file, and implementation functions assert that protection.

## Test Signals

Useful validation signals include:

- Compile coverage for all DCN1 resource files that include this header.
- Header self-containment checks if project policy changes to require forward declarations.
- Runtime FPU assertion coverage through the implementation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn10/dcn10_fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/dcn20_fpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/dcn20_fpu.c

## Purpose

`dcn20_fpu.c` centralizes floating-point display mode and bandwidth logic for DCN2.0, DCN2.01, and DCN2.1. It owns DCN2 hardware bounding-box defaults, watermark tables, DML pipe population, DML-based bandwidth validation, watermark/DLG/RQ/TTU calculation, writeback modeling, bounding-box patching from firmware/SMU/debug overrides, and selected DCN2.1 clock-table initialization.

Like `dcn10_fpu.c`, it follows AMD DC's kernel FPU isolation convention: callers must enter the FPU critical section outside this file, and every public function asserts FPU access with `dc_assert_fp_enabled()`.

## Important APIs, Types, And Data

Major global data:

- `dcn2_0_ip`, `dcn2_0_nv14_ip`, `dcn2_1_ip`: DML IP parameter tables for DCN2.0/Navi variants and DCN2.1. They describe DPP/OTG/DSC/writeback counts, VM/PTE capabilities, buffers, chunks, scaler capabilities, cursor buffers, delay values, DCC/XFC support, and cursor count.
- `dcn2_0_soc`, `dcn2_0_nv14_soc`, `dcn2_0_nv12_soc`, `dcn2_1_soc`: DML SoC bounding boxes with clock-limit arrays, voltage states, latency values, bandwidth policy, DRAM/channel configuration, bus widths, clock-change latencies, XFC parameters, and urgent-burst behavior.
- `ddr4_wm_table_gs`, `lpddr4_wm_table_gs`, `lpddr4_wm_table_with_disabled_ppt`, `ddr4_wm_table_rn`, `ddr4_1R_wm_table_rn`, `lpddr4_wm_table_rn`: watermark tables for different platforms/memory configurations.
- `LPDDR_MEM_RETRAIN_LATENCY`: latency constant used for DCN2.1 watermark set D retraining.

Primary exported functions:

- `dcn20_populate_dml_writeback_from_context`: populates one writeback model per active stream, using stream writeback info slot 0.
- `dcn20_fpu_set_wb_arb_params`: calculates MCIF writeback urgent and pstate watermarks and time-per-pixel.
- `dcn20_calculate_dlg_params`: applies DML results to clocks, pipe DLG timing, DET/unbounded request state, MCIF arbitration, RQ/DLG registers, pstate support, compbuf size, and zstate support.
- `dcn20_populate_dml_pipes_from_context`: translates active `pipe_ctx` entries into DML `display_e2e_pipe_params_st`.
- `dcn20_calculate_wm`: calculates DCN2.0 watermarks A-D and required pipe clocks for the selected voltage.
- `dcn20_update_bounding_box`: rebuilds SoC clock limits from SMU max clocks and UCLK states.
- `dcn20_cap_soc_clocks`: caps a bounding box to SMU-reported max clocks and removes duplicate states.
- `dcn20_patch_bounding_box`: applies debug/BB latency overrides to a SoC bounding box.
- `dcn20_validate_bandwidth_fp`: full DCN2.0 validation entry point with dummy-pstate fallback behavior.
- `dcn20_fpu_set_wm_ranges`: fills SMU watermark range fill-clock bounds for a table entry.
- `dcn20_fpu_adjust_dppclk`: doubles or halves a required DPPCLK entry around validation.
- `dcn21_populate_dml_pipes_from_context`: DCN2.1 wrapper over the DCN2.0 pipe population path that enables hostvm/gpuvm fields.
- `dcn21_validate_bandwidth_fp`: DCN2.1 validation entry point.
- `dcn21_update_bw_bounding_box_fpu`: reconstructs DCN2.1 DML clock limits from `clk_bw_params`, inserts a low DF pstate, updates resource counts, and reinitializes DML.
- `dcn21_clk_mgr_set_bw_params_wm_table`: sets watermark set D as a retraining entry.
- `dcn201_populate_dml_writeback_from_context_fpu`: DCN2.01 writeback population supporting multiple writebacks and selecting worst-case writeback DISPCLK.

Important internal helpers:

- `is_dtbclk_required`: detects DP 128b/132b links and requests DTBCLK.
- `decide_zstate_support`: determines Z8/Z9/Z10 support from plane count, eDP link index, PSR/replay, and DML stutter period.
- `dcn20_adjust_freesync_v_startup`: patches `vstartup_start` for adaptive sync timing on pre-DCN3.1.
- `swizzle_to_dml_params`: maps DC swizzle modes to DML swizzle enums.
- `dcn20_validate_bandwidth_internal`: common DCN2.0 fast-validate plus programming calculation path.
- `patch_bounding_box`, `calculate_wm_set_for_vlevel`, `dcn21_calculate_wm`, and `construct_low_pstate_lvl`: DCN2.1-specific watermark and clock-table helpers.

## Control Flow

The DCN2.0 validation path is:

1. `dcn20_validate_bandwidth_fp` asserts FPU access, copies pstate latency, writes debug DRAM-clock-change policy into `context->bw_ctx.dml.soc`, and asserts it is not mutating `dc->current_state`.
2. Fast validation modes call `dcn20_validate_bandwidth_internal` directly.
3. Programming validation first tries the full DML pstate latency by calling the internal validator.
4. `dcn20_validate_bandwidth_internal` calls `dcn20_fast_validate_bw`, receives pipe count, split mapping, and voltage level, exits early on empty/failed/non-programming cases, and in programming mode calls `dcn20_calculate_wm` followed by `dcn20_calculate_dlg_params`.
5. If full pstate is unsupported and a dummy pstate latency exists, `dcn20_validate_bandwidth_fp` temporarily changes `dram_clock_change_latency_us`, clears the pipe array, reruns internal validation, and accepts the result with `p_state_change_support` forced false when the fallback succeeds.
6. It restores original pstate latency before returning.

`dcn20_populate_dml_pipes_from_context` is the translation front end used by validation:

1. It first determines whether all streams have synchronizable timing/vblank unless debug disables timing sync.
2. For each active pipe, it fills refclk, vblank/active timing, interlace, pixel rate, OTG instance, DSC state, dynamic metadata, vtotal min/max, ODM combine state, hsplit group, output type, output format/bpp, DSC bpp, audio sample rate, cursor count, and default cursor properties.
3. For no-plane pipes, it builds a conservative synthetic source capped to 1920x1080 and adjusts viewport/recout for ODM combine.
4. For real planes, it fills immediate flip, split status, stereo split exceptions, rotation, viewport/surface/pitch/DCC, recout/full recout including split-chain width, scaler ratios/taps, macro tile, DML swizzle, and source pixel format.
5. It delegates writeback population to the resource pool callback.

`dcn20_calculate_wm` uses DML fast-validation results to set per-pipe DISPCLK/DPPCLK and ODM combine, repopulating DML pipes if DML pipe count and pipe index diverge. It then evaluates watermark sets B, C, D, and A by temporarily changing pipe 0 voltage/DCF/SOC clocks and calling DML watermark helper functions.

`dcn20_calculate_dlg_params` applies programmed results: it sets MCIF writeback arbitration, writes selected DML clocks into `context->bw_ctx.bw.dcn.clk`, determines pstate and DTBCLK support, updates per-pipe DPP clocks and `pipe_dlg_param`, handles SubVP phantom DET/unbounded request requirements, computes compbuf size, generates RQ/DLG register values through DML callbacks, and decides zstate support.

DCN2.1 follows the same broad validation structure with `dcn21_fast_validate_bw`, `dcn21_calculate_wm`, and `dcn20_calculate_dlg_params`. Its watermark calculation uses `clk_mgr->bw_params->wm_table` entries and selected voltage levels rather than the DCN2.0 fixed B/C/D sequence.

Bounding-box update flows:

- `dcn20_update_bounding_box` clears clock limits and rebuilds them from UCLK states and SMU max clocks, choosing a minimum DCFCLK, deriving FCLK from UCLK ratio, capping SOCCLK/DCFCLK by SMU maxes, and duplicating the last state for DML.
- `dcn20_cap_soc_clocks` caps existing state clocks to SMU maxes and reduces `num_states` for trailing duplicates.
- `dcn21_update_bw_bounding_box_fpu` maps firmware clock-table entries onto the closest default DCN2.1 DCFCLK level for display-related clocks, inserts a reserved low pstate, duplicates the last level, updates global `dcn2_1_soc`, and reinitializes `dc->dml`.

## State And Persistence Behavior

There is no disk persistence. The file has extensive in-memory state effects:

- Global SoC/IP tables are mutable globals and can be updated, especially `dcn2_1_soc`, `dcn2_1_ip`, and their clock limits/resource counts.
- Validation writes `context->bw_ctx.dml.soc` policy flags and temporarily modifies `dram_clock_change_latency_us`.
- Validation writes `context->bw_ctx.bw.dcn.watermarks`, clock votes, pstate support, DTBCLK enable, zstate support, compbuf size, and bandwidth DPP/DISPCLK snapshots.
- DLG calculation writes each active `pipe_ctx`'s `pipe_dlg_param`, `plane_res.bw.dppclk_khz`, `det_buffer_size_kb`, `unbounded_req`, `dlg_regs`, `ttu_regs`, and `rq_regs`.
- Pipe population mutates only the caller-provided `pipes` array, except through delegated writeback callbacks.
- Bounding-box patch functions mutate passed bounding boxes and, for DCN2.1, `dc->clk_mgr->bw_params->wm_table`.
- `dcn21_update_bw_bounding_box_fpu` uses `dc->scratch.update_bw_bounding_box.clock_limits` as a staging buffer and calls `dml_init_instance` to reinitialize the display mode library.

All public functions assume caller-managed FPU lifetime. They do not call `DC_FP_START` or `DC_FP_END`.

## Dependencies And Integration Points

Direct dependencies include:

- Display resource/clock/link/core state: `resource.h`, `clk_mgr.h`, `dchubbub.h`, `link_service.h`, `dc_state_priv.h`.
- DCN2.0/DCN2.1 resource headers for platform-specific pools and fast validation.
- `dcn20_fpu.h` for exported prototypes.
- DML helpers such as `get_wm_urgent`, `get_wm_stutter_exit`, `get_wm_dram_clock_change`, `get_vstartup`, `CalculateWriteBackDISPCLK`, `dml_get_status_message`, and DML RQ/DLG callbacks through `context->bw_ctx.dml.funcs`.
- Resource pool callbacks: `set_mcif_arb_params`, `populate_dml_writeback_from_context`, and optional `populate_dml_pipes`.
- Link service callback `dp_is_128b_132b_signal`, audio helper `get_audio_check`, resource helper `resource_get_odm_slice_count`, and SubVP helper `dc_state_get_pipe_subvp_type`.
- SMU/firmware clock structures: `pp_smu_nv_clock_table`, `clk_bw_params`, `clk_limit_table`, `wm_table`, and `pp_smu_wm_range_sets`.

Repository call sites show these functions are integrated from DCN20/DCN21 resource validation and bounding-box update code, and newer DCN resource files reuse `dcn20_patch_bounding_box`.

## Risks And Edge Cases

- Every public entry point requires active kernel FPU protection. Runtime assertions catch misuse, but the type system does not.
- The validation code asserts `context != dc->current_state` because current pipe merge/split logic is unsafe for in-place current-state mutation. Violating this can corrupt live display state.
- `dcn20_populate_dml_writeback_from_context` takes `&res_ctx->pipe_ctx[i].stream->writeback_info[0]` before checking `stream` for null, which is a latent null-deref risk if evaluated by the compiler before the later guard. The DCN2.01 version avoids this by checking `stream` first.
- DML pipe population assumes several nested resource pointers exist for active streams and planes, including timing generator, scaler data, link/sink for eDP zstate logic, and plane size/pitch metadata.
- Many calculations use pipe index and DML pipe index mappings (`pipe_split_from`, `pipe_idx`, `pipe_cnt`). Off-by-one or split-chain divergence can assign clocks or ODM combine settings to the wrong pipe.
- DCN2.0 watermark set D uses clock limit index 2 when `vlevel < 3`, which may be intentional but is fragile around low `num_states`.
- Bounding-box updates assume `num_states > 0`; they guard zero in `dcn20_update_bounding_box`, but duplicate-last-state logic depends on arrays sized for one extra state.
- `dcn20_cap_soc_clocks` reduces only `num_states` for duplicates; stale entries remain in the array but should be ignored. Consumers must honor `num_states`.
- DCN2.1 updates mutate global `dcn2_1_soc` and `dcn2_1_ip`, so multi-device or reinitialization scenarios must ensure the globals are safe for the driver architecture.
- `construct_low_pstate_lvl` increments `clk_table->num_entries` and shifts entries in place; callers must ensure capacity in the clock table.
- Several platform tables encode hard-coded latency and clock values. Wrong ASIC/memory table selection causes validation errors, underflow, flicker, or excessive power.

## Test Signals

Useful validation signals include:

- Mode validation coverage for DCN2.0, DCN2.01, and DCN2.1 in fast and programming modes.
- Regression tests for full pstate support, dummy pstate fallback, no-stream/no-plane cases, and empty `pipe_cnt`.
- DML pipe population tests across DP, DP2 128b/132b, eDP, HDMI/DVI, virtual outputs, DSC, dynamic metadata, RGB/YUV420/YUV422, high bpc, immediate flip, DCC, rotations, ODM 2:1/4:1, MPC splits, stereo exceptions, SubVP phantom pipes, and video planes with cursor disabled.
- Writeback tests for single writeback, multiple writebacks on DCN2.01, crop versus source dimensions, YUV420 8/10 bpc, and worst-case writeback DISPCLK selection.
- Bounding-box tests with zero UCLK states, capped SMU clocks, duplicate clock states, Navi12 min DCFCLK behavior, debug latency overrides, and DCN2.1 low-pstate insertion.
- Watermark tests comparing A-D watermark fields against known DML reference outputs for DDR4/LPDDR4/Renoir/green sardine tables.
- Runtime assertions for FPU protection and `context != dc->current_state`.
- Display bring-up and power-management tests checking pstate switch support, zstate support, DTBCLK enable for DP2, and FreeSync vstartup adjustment.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/dcn20_fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/dcn20_fpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/dcn20_fpu.h

## Purpose

`dcn20_fpu.h` declares the FPU-protected DCN2.0/DCN2.01/DCN2.1 DML and bandwidth helper interfaces implemented in `dcn20_fpu.c`. It is the integration boundary used by resource, clock-manager, and writeback code that must call into floating-point DML logic while keeping FPU-sensitive implementation details centralized.

## Important APIs, Types, And Functions

The header includes `core_types.h`, which supplies many of the display core type declarations used in the prototypes. Declared APIs include:

- Writeback modeling: `dcn20_populate_dml_writeback_from_context`, `dcn201_populate_dml_writeback_from_context_fpu`.
- Writeback arbitration: `dcn20_fpu_set_wb_arb_params`.
- DLG and watermark programming: `dcn20_calculate_dlg_params`, `dcn20_calculate_wm`.
- DML pipe translation: `dcn20_populate_dml_pipes_from_context`, `dcn21_populate_dml_pipes_from_context`.
- Bounding-box and clock table updates: `dcn20_cap_soc_clocks`, `dcn20_update_bounding_box`, `dcn20_patch_bounding_box`, `dcn21_update_bw_bounding_box_fpu`, `dcn21_clk_mgr_set_bw_params_wm_table`.
- Bandwidth validation entry points: `dcn20_validate_bandwidth_fp`, `dcn21_validate_bandwidth_fp`.
- SMU/DML adjustment helpers: `dcn20_fpu_set_wm_ranges`, `dcn20_fpu_adjust_dppclk`.

The prototypes expose several cross-subsystem structures: `struct dc`, `struct dc_state`, `struct resource_context`, `struct mcif_arb_params`, `display_e2e_pipe_params_st`, `struct _vcs_dpi_soc_bounding_box_st`, `struct pp_smu_nv_clock_table`, `struct pp_smu_wm_range_sets`, `struct vba_vars_st`, and `struct clk_bw_params`.

## Control Flow

The header itself has no runtime control flow. It enables resource-layer code to call into these flows:

1. Populate DML pipes from a proposed `dc_state`.
2. Run DCN2 bandwidth validation.
3. Calculate watermarks and DLG/RQ/TTU programming data.
4. Update SoC bounding boxes from firmware/SMU clock data.
5. Populate SMU watermark ranges and writeback arbitration parameters.

## State And Persistence Behavior

The header owns no state. The declared functions mutate display driver state in their implementation, especially `context->bw_ctx`, `context->res_ctx.pipe_ctx`, DML bounding boxes, clock-manager bandwidth parameters, and caller-provided pipe arrays. There is no disk persistence.

## Dependencies And Integration Points

This header is included by:

- `dcn20_fpu.c` for prototype consistency.
- DCN20/DCN21 resource files that call validation, bounding-box update, watermark range, and writeback helpers.
- DCN201 resource code for the DCN2.01 writeback-specific helper.
- Newer DCN resource files that reuse the generic `dcn20_patch_bounding_box`.

The header is part of the FPU boundary. Callers must wrap calls with the display core FPU protection mechanism before entering these APIs.

## Risks And Edge Cases

- The `_fp` suffix is a convention, not compile-time enforcement. Incorrect caller-side FPU handling is caught only by implementation assertions.
- Prototypes expose DML-internal types, so changes to DML struct names or include paths ripple into resource code.
- Some functions are DCN2.0-specific while others apply to DCN2.1 or DCN2.01. Calling the wrong helper for a resource generation can silently produce invalid DML modeling.
- `dcn20_fpu_adjust_dppclk` mutates DML VBA arrays in place; callers must pair validation/non-validation adjustment correctly to avoid leaving doubled or halved clocks.
- Header include order is partly covered by `core_types.h`, but callers may still need generation-specific headers for complete definitions.

## Test Signals

Useful validation signals include:

- Compile coverage for all resource files that include this header.
- Link coverage ensuring every declared symbol remains implemented when DCN generation configs are enabled.
- Runtime FPU assertion tests through representative callers.
- Cross-generation validation tests confirming DCN20, DCN201, and DCN21 resource code dispatches to the correct declared helper.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/dcn20_fpu.h -->
