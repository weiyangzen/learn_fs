# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm63xx-usbh.c

Purpose: Implements BCM63xx USBH PHY control across several SoC variants with differing register maps, PLL bits, endian swap settings, and device-mode selectors.

Important APIs and types: `struct bcm63xx_usbh_phy_variant` describes per-SoC register offsets and bit masks. `struct bcm63xx_usbh_phy` stores mapped base, optional clocks, reset, selected variant, and a `device_mode` flag set by phandle translation. PHY ops implement init, exit, power_on, and power_off.

Control flow: probe selects variant match data, maps MMIO, gets exclusive reset and optional `usbh`/`usb_ref` clocks, creates one PHY, and registers a custom xlate. Xlate stores whether the consumer requested device mode. Init enables clocks, resets the block, configures native CPU endian swap bits, setup polarity bits, USB simulation control, optional magic test-port value, and UTMI device-mode bits. Power-on/off set or clear per-variant PLL control masks. Exit disables both clocks.

State and persistence: `device_mode` persists from the most recent xlate call, so the single PHY provider is configured according to its consumer argument. Variant data is static. Hardware register programming is re-applied during init.

Dependencies and integration: It depends on optional clocks, reset controller, generic PHY, raw MMIO access, and compatibles for BCM6318/6328/6358/6362/6368/63268.

Risks and test signals: There is a likely typo in the `USBH_PLLC_CLKSEL_MASK` definition using its own mask in the shift expression, though that field is not used in this file. Single stored `device_mode` would be unsafe for multiple consumers with conflicting args. Test each variant register map, host/device xlate args, optional clock absence, reset/clock rollback, PLL power bits, and endian behavior on MIPS.
