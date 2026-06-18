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
