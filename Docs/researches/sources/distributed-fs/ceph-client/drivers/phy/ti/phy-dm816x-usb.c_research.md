# sources/distributed-fs/ceph-client/drivers/phy/ti/phy-dm816x-usb.c

## Purpose
DM816x USB2 nanoPHY driver. It exposes a generic PHY and a legacy `usb_phy`, programs syscon USB control/tuning registers, prepares a reference clock, and supports runtime power control for either PHY instance.

## APIs, Flow, And State
`struct dm816x_usb_phy` stores syscon, instance number, `refclk`, legacy `usb_phy`, and USB control offsets. Probe derives per-instance USBPHY control offset from the MMIO resource, obtains the `"syscon"` phandle, prepares `refclk`, creates the generic PHY/provider, and registers the legacy PHY with `usb_add_phy_dev()`. `dm816x_usb_phy_init()` warns on non-24 MHz refclk, writes shared USB_CTRL sleep/refclk bits, and programs TX rise/reference/preemphasis tuning. Runtime suspend disables the instance bit and clock; resume enables clock and the instance bit.

## Dependencies And Integration
Uses syscon/regmap, generic PHY, legacy USB PHY/OTG callbacks, clocks, runtime PM, and compatible `ti,dm8168-usb-phy`.

## Risks And Tests
Hardware comments note some DM816x revisions may ignore USB_CTRL writes. `usb_add_phy_dev()` is unchecked, and runtime PM unwind is partial on some probe failures. Test both instances, refclk rates, tuning writes, runtime suspend/resume, legacy PHY registration/removal, missing syscon/clock failures, and behavior on hardware revisions with writable versus ignored USB_CTRL.
