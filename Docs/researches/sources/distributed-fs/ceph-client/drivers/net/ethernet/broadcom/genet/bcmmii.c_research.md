# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/genet/bcmmii.c

## Purpose

`bcmmii.c` implements GENET MDIO bus registration, PHY discovery/attachment, PHY interface selection, link-change programming, pause negotiation, internal PHY power sequencing, MoCA fixed-link handling, and MDIO interrupt waiting. It is the PHY-side companion to the main GENET netdev/DMA driver in `bcmgenet.c`.

## Important APIs and Functions

The internal APIs exported to the rest of the GENET driver are `bcmgenet_mii_init`, `bcmgenet_mii_exit`, `bcmgenet_mii_probe`, `bcmgenet_mii_config`, `bcmgenet_mii_setup`, `bcmgenet_phy_pause_set`, and `bcmgenet_phy_power_set`.

`bcmgenet_mac_config` programs UniMAC speed, duplex, pause-ignore bits, RGMII link state, and clears software reset when needed after a PHY reports link up. `bcmgenet_mii_setup` is the phylib adjust-link callback; it calls `bcmgenet_mac_config` on link up, clears `RGMII_LINK` on link down, syncs EEE through `bcmgenet_eee_enable_set`, and prints PHY status.

`bcmgenet_mii_config` chooses `SYS_PORT_CTRL` mode and RGMII out-of-band settings from `priv->phy_interface`, supporting internal PHY, MoCA, external MII, reverse MII, and RGMII variants. It also applies max-speed restrictions for MII/reverse MII and sets `priv->ext_phy`. `bcmgenet_mii_probe` attaches the netdev to a DT PHY, ACPI-discovered UniMAC MDIO PHY, or existing direct PHY, applies Broadcom PHY flags, handles legacy RGMII delay interpretation quirks, configures the port mux after PHY capabilities are known, assigns MAC interrupts for internal PHYs when valid, marks PHY PM as MAC-managed, and enables EEE support except on GENET v1.

`bcmgenet_mii_register` creates a child `mdio-bcm-unimac` platform device over the UniMAC MDIO command registers and passes `unimac_mdio_pdata`, including a wait callback. `bcmgenet_mii_wait` waits on `priv->wq` until `MDIO_START_BUSY` clears, using either MDIO interrupts or timeout. DT setup is handled by `bcmgenet_mii_of_init`, including fixed-link registration and MoCA link-down initialization.

## Control Flow

Probe-time initialization runs through `bcmgenet_mii_init`: register the UniMAC MDIO child device, then initialize bus/PHY interface metadata from OF or ACPI. Netdev open later calls `bcmgenet_mii_probe`, which attaches to the actual PHY and runs `bcmgenet_mii_config`. Link changes from phylib call `bcmgenet_mii_setup`, which updates MAC and RGMII state. Close/remove call `bcmgenet_mii_exit`, deregistering fixed links, dropping `phy_dn`, and unregistering the child MDIO platform device.

Internal PHY power sequencing is split from PHY attachment. `bcmgenet_phy_power_set` manipulates `EXT_GPHY_CTRL` for GENET v4 or 16 nm EPHY variants, with ordered clock, IDDQ, power-down, and reset delays. Main probe/open/suspend/resume code calls this through `bcmgenet_power_up`/`bcmgenet_power_down`.

## State and Persistence Behavior

This file populates and consumes `struct bcmgenet_priv` fields `phy_interface`, `internal_phy`, `ext_phy`, `phy_dn`, `mdio_dn`, `mii_bus`, `mii_pdev`, `gphy_rev`, `wq`, and pause flags indirectly. It modifies `dev->phydev` state and capabilities, including `dev_flags`, IRQ mode, `mac_managed_pm`, EEE support, advertising pause bits, and fixed-link update callbacks. State is device-lifetime memory and phylib state, not disk-persistent.

## Dependencies and Integration Points

Dependencies include phylib, fixed PHY support, OF/ACPI helpers, OF MDIO, Broadcom PHY flags, platform-device child registration, and `mdio-bcm-unimac` platform data. It relies on shared register definitions and accessors from `bcmgenet.h` and UniMAC command bits from `unimac.h`. Link setup integrates with `bcmgenet.c` netdev open/resume and ethtool pause/EEE paths.

## Risks and Edge Cases

The PHY interface matrix is hardware-sensitive. Wrong `phy-mode` values can program the wrong port mode or RGMII delay behavior. There is a documented legacy quirk that reverses RGMII/RGMII_TXID meanings for dedicated PHY drivers; changing that risks breaking existing device trees. Fixed-link MoCA uses a custom link update callback based on UniMAC mode bits. Internal PHY interrupt handling avoids GENET v5 10 Mbps link-up interrupt issues by falling back to polling. The child MDIO platform device must be unregistered on all init failure paths to avoid leaked devices or node references.

## Test Signals

Test signals include DT and ACPI probing, fixed-link registration/removal, all supported `phy-mode` values, internal PHY power on/off ordering, RGMII link up/down, pause autoneg/manual override through ethtool, EEE enable/disable, MDIO reads/writes with interrupt and timeout wait behavior, PHY attach failures, and suspend/resume around MAC-managed PHY PM. Logs to watch include invalid PHY mode, missing MDIO child, unable-to-find-PHY, and "configuring instance for ..." messages.
