# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/Kconfig

## Purpose
This Kconfig file declares DPAA2 Ethernet, optional DPAA2 DCB support, DPAA2 PTP clock support, and DPAA2 switch support.

## Important APIs, Types, and Functions
`FSL_DPAA2_ETH` depends on `FSL_MC_BUS` and `FSL_MC_DPIO`, and selects `PHYLINK`, `PCS_LYNX`, `FSL_XGMAC_MDIO`, and `NET_DEVLINK`. `FSL_DPAA2_ETH_DCB` depends on `DCB` and is available only under DPAA2 Ethernet. `FSL_DPAA2_PTP_CLOCK` depends on DPAA2 Ethernet plus `PTP_1588_CLOCK_QORIQ`. `FSL_DPAA2_SWITCH` depends on bridge/switchdev plus MC/DPIO and selects phylink/PCS/MDIO support.

## Control Flow
When symbols are enabled, `dpaa2/Makefile` selects the corresponding composite objects. DCB support conditionally adds `dpaa2-eth-dcb.o`; debugfs is controlled separately by `CONFIG_DEBUG_FS`.

## State and Persistence
The only state is kernel configuration.

## Dependencies and Integration Points
This file connects DPAA2 Ethernet to the Freescale Management Complex bus, DPIO portals, phylink, Lynx PCS, XGMAC MDIO, devlink, PTP, DCB, and switchdev.

## Risks
Missing `NET_DEVLINK` would break devlink support in `dpaa2-eth-devlink.c`; missing MC/DPIO would expose a driver with no device/control-plane substrate. Optional DCB must stay gated because `dpaa2-eth-dcb.c` depends on DCB netlink types.

## Test Signals
Config build DPAA2 Ethernet with and without DCB, PTP, switch, and debugfs; verify symbols are hidden when MC/DPIO dependencies are absent.
