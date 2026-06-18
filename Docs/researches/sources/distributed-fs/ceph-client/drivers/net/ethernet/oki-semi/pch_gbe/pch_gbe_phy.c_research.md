# sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe_phy.c

## Purpose
Implements PCH GBE PHY access and setup over MAC MIIM: standard register access, PHY ID, reset/power state, initial MII configuration, RGMII reset, and AR803x TX clock delay/hibernate quirks.

## Important APIs, Types, And Functions
Exports `pch_gbe_phy_get_id()`, MIIM read/write helpers, `pch_gbe_phy_hw_reset()`, power up/down, `pch_gbe_phy_set_rgmii()`, `pch_gbe_phy_init_setting()`, and `pch_gbe_phy_disable_hibernate()`. Internal `pch_gbe_phy_sw_reset()` and `pch_gbe_phy_tx_clk_delay()` handle BMCR reset and AR803x debug registers.

## Control Flow
Register helpers validate 5-bit offsets and call `pch_gbe_mac_ctrl_miim()`. PHY ID combines ID1/ID2. Hardware reset writes default control/advertisement/next-page/1000T/specific-control values. Initial settings build an `ethtool_cmd` from cached policy, apply MII settings, reset PHY, assert CRS on TX, and optionally program TX delay.

## State And Persistence
Updates `hw->phy.id`, `hw->phy.revision`, and PHY registers. State persists only until PHY reset or power cycle.

## Dependencies And Integration Points
Depends on main-file MIIM control, `adapter->mii` helpers, and platform quirk flags.

## Risks And Edge Cases
MIIM timeout returns zero, indistinguishable from a valid zero read. AR803x quirks return `-EINVAL` on unknown PHYs. Hardware reset writes defaults without completion polling. Power-down does not itself check WOL despite comments.

## Test Signals
PHY discovery, ethtool link changes, power down/up, AR803x TX delay and hibernate quirks, timeout logging, and PHY dumps.
