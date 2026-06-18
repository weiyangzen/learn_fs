# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_28nm.xml

## Purpose
This XML describes the standard 28nm DSI PHY, its regulator block, and its PLL block. It covers four data lanes, a clock lane, D-PHY timing/control/strength/BIST registers, regulator calibration/power controls, and PLL programming for the DSI serial clock.

## Important APIs, Types, and Functions
Generated APIs include `REG_DSI_28nm_PHY_*`, `REG_DSI_28nm_PHY_REGULATOR_*`, and `REG_DSI_28nm_PHY_PLL_*`. Important bitfields include timing fields for clock and HS/TA transitions, `GLBL_TEST_CTRL_BITCLK_HS_SEL`, PLL `REFCLK_CFG_DBLR`, `VREG_CFG_POSTDIV1_BYPASS_B`, `GLB_CFG_PLL_PWRDN_B`, `GLB_CFG_PLL_LDO_PWRDN_B`, `GLB_CFG_PLL_PWRGEN_PWRDN_B`, `GLB_CFG_PLL_ENABLE`, SDM divider/dither fields, `TEST_CFG_PLL_SW_RESET`, and `STATUS_PLL_RDY`.

## Control Flow
Driver setup programs regulator control/calibration, configures PLL reference/post-divider/charge-pump/SDM/SSC/lock-detect/calibration registers, enables PLL power bits, polls `PLL_RDY`, then programs PHY lane and timing registers for the desired DSI mode. The DSI host depends on this sequence completing before enabling high-speed transmission.

## State and Persistence Behavior
The register state spans regulator power, PLL tuning, spread spectrum, lock detection, calibration results, lane timing, strength, test/BIST settings, and control flags. All of it is hardware-volatile and must be replayed after PHY reset, regulator disable, or SoC suspend.

## Dependencies and Integration Points
This map is consumed by the 28nm DSI PHY and PLL code, DSI host mode setup, regulator framework, clock framework, panel power sequencing, and common D-PHY timing calculations. It is related to `dsi_phy_20nm.xml` for lane/timing layout and to `dsi_phy_28nm_8960.xml` for earlier 8960-specific differences.

## Risks
PLL power bit polarity and SDM fractional fields are easy to mispack; failures appear as no PLL lock or wrong pixel clock. Regulator and PLL domains are separate, so incomplete programming can pass generated-header tests but fail electrically. Accidentally using 8960 offsets on the standard 28nm map corrupts clock-lane or control programming.

## Test Signals
Signals include PLL rate/lock tests, generated macro build, panels at several refresh rates, high/low lane-count modes, suspend/resume, regulator off/on loops, DSI error counters, and visual stability under high pixel-clock modes.
