<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rza2.c -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rza2.c

Purpose: Renesas USBHS RZ/A2 and RZ/G2L platform glue for PHY acquisition, PHY power sequencing, suspend-mode bit control, gadget-only ID policy, and USBHS capability flags. The complete 86-line source was read.

Important APIs/types/functions: `usbhs_rza2_hardware_init()`, `usbhs_rza2_hardware_exit()`, `usbhs_rza2_power_ctrl()`, `usbhs_rza2_plat_info`, `usbhs_rzg2l_plat_info`, `struct renesas_usbhs_platform_info`, `usbhs_pdev_to_priv()`, `usbhs_bset()`, `phy_get()`, `phy_init()`, `phy_power_on()`, `phy_power_off()`, and `phy_exit()`.

Control flow: hardware init gets the named `"usb"` PHY and stores it in `priv->phy`; power enable initializes the PHY, sets `SUSPMODE.SUSPM`, waits 100 us for PLL stability, then powers the PHY; power disable clears `SUSPM`, powers off, and exits the PHY; hardware exit releases the PHY pointer. State is limited to `priv->phy`, the SUSPMODE bit, and PHY runtime state, with no persistent storage.

Dependencies and integration points: Linux PHY framework, Renesas USBHS common code, platform callbacks, `usbhs_get_id_as_gadget`, and driver params such as `has_cnen`, `cfifo_byte_addr`, and RZ/A2 `has_new_pipe_configs`.

Risks and test signals: risks include missing/deferred PHYs, unbalanced PHY power lifecycle, PLL timing sensitivity, and `SUSPM` being set even if `phy_init()` failed. Test with probe/remove, enable/disable loops, PHY failure injection, SUSPMODE checks, and gadget enumeration on RZ/A2/RZ/G2L hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rza2.c -->
