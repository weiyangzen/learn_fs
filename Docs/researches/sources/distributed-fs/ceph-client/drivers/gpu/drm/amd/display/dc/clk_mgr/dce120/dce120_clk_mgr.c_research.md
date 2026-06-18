# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce120/dce120_clk_mgr.c

## Purpose
This file specializes clock management for DCE12/Vega-era hardware, including separate display PHY voltage requests and Vega20 DCE12.1 XGMI spread-spectrum handling.

## Important APIs, Types, And Functions
- `dce121_clock_patch_xgmi_ss_info()` reads XGMI spread-spectrum info and reuses it for DPREFCLK adjustment when XGMI is enabled.
- `dce12_update_clocks()` programs display clock through DCE112 helpers, sends PP clock-for-voltage requests for display and PHY clocks, and applies DCE11 display requirements.
- `dce120_clk_mgr_construct()` initializes DCE12 defaults and sets a 600 MHz DPREFCLK.
- `dce121_clk_mgr_construct()` adjusts DPREFCLK to 625 MHz and patches XGMI spread-spectrum info when hardware sequence reports XGMI enabled.

## Control Flow
The update path patches display clock by 115% when DFS bypass is inactive, optionally spread-spectrum adjusts it for XGMI, programs the display clock, requests display-clock voltage, then independently requests PHY clock voltage based on the max pixel/symbol clock across paths.

## State And Persistence
Persistent manager state includes DCE12 max clock limits, base DPREFCLK, XGMI enable state, and spread-spectrum fields. Runtime updates mutate `base.clks.dispclk_khz`, `base.clks.phyclk_khz`, and PP display configuration state.

## Dependencies And Integration Points
It depends on DCE112 clock setters, DCE110 PPLIB display requirement helpers, DCE100 shared helpers, VBIOS spread-spectrum queries, PP clock-for-voltage APIs, and `dce121_xgmi_enabled()` from DCE120 HW sequence.

## Risks
XGMI spread-spectrum data intentionally overwrites DPREFCLK SS values, which can affect audio/display clock adjustment. Display and PHY voltage requests are separate, so missed `should_set_clock()` transitions can leave stale PP voltage requests. The 115% workaround continues to affect power.

## Test Signals
Validate Vega10 and Vega20 constructor selection, DPREFCLK values, XGMI-enabled spread-spectrum behavior, display/PHY voltage requests, multi-display PHY clock requirements, and DP audio/link stability.
