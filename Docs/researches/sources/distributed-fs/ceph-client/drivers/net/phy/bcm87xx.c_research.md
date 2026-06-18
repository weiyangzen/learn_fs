# sources/distributed-fs/ceph-client/drivers/net/phy/bcm87xx.c

## Purpose
`bcm87xx.c` supports Broadcom BCM8706 and BCM8727 10G Clause 45 PHYs. It provides minimal feature advertisement, optional device-tree register initialization, fixed 10G status reading, LASI interrupt control, and custom matching using C45 device IDs.

## Important APIs, Types, And Functions
When OF MDIO is enabled, `bcm87xx_of_reg_init()` parses `broadcom,c45-reg-init` tuples of `<devid reg mask value>` and applies masked or direct MMD writes. `bcm87xx_get_features()` adds `10000baseR_FEC` support. `bcm87xx_read_status()` reads PMAPMD signal detect, PCS 10GBASE-R status, and PHYXS lane status. `bcm87xx_config_intr()` toggles PCS LASI control and acknowledges LASI status. `bcm87xx_match_phy_device()` matches C45 device ID slot 4 against the driver ID.

## Control Flow
Config init only applies optional OF register programming. Autoneg configuration returns `-EINVAL`, reflecting fixed/no-aneg operation. Status read checks three hardware conditions in sequence; any missing signal, PCS lock, or lane status clears link. On success it sets speed 10000, full duplex, and link up. Interrupt enable reads LASI control, clears pending status, sets bit 0 to enable; disable clears bit 0 and then reads status. The interrupt handler reads LASI status and triggers the PHY state machine when nonzero.

## State And Persistence
There is no driver-private state. Optional OF register initialization writes persistent-until-reset hardware configuration. Link state is reported in `phydev`.

## Dependencies And Integration Points
The driver depends on phylib, Clause 45 MMD access, optional OF MDIO properties, and generic 10G constants. It integrates via `module_phy_driver()` and two static PHY IDs. Device-tree board files can use `broadcom,c45-reg-init` for platform-specific register fixes.

## Risks And Edge Cases
`bcm87xx_handle_interrupt()` reads `BCM87XX_LASI_STATUS` through `phy_read()` rather than `phy_read_mmd(MDIO_MMD_PCS, ...)`, while `config_intr()` uses MMD access; this is a notable audit point. The OF tuple parser ignores trailing incomplete cells and uses mask semantics where `val = old & mask | val_bits`, which differs from common clear-mask/write semantics. No autoneg path exists.

## Test Signals
Test fixed 10G link up/down on signal loss, PCS loss, and PHYXS lane loss; LASI IRQ enable/disable; C45 device matching for both IDs; and representative `broadcom,c45-reg-init` board data including masked writes and direct writes.
