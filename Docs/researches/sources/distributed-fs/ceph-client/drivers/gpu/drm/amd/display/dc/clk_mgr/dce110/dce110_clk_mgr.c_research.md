# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce110/dce110_clk_mgr.c

## Purpose
This file specializes the common DCE clock manager for DCE110/CZ-era hardware with DCE11 register definitions, clock-state limits, display-configuration reporting, and PPLIB requirement programming.

## Important APIs, Types, And Functions
- `determine_sclk_from_bounding_box()` selects an SCLK level from `dc->sclk_lvls`.
- `dce110_get_min_vblank_time_us()` calculates the minimum vblank duration across streams.
- `dce110_fill_display_configs()` populates `dm_pp_display_configuration` per active stream.
- `dce11_pplib_apply_display_requirements()` fills power-management requirements including memory/engine clocks and display configs.
- `dce11_update_clocks()` applies PP clock-state changes, programs display clock with a 115% workaround when DFS bypass is inactive, and sends PPLIB requirements.
- `dce110_clk_mgr_construct()` builds on `dce_clk_mgr_construct()` and overrides registers, max clock table, and function pointers.

## Control Flow
The update path computes a patched display clock, requests the required PP power state if safe or necessary, calls `dce_set_clock()` when needed, stores the current display clock, and applies display requirements. Display config filling scans streams, finds their pipe contexts, skips DPMS-off streams, and records signal/link/timing metadata for PPLIB.

## State And Persistence
Persistent state includes the DCE110 max clock table and function table in `clk_mgr_internal`. Runtime updates mutate `cur_min_clks_state`, `base.clks.dispclk_khz`, and `context->pp_display_cfg`.

## Dependencies And Integration Points
Dependencies include DCE11 register definitions, common DCE clock manager utilities, PPLIB, bandwidth context, link settings, timing generators, and ASIC ID/memory type information. It is reused by DCE112 and DCE120 via exported display requirement helpers.

## Risks
The 115% patched display-clock workaround can over-request clocks and affects power. Display config filling asserts a pipe context exists for each stream; malformed state can trip assertions. Memory clock calculations depend on VBIOS bandwidth data and special Vega20/HBM handling.

## Test Signals
Validate PPLIB display configs for multi-display, DPMS-off, varying link settings, HBM/Vega20 cases, and safe-to-lower transitions. Check actual display clock, SCLK/MCLK requests, and vblank-derived switch time.
