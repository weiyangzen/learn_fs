# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_20nm.xml

## Purpose
This XML defines the 20nm DSI PHY register map. It is a compact D-PHY map with four data-lane register windows, a separate clock-lane register group, timing controls, control/strength registers, BIST controls, global test control, and LDO control.

## Important APIs, Types, and Functions
Generated symbols include `REG_DSI_20nm_PHY_LN_*`, `REG_DSI_20nm_PHY_LNCK_*`, timing control macros, `REG_DSI_20nm_PHY_CTRL_*`, `REG_DSI_20nm_PHY_STRENGTH_*`, BIST register macros, `REG_DSI_20nm_PHY_GLBL_TEST_CTRL`, and `REG_DSI_20nm_PHY_LDO_CNTRL`. Timing bitfields cover `CLK_ZERO`, `CLK_TRAIL`, `CLK_PREPARE`, high bit `CLK_ZERO_8`, `HS_EXIT`, `HS_ZERO`, `HS_PREPARE`, `HS_TRAIL`, `HS_RQST`, `TA_GO`, `TA_SURE`, `TA_GET`, and `TRIG3_CMD`.

## Control Flow
The enable path programs each data lane via the `LN` array, separately configures the clock lane, writes D-PHY timing controls computed from the mode bit clock, selects strengths/control values, and enables the LDO/test settings required for transmission. Unlike the later 10nm/7nm XML files, this map does not include a PLL domain in the same file, so clock generation is integrated elsewhere or through a different block.

## State and Persistence Behavior
The state described here is volatile PHY register state: lane config, clock-lane config, timing counters, control bits, drive strength, BIST setup, and LDO settings. It must be restored after reset or power loss and kept coherent with the DSI controller's lane count and low/high power transition timing.

## Dependencies and Integration Points
It integrates with MSM DSI PHY 20nm code, DSI host mode timing, regulator/reset control, lane-count setup, and panel bridge lifecycle. It shares many D-PHY timing fields with 28nm and 28nm-8960 maps, enabling common timing calculation with generation-specific register offsets.

## Risks
Clock-lane and data-lane windows are distinct, so array-index assumptions can misprogram the clock lane. Missing or wrong timing high bits, especially for `CLK_ZERO`, can break high-rate modes. BIST/test registers should not be left active during normal display operation.

## Test Signals
Useful signals are panel bring-up on 20nm devices, generated macro compilation, lane-count variants, timing validation at low and high bit rates, power-cycle loops, BIST isolation, and suspend/resume display restoration.
