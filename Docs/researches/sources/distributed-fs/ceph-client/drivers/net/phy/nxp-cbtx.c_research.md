# sources/distributed-fs/ceph-client/drivers/net/phy/nxp-cbtx.c

## Purpose
This file is the phylib driver for the 100BASE-TX PHY embedded in the NXP SJA1110 switch. It supplies reset handling, MDIX configuration/status, interrupt handling, and a single RX error ethtool statistic.

## Important APIs, Types, and Functions
The driver registers `PHY_ID_CBTX_SJA1110` in `cbtx_driver[]`. Key callbacks are `cbtx_soft_reset()`, `cbtx_config_init()`, `cbtx_read_status()`, `cbtx_config_aneg()`, `cbtx_config_intr()`, `cbtx_handle_interrupt()`, `cbtx_get_sset_count()`, `cbtx_get_strings()`, and `cbtx_get_stats()`.

## Control Flow
Soft reset first clears true power-down because the PHY cannot reset while powered down, then delegates to `genphy_soft_reset()`. Init defers actual MDIX programming by setting `phydev->mdix_ctrl = ETH_TP_MDI_AUTO`; config-aneg applies the MDIX mode and then runs generic autoneg. Read-status updates MDIX status from `CBTX_MODE_CTRL_STAT` and delegates link state to `genphy_read_status()`.

Interrupt configuration acknowledges latched status by reading `CBTX_IRQ_STAT`, then enables link-down, autoneg-complete, and energy-on events, or disables all events and acknowledges pending state. The interrupt handler reads and clears status, reads the enable mask, ignores disabled/unasserted events, and triggers the phylib state machine.

## State and Persistence
No private software state is used. Persistent state is in PHY registers for power-down, MDIX mode, IRQ enable/status, and the RX error counter. `phydev->mdix_ctrl` and `phydev->mdix` are the phylib-facing mirrors.

## Dependencies and Integration Points
The driver uses phylib Clause 22 helpers, generic autoneg/suspend/resume/status code, ethtool stats helpers, and module MDIO device matching.

## Risks
`cbtx_mdix_config()` returns success for unknown `mdix_ctrl` values instead of `-EINVAL`, which may hide unsupported control requests. Stats reads return `U64_MAX` on MDIO failure. Interrupt status semantics rely on read-to-clear behavior.

## Test Signals
Test reset from true power-down, auto/MDI/MDI-X configuration, link readout, IRQ enable/disable, link-down/autoneg IRQ delivery, RX error ethtool stat reads, and suspend/resume with the embedded switch PHY.
