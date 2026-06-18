# sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-gxl-usb2.c

Purpose: Provides the Meson GXL/GXM USB2 PHY implementation, including host/device/OTG mode pin control, clock/reset management, and runtime PHY reset.

Important APIs and types: `struct phy_meson_gxl_usb2_priv` tracks regmap, current `enum phy_mode`, enable flag, optional clock, and optional shared reset. `phy_ops` expose init, exit, power on/off, set_mode, and reset.

Control flow: probe maps U2P registers, defaults mode to host, creates the regmap, gets optional resources, creates the PHY, and registers a simple provider. Init resets the optional reset line and enables the optional clock, rearming reset on clock failure. Power-on clears `POWER_ON_RESET`, marks enabled, and reapplies the current mode. `set_mode()` programs DM/DP pulldowns and ID pullup for host/OTG versus device, then triggers a PHY reset if enabled. Power-off sets reset and clears enabled. Exit disables the clock and rearms reset.

State and persistence: The last requested mode persists in `priv->mode` while powered off, allowing `power_on` to apply it. `is_enabled` guards reset side effects. No nonvolatile state exists.

Dependencies and integration: It integrates with USB controller PHY consumers through generic PHY mode APIs and matches `amlogic,meson-gxl-usb2-phy`. It uses regmap MMIO, optional shared reset, and optional `phy` clock.

Risks and test signals: Unsupported modes return `-EINVAL` and power-on rolls back to reset. Test host/device/OTG mode switches before and after power-on, optional clock/reset absence, repeated reset calls, and USB role switching with line-state/pullup behavior.
