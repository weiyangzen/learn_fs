# sources/distributed-fs/ceph-client/drivers/phy/ti/phy-omap-usb2.c

## Purpose
OMAP/DRA7/AM437/AM654 USB2 PHY driver exposing both generic PHY and legacy `usb_phy`. It manages clocks, syscon or control-module power, OTG comparator callbacks, false-disconnect calibration, and AM65x charger-detect erratum handling.

## APIs, Flow, And State
`struct omap_usb` holds legacy PHY, optional comparator, MMIO base, control/syscon power references, wakeup/reference clocks, flags, and power masks. `omap_usb2_set_comparator()` lets companion drivers provide VBUS/SRP callbacks. Probe maps the PHY, resolves power control through `syscon-phy-power` or `ctrl-module`, gets clocks with legacy-name fallbacks, creates generic PHY/provider, powers off initially, and registers the legacy PHY. Init enables clocks and applies false-disconnect or charger-detect register tweaks. Power ops update syscon bits or call `omap_control_phy_power()`.

## Dependencies And Integration
Depends on generic PHY, legacy USB PHY, OMAP control PHY helpers, syscon/regmap, clocks, runtime PM, OF, and `soc_device_match()`.

## Risks And Tests
`omap_usb_init()` ignores clock-enable failure, `usb_add_phy_dev()` is unchecked, and fallback clock names can hide DT drift. Test each compatible mask/on/off set, syscon and control-module power paths, comparator VBUS/SRP callbacks, clock fallbacks, AM65x SR1.0 erratum, initial power-off, and register writes.
