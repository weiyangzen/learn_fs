<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-omap-otg.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-omap-otg.c

## Purpose

`phy-omap-otg.c` drives the OMAP1 USB OTG controller output bits based on extcon ID and VBUS state. It bridges external connector notifications into the legacy OMAP OTG control register so host/peripheral mode signaling is visible to the controller.

## Important APIs, Types, and Functions

`struct otg_device` stores MMIO base, cached ID/VBUS booleans, extcon pointer, and notifier blocks. Important functions are `omap_otg_ctrl()`, `omap_otg_set_mode()`, `omap_otg_id_notifier()`, `omap_otg_vbus_notifier()`, and `omap_otg_probe()`.

## Control Flow

Probe requires platform data naming an extcon device, maps the OTG resource, registers notifiers for `EXTCON_USB_HOST` and `EXTCON_USB`, reads initial states, writes the corresponding OTG output bits, logs revision and state, and stores drvdata. ID and VBUS notifiers update cached state and call `omap_otg_set_mode()`, which programs B-session-valid, A-session-valid, or B-session-end bits depending on ID/VBUS combination.

## State and Persistence Behavior

Runtime state is the cached ID/VBUS values and notifier registrations. Hardware state persists in `OMAP_OTG_CTRL` output bits until overwritten.

## Dependencies and Integration Points

The file depends on OMAP1 platform data, extcon, MMIO, and platform devices. It is selected by `OMAP_OTG` and integrates with board-level connector detection.

## Risks and Test Signals

Risks include ambiguous extcon boolean polarity, missing state for some ID/VBUS combinations, no remove callback beyond devm cleanup, and platform-data-only binding. Tests should cover extcon absent/deferred, initial host/peripheral/no-cable states, ID/VBUS notification ordering, register bit readback, and controller behavior during cable changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-omap-otg.c -->
