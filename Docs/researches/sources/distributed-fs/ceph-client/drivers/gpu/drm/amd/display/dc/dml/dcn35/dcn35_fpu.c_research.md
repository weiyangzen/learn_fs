# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn35/dcn35_fpu.c

## Purpose
This file supplies DCN3.5 DML FPU support: static IP/SOC bounding boxes, runtime bounding-box updates from clock tables and overrides, per-context DML pipe adjustment, and z-state support decisions. It adapts DCN31-era DML pipe population for DCN35-specific timing, DET, immediate-flip, DSC, and low-power policy.

## Important APIs, Types, And Functions
`dcn3_5_ip` defines DCN35 hardware limits and DML knobs, including HostVM/GPUVM, ROB/DET/config return buffer, chunk/meta sizes, DSC support, line buffer, DPP/OTG counts, scaler limits, DPTE buffers, delays, DCC, and default vblank target. `dcn3_5_soc` defines default clock states, latency, bandwidth percentage, page size, bus width, and spread values. Public functions are `dcn35_build_wm_range_table_fpu()` (currently TODO/no-op), `dcn35_update_bw_bounding_box_fpu()`, `dcn35_populate_dml_pipes_from_context_fpu()`, and `dcn35_decide_zstate_support()`. Private helpers detect dual-plane formats and convert microseconds to vertical lines/back porch.

## Control Flow And State
The bounding-box update asserts FPU availability, adjusts DPP/OTG counts from the resource pool, sets channel count from `bw_params`, derives max DISPCLK/DPPCLK from the SMU clock table, maps each runtime entry to the closest static voltage level, copies voltage-dependent and independent clocks into scratch `clock_limits`, applies latency overrides, reinitializes DML as `DML_PROJECT_DCN31`, and mirrors clock/latency data into DML2 override structures when enough clock entries exist. Pipe population first calls `dcn31_populate_dml_pipes_from_context()`, then clamps `vblank_nom`, detects upscaling, forces immediate flip support, disables unbounded request by default, zeros DCC fractions, sets vfront porch/DCC rate/GPUVM min page size, derives DSC input bpc from timing color depth, adjusts DET size, optionally enables unbounded request for a single non-dual-plane <=5K surface, and applies seamless boot ODM policy. Z-state policy counts planes and allows deeper states primarily for no-plane cases or single eDP with PSR/replay and sufficient stutter residency.

## State And Persistence Behavior
The file mutates global `dcn3_5_ip` and `dcn3_5_soc`, `dc->scratch.update_bw_bounding_box.clock_limits`, `dc->dml`, `dc->dml2_options.bbox_overrides`, `context->bw_ctx.dml.ip`, `pipes[]`, `context->bw_ctx.dml.vba.ODMCombinePolicy`, and `context->bw_ctx.bw.dcn.clk.zstate_support`. These updates are runtime state and may vary with clock table, debug flags, stream timing, plane format, and boot optimization flags.

## Dependencies And Integration Points
The file includes resource headers for DCN31/DCN32/DCN35, `dml/dcn31/dcn31_fpu.h`, `dml_inline_defs.h`, and `link_service.h`. It depends on `clk_bw_params`, `dc_state`, `pipe_ctx`, stream timing, debug settings, PSR/replay link state, and DML structs from `display_mode_structs.h`. Resource-layer function tables call these hooks for DCN35 validation and bandwidth setup.

## Risks
`dcn35_build_wm_range_table_fpu()` is a TODO, so callers must not rely on it for real watermark range construction. The update path asserts clock entries exist and copies into fixed-size global arrays; invalid SMU table counts can be dangerous. `pipe` is used after the population loop for single-pipe DET decisions and assumes at least one active pipe. Immediate flip is forced for all active pipes to avoid intermittent underflow, which can raise bandwidth requirements. Z-state behavior depends on stutter period, link index, PSR/replay flags, and debug residency thresholds.

## Test Signals
Important signals include DML/DML2 clock table contents, DET size selected per context, `vblank_nom` clamping, DSC input bpc selection, immediate flip validation, unbounded request enablement for single 5K-or-less RGB surfaces, seamless boot ODM selection, and z-state support logged against stutter period. Tests should cover one SMU clock entry, multiple clock entries, latency overrides, eDP PSR/replay, no-plane/no-stream cases, multi-display with upscaling, dual-plane formats, and DSC color depths.
