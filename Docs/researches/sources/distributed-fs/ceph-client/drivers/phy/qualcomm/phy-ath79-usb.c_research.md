# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-ath79-usb.c

This Atheros AR71XX/9XXX USB PHY driver is a minimal generic PHY provider around reset controls. `struct ath79_usb_phy` stores the mandatory `phy` reset and optional inverted `usb-suspend-override` reset.

Probe allocates state, gets reset controls, creates a generic PHY with power callbacks, stores private data, and registers `of_phy_simple_xlate` for `qca,ar7100-usb-phy`. `power_on()` asserts `no_suspend_override` if present because the logic is inverted, then deasserts the PHY reset; if deassert fails it unwinds the override. `power_off()` asserts the PHY reset, then deasserts the override, unwinding the PHY reset if that fails.

State is entirely in reset lines. Dependencies are reset controller, generic PHY, OF matching, and platform driver infrastructure. Risks are reset polarity confusion, optional override availability differences across SoCs, and no explicit delays around reset transitions. Test signals are resource acquisition and USB controller link behavior.
