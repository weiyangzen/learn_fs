# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_dpmm/dml2_dpmm_dcn4.c

## Purpose
Implements DCN3/DCN4/DCN42 display power management mapping. It converts core mode-support bandwidth/latency results into SoC DPM clock requests, rounds those requests to DPM table or DFS granularity, decides p-state and stutter feature support, and maps core watermarks into DCHUB register sets.

## Important APIs, types, and functions
- `dpmm_dcn3_map_mode_to_soc_dpm()` and `dpmm_dcn4_map_mode_to_soc_dpm()` are exported clock/power-feature mappers.
- `dpmm_dcn4_map_watermarks()` emits two DCHUB watermark sets from `mode_lib->mp.Watermark` and urgent bandwidth fractions.
- `dpmm_dcn42_map_watermarks()` emits four identical watermark sets for DCN42.
- `dram_bw_kbps_to_uclk_khz()` converts bandwidth to UCLK using DRAM geometry or an alternate bandwidth-to-clock table.
- `calculate_system_active_minimums()`, `calculate_svp_prefetch_minimums()`, and `calculate_idle_minimums()` compute UCLK/FCLK/DCFCLK requirements from active, SVP-prefetch, and idle bandwidth domains plus latency floor.
- `map_min_clocks_to_dpm()` chooses fine-grained or coarse-grained mapping and rounds global, per-plane DPPCLK, and per-stream DSC/DTB/PHY clocks.
- `add_margin_and_round_to_dfs_grainularity()`, `round_to_non_dfs_granularity()`, `round_up_and_copy_to_next_dpm()`, and `round_up_to_next_dpm()` implement clock quantization.
- `are_timings_trivially_synchronizable()`, `find_smallest_idle_time_in_vblank_us()`, and power-management feature helpers decide whether UCLK/FCLK p-state changes can be supported through blank/vactive/FAMS margin.

## Control flow and integration
The common `map_mode_to_soc_dpm()` first calculates active/SVP/idle minimums, boosts active clocks to prefetch requirements for NV4-like constraints, computes DISPCLK/DPPREFCLK/DTBREFCLK with downspread and ramp margins, rounds with DFS or non-DFS rules, derives per-plane DPPCLK ratios, copies deepsleep DCFCLK/SOCCLK, and maps all clocks to the SoC table. DCN3 then tries vblank, vactive+vblank, and FAMS-based p-state support before clamping unsupported UCLK/FCLK to max. DCN4 trusts successful stage3 for UCLK p-state, evaluates FCLK via vactive/vblank margin, clamps unsupported clocks, and evaluates stutter/Z8 blank support.

## State and persistence behavior
All state is written into caller-owned `dml2_display_cfg_programming`: `min_clocks.dcn4x`, per-plane/per-stream min clocks, p-state support booleans, stutter/Z8 support flags, global watermark register sets, and watermark-set count. Inputs are `display_cfg` mode-support results, SoC bounding box, min-clock table, IP params, and core mode-lib.

## Dependencies
Includes DPMM and internal shared types, top DML types, and float math. It consumes `dml2_core_mode_support_result`, `dml2_soc_state_table`, `dml2_mcg_min_clock_table`, `dml2_dram_params`, DCHUB global register sets, and core mode-lib watermark fields.

## Risks and edge cases
Clock table handling is sensitive. `round_up_and_copy_to_next_dpm()` includes a guard for zero-entry clock tables, avoiding an unsigned wrap/out-of-bounds read for absent clocks such as tied-off DTBCLK; similar code should preserve that behavior. Coarse-grained mapping assumes aligned UCLK/FCLK/DCFCLK table indices. `get_displays_with_fams_mask()` indexes `plane_descriptors->overrides` instead of `plane_descriptors[i].overrides`, which means it checks the first plane repeatedly and may under/over-report FAMS coverage. Watermark conversion truncates doubles to unsigned ref cycles.

## Test signals
Tests should cover fine-grained and coarse-grained clock tables, zero-entry optional clocks with zero and non-zero requested values, alternate DRAM bandwidth conversion, DFS and no-DFS rounding, downspread/ramp margin clamping, SVP prefetch boosting, p-state clamping paths, vblank/vactive support paths, all-stream timing sync/DRR cases, and DCN4 versus DCN42 watermark-set counts.
