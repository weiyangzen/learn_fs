# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispcsiphy.c

## Purpose
`ispcsiphy.c` manages the OMAP3 CSI/CCP2 physical-layer frontend. It routes ISP interfaces to PHY instances, validates lane configuration, programs D-PHY timing and lane polarity/position, powers PHYs through regulators and CSI2 PHY power commands, and serializes ownership between CSI2/CCP2 users.

## Important APIs, Types, And Functions
- Public lifecycle: `omap3isp_csiphy_init()` initializes PHY1/PHY2 metadata and mutexes; `omap3isp_csiphy_cleanup()` destroys mutexes.
- Ownership: `omap3isp_csiphy_acquire()` enables the regulator, resets the associated CSI2 block, assigns `phy->entity`, configures routing/timing/lanes, powers revision 15.0 PHYs on, and enables autoswitch; `omap3isp_csiphy_release()` reverses routing, disables autoswitch/power, disables the regulator, and clears ownership.
- Routing helpers: `csiphy_routing_cfg_3630()` and `csiphy_routing_cfg_3430()` write syscon/control registers for OMAP3630 and OMAP3430-specific routing.
- Power helpers: `csiphy_power_autoswitch_enable()` and `csiphy_set_power()` manipulate `ISPCSI2_PHY_CFG`.
- Configuration: `omap3isp_csiphy_config()` validates clock/data lane positions and polarity, selects CCP2 versus CSI-2 lane config, computes DDR clock, and writes `ISPCSIPHY_REG0/REG1` timing.

## Control Flow
Acquire is the central path. It fails early if no regulator is available, locks the PHY mutex, enables power, resets the CSI2 block, records the owning media entity, validates and programs bus routing and D-PHY settings from the active pipeline external bus config, then powers the PHY on for revision 15.0. Release locks the same mutex, derives the bus config from the owner entity, turns routing off where supported, powers down revision 15.0 PHYs, disables the regulator, and drops ownership.

## State And Persistence
Persistent state resides in `struct isp_csiphy`: ISP pointer, mutex, associated CSI2 device, regulator, current owning media entity, register resource IDs, and supported lane count. Syscon routing and PHY timing registers are volatile and reprogrammed on acquisition; comments note control register contents are lost in off-mode but acceptable while the ISP is active.

## Dependencies And Integration Points
The file depends on regmap/syscon for SoC control routing, Linux regulators for PHY power, ISP register helpers, the active ISP pipeline and `isp_bus_cfg`, CSI2 reset, and interface enums from OMAP3 ISP platform data. It is used by CSI2 and CCP2 stream-start paths.

## Risks And Edge Cases
- `omap3isp_csiphy_acquire()` does not disable the regulator for all failure paths after regulator enable; only the revision 15.0 power-command failure path explicitly disables it.
- Lane validation rejects duplicate data lanes and clock lane conflicts, but depends on platform bus config correctness.
- DDR clock calculation divides by `hweight32(used_lanes)`; a malformed zero-lane CSI2 config would be hazardous if not prevented upstream.
- `csiphy_routing_cfg_3430()` only supports CCP2B on PHY1; other interface requests silently do nothing.

## Test Signals
Test regulator-missing and regulator-enable failure paths, duplicate/invalid lane rejection, PHY ownership serialization, revision-specific routing writes, power command timeout handling, and CSI2/CCP2 stream start/stop sequences that acquire and release the same PHY.
