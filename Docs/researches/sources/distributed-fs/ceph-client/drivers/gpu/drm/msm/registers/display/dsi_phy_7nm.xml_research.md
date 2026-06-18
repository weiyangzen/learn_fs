# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_7nm.xml

## Purpose
This XML defines the 7nm DSI PHY, including a larger common block, per-lane registers, and an expanded PLL block. It supports modern DSI electrical configuration with global timing controls, strength/pre-emphasis/rescode controls, VREG controls, PHY/lane status, and rich PLL calibration, SSC, rate, and lock programming.

## Important APIs, Types, and Functions
Generated symbols include `REG_DSI_7nm_PHY_CMN_*`, `REG_DSI_7nm_PHY_LN_*`, and `REG_DSI_7nm_PHY_PLL_*`. Important common registers are revision ids, clock/global controls, lane controls, PLL control, timing controls `TIMING_CTRL_0` through `TIMING_CTRL_13`, global HSTX/LPTX/pre-emphasis/rescode controls, VREG, status, and lane status. Per-lane registers cover `CFG*`, `TEST_DATAPATH`, `PIN_SWAP`, `LPRX_CTRL`, and `TX_DCTRL`. PLL registers cover analog controls, DSM/feedback dividers, calibration timers and bands, frequency detect, filters, gain, lock-detect, outdiv, fastlock, pass/core overrides, rate change, decimal/fractional divider sets, MASH, SSC sets, rate-specific lock/gain/band controls, and lock override/delay.

## Control Flow
7nm PHY enable flows program common lane/timing/electrical controls, set per-lane configuration and pin swap, program PLL dividers and calibration for the requested bit clock, optionally configure SSC/rate tables, start or update the PLL, poll lock/status, and then allow the DSI controller to enter high-speed operation. The larger common timing block lets the driver program timing globally instead of repeating all timing fields inside each lane window.

## State and Persistence Behavior
Runtime state includes global timing, lane control, drive strength, pre-emphasis, rescode offsets, VREG state, lane status, PLL calibration bands, divider state, SSC state, and rate-dependent PLL parameters. It is volatile across PHY power collapse and must be rebuilt by the driver during enable and resume.

## Dependencies and Integration Points
It integrates with 7nm DSI PHY and PLL drivers, the MSM clock framework, DSI host mode calculation, panel sequencing, regulator/reset management, and newer SoC display pipelines. It is structurally related to 10nm but has a richer common/PLL register set and different offsets.

## Risks
The expanded PLL block contains many similarly named rate and divider registers; off-by-one offset errors can generate clocks that appear locked but are at the wrong rate. Global timing programming differs from older lane-local timing maps, so shared timing code must branch correctly. Pin swap, pre-emphasis, and rescode values are board- and PHY-sensitive.

## Test Signals
Signals include generated macro build, PLL rate and lock verification, multiple refresh rates and bpp modes, dual-DSI or lane-swap configurations, suspend/resume, ULPS transitions, high bit-rate stress, DSC panel modes, and display stability under repeated power collapse.
