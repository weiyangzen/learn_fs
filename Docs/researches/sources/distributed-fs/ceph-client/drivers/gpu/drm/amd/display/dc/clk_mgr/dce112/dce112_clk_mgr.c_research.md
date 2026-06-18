# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce112/dce112_clk_mgr.c

## Purpose
This file specializes the DCE clock manager for DCE11.2/Polaris-era hardware, using `SetDCEClock` VBIOS commands for display clock and DP reference clock programming.

## Important APIs, Types, And Functions
- `dce112_set_clock()` programs display clock then programs DPREFCLK in one combined flow.
- `dce112_set_dispclk()` programs only display clock and updates DMCU PSR wait-loop timing.
- `dce112_set_dprefclk()` programs only DPREFCLK and returns the VBIOS-selected target.
- `dce112_update_clocks()` applies PP state changes, sets the patched display clock, and applies DCE11 PPLIB display requirements.
- `dce112_clk_mgr_construct()` builds on the common DCE constructor and installs DCE11.2 registers, clock limits, and functions.

## Control Flow
Display clock programming builds `bp_set_dce_clock_parameters` with `CLOCK_SOURCE_ID_DFS` and `DCECLOCK_TYPE_DISPLAY_CLOCK`, enforcing a minimum dentist VCO divider threshold. DPREFCLK programming passes a zero target and `DCECLOCK_TYPE_DPREFCLK`, allowing VBIOS to choose the frequency, with genlock-source flags disabled for Vega20.

## State And Persistence
The manager stores DCE11.2 max clocks and register tables. Runtime programming updates `cur_min_clks_state`, `dfs_bypass_disp_clk`, `base.clks.dispclk_khz`, and DMCU PSR wait-loop timing.

## Dependencies And Integration Points
Dependencies include DCE11.2 registers, common DCE helpers, DCE110 display requirements, ASIC ID macros, VBIOS `set_dce_clock`, PPLIB, and DMCU.

## Risks
The combined `dce112_set_clock()` always follows display clock programming with DPREFCLK programming, which may have side effects on link/audio timing. The 115% workaround remains in the update path. Minimum divider threshold differs from the older `/64` logic. Vega20 exception handling must align with DCE120/DCE121 behavior.

## Test Signals
Validate display clock readback, DPREFCLK stability, PSR timing, VegaM/Polaris constructor selection, safe-to-lower transitions, and DP audio/link behavior after clock changes.
