# sources/distributed-fs/ceph-client/drivers/net/phy/rockchip.c

## Purpose
`rockchip.c` is a small phylib driver for Rockchip integrated 10/100 Ethernet PHYs matching `INTERNAL_EPHY_ID`. It applies analog/DSP tuning, disables problematic auto-MDIX behavior by default, supports explicit MDI/MDI-X control during autoneg configuration, and re-applies analog tuning when the PHY transitions to 100 Mbps.

## Important APIs, Types, And Functions
The main helpers are `rockchip_init_tstmode()`, `rockchip_close_tstmode()`, `rockchip_integrated_phy_analog_init()`, `rockchip_integrated_phy_config_init()`, `rockchip_link_change_notify()`, `rockchip_set_polarity()`, `rockchip_config_aneg()`, and `rockchip_phy_resume()`. The exported integration point is the `rockchip_phy_driver[]` array registered with `module_phy_driver()`.

## Control Flow
On config init, the driver reads `MII_INTERNAL_CTRL_STATUS`, clears `MII_AUTO_MDIX_EN`, writes the result, then enters the test register bank and writes a vendor analog amplitude value through `SMI_ADDR_TSTWRITE` plus `TSTCNTL_WR | WR_ADDR_A7CFG`. `config_aneg` first forces the requested MDI polarity if `phydev->mdix` is fixed, then delegates negotiation to `genphy_config_aneg()`. `link_change_notify` re-runs analog initialization when phylib reports `PHY_RUNNING` at 100 Mbps, because mode switching from 10BT to 100BT resets DSP/AFE registers. Resume calls `genphy_resume()` and then repeats config init.

## State And Persistence
There is no private allocation. State persists in PHY vendor registers and in phylib fields such as `phydev->mdix`, `state`, and `speed`. Test mode is only a transient access mechanism; the driver returns to the basic register bank after analog writes.

## Dependencies And Integration Points
The file depends on Linux phylib, MII constants, ethtool MDIX values, and module registration. Its callbacks integrate with phylib config, autoneg, suspend/resume, soft reset, and link-change notification.

## Risks And Edge Cases
Analog programming uses magic values and assumes the test-mode sequence is stable across matched revisions. `rockchip_phy_resume()` ignores the return value from `genphy_resume()`, so a resume error can be hidden by a later config result. Auto-MDIX is disabled during init as a board workaround, which may surprise deployments expecting automatic cable crossover unless user MDIX policy is applied later.

## Test Signals
Check probe matching, init register writes, 10-to-100 link transitions, forced MDI and MDI-X operation, autoneg restart behavior, suspend/resume after link loss, and failure injection for test-mode register writes.
