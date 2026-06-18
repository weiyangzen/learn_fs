# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_28nm_8960.xml

## Purpose
This XML defines the 28nm DSI PHY variant used by MSM8960-era hardware. It is a reduced/specialized D-PHY map with four data lanes, a clock lane, timing registers, control/strength registers, BIST controls, and LDO control, but without the standard 28nm regulator and PLL domains in this file.

## Important APIs, Types, and Functions
Generated macros use the `DSI_28nm_8960_PHY` domain and include lane array registers `LN_CFG_*`, `LN_TEST_*`, clock-lane `LNCK_*`, timing controls for clock/HS/TA transitions, `CTRL_0` through `CTRL_3`, `STRENGTH_0` through `STRENGTH_2`, BIST controls, and `LDO_CTRL`. Timing fields mirror the older 20nm/28nm-style names such as `CLK_ZERO`, `CLK_TRAIL`, `CLK_PREPARE`, `HS_EXIT`, `HS_ZERO`, `HS_PREPARE`, `HS_TRAIL`, `HS_RQST`, `TA_GO`, `TA_SURE`, `TA_GET`, and `TRIG3_CMD`.

## Control Flow
The 8960 PHY driver programs data lanes, the dedicated clock lane, timing counters, strength values, and LDO control as part of DSI host enable. Since PLL/regulator details are not represented as separate domains here, those controls are either external to this map or handled by 8960-specific code paths.

## State and Persistence Behavior
The described state is volatile lane, timing, strength, BIST, and LDO hardware state. It is tied to the active DSI mode and must be restored whenever the display pipeline is powered back up.

## Dependencies and Integration Points
It integrates with legacy MSM8960 DSI PHY support, DSI host timing calculation, panel enable/disable sequences, and platform-specific clock/regulator setup. It must remain separate from the standard `DSI_28nm_PHY` map because offsets and available registers differ.

## Risks
The similarity to standard 28nm and 20nm maps can hide subtle offset/register-count differences. The missing PLL domain means tests that only validate generated symbols may not cover full clock bring-up. Misprogramming strength or LDO settings can cause marginal panels that fail only under temperature, voltage, or high bit-rate conditions.

## Test Signals
Useful coverage includes generated macro checks, MSM8960 panel bring-up, lane-count modes, repeated power cycles, suspend/resume, DSI command/video mode validation, and timing stress near maximum supported lane rates.
