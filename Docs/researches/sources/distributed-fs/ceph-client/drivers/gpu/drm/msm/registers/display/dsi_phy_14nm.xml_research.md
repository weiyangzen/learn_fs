# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_14nm.xml

## Purpose
This XML defines the 14nm DSI PHY common block, lane block, and PLL registers. It captures the 14nm-specific split between common software/hardware configuration, per-lane D-PHY timing, lane strength, LDO control, and PLL tuning/calibration registers.

## Important APIs, Types, and Functions
Generated symbols include `REG_DSI_14nm_PHY_CMN_*`, `REG_DSI_14nm_PHY_LN_*`, and `REG_DSI_14nm_PHY_PLL_*`. Notable bitfields include common clock-divider bits in `CLK_CFG0`, `DSICLK_SEL`, `BITCLK_HS_SEL`, `PLL_CNTRL_PLL_START`, `LDO_CNTRL_VREG_CTRL`, lane `CFG0_PREPARE_DLY`, `CFG1_HALFBYTECLK_EN`, D-PHY timing fields for `HS_EXIT`, `HS_ZERO`, `HS_PREPARE`, `HS_TRAIL`, `HS_RQST`, `TA_GO`, `TA_SURE`, `TA_GET`, and `TRIG3_CMD`. The PLL map includes trim, reset state machine, KVCO/VCO calibration, lock compare, fractional divider, SSC, TX clock, charge pump, filter, and bandgap registers.

## Control Flow
14nm PHY enable flows program common clock selection and LDO state, configure per-lane timing/strength, program PLL dividers and calibration, assert `PLL_START`, wait for ready/lock status, and then allow the DSI controller to transmit. Disable flows reverse this by stopping the controller, disabling lanes/PLL, and potentially powering down LDO/regulator state.

## State and Persistence Behavior
The live state consists of lane electrical tuning, timing counters, common clock routing, LDO voltage control, and PLL calibration/divider values. This state is volatile across PHY reset and power collapse, so the driver must replay it during every enable or resume sequence.

## Dependencies and Integration Points
The map is used by the 14nm DSI PHY driver, DSI host mode setup, regulator/clock/reset framework, PLL clock provider code, and panel bridge sequencing. It shares conceptual timing fields with 20nm/28nm maps but has different offsets and extra common/PLL controls.

## Risks
The `CLK_CFG0` duplicate field names map both divider halves to the same bit range, so consumers must understand the intended hardware meaning before relying on generated packers. Wrong PLL trim/calibration values can produce unstable clocks. Timing field mismatches appear as intermittent panel failures, lane errors, or high-speed entry/exit violations.

## Test Signals
Signals include generated-header build, PLL lock and rate tests, multiple DSI lane counts and bpp modes, panel enable/disable loops, runtime PM resume, ULPS/low-power transitions, high-speed timing margin validation, and failure logs for lane/PLL status.
