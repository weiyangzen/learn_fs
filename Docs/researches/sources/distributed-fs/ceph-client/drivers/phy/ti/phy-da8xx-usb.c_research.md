# sources/distributed-fs/ceph-client/drivers/phy/ti/phy-da8xx-usb.c

## Purpose
DA8xx USB PHY driver for separate USB1.1 and USB2.0 generic PHY instances. It controls CFGCHIP2 syscon bits, 48 MHz clocks, OTG mode override, and runtime PM interactions for OHCI and MUSB users.

## APIs, Flow, And State
`struct da8xx_usb_phy` holds both PHYs, both clocks, the CFGCHIP regmap, and provider state. USB1.1 ops toggle `CFGCHIP2_USB1SUSPENDM`, enable `usb1_clk48`, and hold a runtime PM reference because USB1.1 may depend on the USB2 reference clock. USB2.0 ops toggle `CFGCHIP2_OTGPWRDN`, enable `usb0_clk48`, and implement `.set_mode()` for host/device/OTG through `CFGCHIP2_OTGMODE_MASK`. Probe obtains platform-data or syscon regmap, creates both PHYs, registers OF or legacy lookups, writes comparator init bits, enables runtime PM, then forbids runtime PM by default.

## Dependencies And Integration
Depends on `da8xx-cfgchip`, syscon/regmap, generic PHY, clocks, runtime PM, OF, and legacy `phy_create_lookup()` names `"ohci-da8xx"` and `"musb-da8xx"`.

## Risks And Tests
Risks include unchecked `pm_runtime_get_sync()` in USB1.1 power-on, warnings-only legacy lookup failures, and runtime PM being forbidden unless userspace allows it. Test OF cell translation, non-OF lookups, both PHY power paths, OTG mode writes, runtime resume `PHYCLKGD` polling, and remove lookup cleanup.
