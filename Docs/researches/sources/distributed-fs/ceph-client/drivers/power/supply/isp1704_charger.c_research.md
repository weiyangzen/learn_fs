# sources/distributed-fs/ceph-client/drivers/power/supply/isp1704_charger.c

## Purpose
This platform driver detects charger type through an NXP ISP1704/ISP1707 USB ULPI transceiver and exposes a USB power supply named `isp1704`. It distinguishes dedicated charging ports from USB/CDP-like sources, controls an enable GPIO, and coordinates with the USB gadget pull-up so charger detection can run before enumeration.

## Important APIs, Types, and Functions
`struct isp1704_charger` holds the power supply, mutable descriptor, enable GPIO, `usb_phy`, notifier, work item, model string, present/online flags, and current limit. `isp1704_charger_detect()` drives vendor power-control bits and polls `VDAT_DET`; `isp1704_charger_verify()` rejects PS/2-like false positives; `isp1704_charger_type()` temporarily manipulates ULPI function/OTG registers to distinguish DCP from CDP. `isp1704_charger_work()` handles `USB_EVENT_VBUS` and `USB_EVENT_NONE`, updates type/current, connects or disconnects the gadget, and calls `power_supply_changed()`. `isp1704_test_ulpi()` verifies scratch register access and NXP product IDs.

## Control Flow
Probe obtains the enable GPIO, gets the USB2 PHY by phandle or type, powers the transceiver, validates ULPI access and product ID, registers the power supply, initializes work and USB notifier, disconnects any existing gadget pull-up, powers down if no VBUS, and schedules detection if VBUS is already present on a B-device.

## State and Persistence
The driver caches `present`, `online`, `current_max`, and descriptor `type`. It temporarily saves/restores ULPI function and OTG control state during detection. The enable GPIO and gadget connect state persist across cable events until the next notifier work.

## Dependencies and Integration Points
It depends on USB PHY/OTG notifier events, ULPI register access, optional OF `usb-phy` phandle, a required `nxp,enable` GPIO, USB gadget APIs, and the power-supply core. It matches `nxp,isp1704` and `nxp,isp1707`.

## Risks
The power-supply descriptor type is mutated at runtime, which consumers may not expect if they cache type. A static mutex serializes detection globally across all instances. Notifier work assumes `isp->phy->otg` and possibly `gadget` are valid. Charger detection intentionally disconnects gadget pull-ups and can disrupt pre-existing enumeration. Some ULPI writes ignore return values.

## Test Signals
Exercise probe with valid and invalid ULPI IDs, VBUS insertion/removal, DCP versus CDP/USB detection, current limit clamping before high-speed chirp, gadget disconnect/connect behavior, existing VBUS at probe, enable GPIO transitions, notifier unregister/remove, and failed ULPI access during detection.
