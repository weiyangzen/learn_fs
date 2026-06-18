# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-kona-usb2.c

Purpose: Implements the Broadcom Kona USB2 PHY with minimal OTG and port-control register sequencing.

Important APIs and types: `struct bcm_kona_usb` stores the mapped register base. `bcm_kona_usb_phy_init()` performs a soft reset through `P1CTL`; power-on/off call `bcm_kona_usb_phy_power()` to set or clear OTG reset bits and line-state fields.

Control flow: probe maps the MMIO resource, creates a generic PHY, sets an 8-bit UTMI bus width, associates driver data, and registers a simple provider. Init toggles `P1CTL_SOFT_RESET` with a 2 ms assertion delay. Power-on clears OTG status/line-state bits and sets PRST/HRESET; power-off clears the reset release bits.

State and persistence: There is no mutable software state beyond the mapped register pointer. The PHY is reinitialized by direct register writes.

Dependencies and integration: It depends on generic PHY and MMIO platform resources, matching `brcm,kona-usb2-phy`. USB controllers consume the PHY provider and bus-width metadata.

Risks and test signals: The reset sequence uses fixed timing and assumes register semantics from older Kona hardware. Test init/power ordering, UTMI 8-bit consumers, repeated power cycles, missing MMIO resource, and USB high-speed attach after soft reset.
