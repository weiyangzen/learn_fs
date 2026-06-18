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
