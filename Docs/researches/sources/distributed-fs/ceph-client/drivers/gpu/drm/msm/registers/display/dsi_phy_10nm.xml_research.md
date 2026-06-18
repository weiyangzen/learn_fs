# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_10nm.xml

## Purpose
This XML describes the 10nm DSI PHY register layout. It covers the common PHY control block, per-lane analog/digital lane registers, and the PLL block used to synthesize DSI bit/byte clocks.

## Important APIs, Types, and Functions
Generated symbols include `REG_DSI_10nm_PHY_CMN_*`, `REG_DSI_10nm_PHY_LN_*`, and `REG_DSI_10nm_PHY_PLL_*`. Important register groups are revision ids, `CLK_CFG*`, `GLBL_CTRL`, `RBUF_CTRL`, `VREG_CTRL`, lane config/control, `PLL_CNTRL`, common timing controls `TIMING_CTRL_0` through `TIMING_CTRL_11`, `PHY_STATUS`, lane status registers, per-lane `CFG*`, `PIN_SWAP`, high/low power TX/RX strength controls, and PLL controls for DSM/feedback dividers, calibration, filters, SSC, lock-detect, and output division.

## Control Flow
The PHY driver typically reads revision ids, enables regulators/buffers, writes PLL divider and calibration values for the desired lane rate, programs common and per-lane timing registers, enables lane control, starts the PLL, polls lock/status, and hands the byte/bit clock to the DSI controller. Per-lane arrays allow identical programming over clock/data lanes while still supporting pin swap and lane-specific electrical tuning.

## State and Persistence Behavior
Runtime state is the PHY's analog configuration: PLL dividers, spread-spectrum values, calibration bands, lane strengths, pin swaps, D-PHY timing values, and status/lock bits. It must be re-created after power collapse or reset; the XML itself persists only the register map used by generated headers.

## Dependencies and Integration Points
This map integrates with the MSM DSI PHY 10nm implementation, common DSI host timing calculations, DRM mode clock selection, regulator and reset control, clock framework PLL registration, and panel enable/disable sequencing. It is close to the 7nm map but has a smaller common/PLL register set and 10nm-specific offsets.

## Risks
PLL and timing register offsets are highly silicon-specific; using 7nm or 14nm values against this map can leave the PLL unlocked or violate MIPI timing. Lane array stride or length mistakes affect clock/data lane addressing. Status polling that assumes another PHY generation's lock bits can cause false success or timeouts.

## Test Signals
Useful tests are generated macro build checks, mode validation across multiple bit rates, PLL lock polling, panel enable/disable loops, ULPS/stop-state transitions, suspend/resume, lane swap configurations, and scope or panel-visible validation for high-speed timing margins.
