# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-ns-usb3.c

Purpose: Initializes Broadcom Northstar USB3 PHYs over MDIO, with separate register sequences for AX and BX families plus a DMP reset register.

Important APIs and types: `enum bcm_ns_family` selects AX or BX. `struct bcm_ns_usb3` stores device, family, DMP reset mapping, MDIO device, and generic PHY. `bcm_ns_usb3_mdio_phy_write()` wraps MDIO writes. PHY `.init` performs reset and family-specific programming.

Control flow: the MDIO probe allocates state, records family match data, maps the `usb3-dmp-syscon` resource, creates a PHY, and registers a provider. Init asserts USB3 system soft reset, then AX or BX sequences select MDIO block pages, program PLL/PIPE/TX PMD values, enable SSC, and deassert DMP reset. BX additionally configures LFPS comparator and deglitch values.

State and persistence: Family is immutable match state; hardware programming persists in MDIO-addressed PHY registers and the DMP reset register.

Dependencies and integration: It is an MDIO driver, not a platform driver. It depends on PHYLIB/MDIO, OF resource parsing, BCMA reset definitions, and generic PHY. Compatible strings distinguish `brcm,ns-ax-usb3-phy` and `brcm,ns-bx-usb3-phy`.

Risks and test signals: MDIO write failures are only checked for the initial block select in family init functions; later writes are fire-and-forget. Test MDIO bus errors, both families, DMP mapping failure, USB3 reset deassertion, SSC behavior, and SuperSpeed enumeration.
