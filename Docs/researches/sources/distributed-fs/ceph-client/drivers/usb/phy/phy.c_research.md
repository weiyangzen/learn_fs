<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy.c

## Purpose
Legacy USB PHY registry and charger-notification support. Providers register `struct usb_phy`; consumers acquire PHYs by type, OF node, or phandle; charger changes are reported through atomic notifiers and uevents.

## Important APIs, Types, And Functions
Provider APIs: `usb_add_phy()`, `usb_add_phy_dev()`, `usb_remove_phy()`, `usb_phy_set_event()`. Consumer APIs: `usb_get_phy()`, `devm_usb_get_phy()`, `devm_usb_get_phy_by_node()`, `devm_usb_get_phy_by_phandle()`, `usb_put_phy()`. Charger APIs: `usb_phy_set_charger_current()`, `usb_phy_get_charger_current()`, `usb_phy_set_charger_state()`. Internal state is protected by `phy_list` and `phy_lock`; extcon setup is in `usb_add_extcon()`.

## Control Flow
Registration initializes charger work/current defaults, wires extcon notifiers, sets device type for uevents, and appends to the global list. Acquisition locks the list, checks module refs, and gets the device. Extcon changes update charger type/state and schedule work, which notifies power users and emits `KOBJ_CHANGE`.

## State And Persistence
Global PHY list, per-PHY charger current limits/type/state, notifier head, extcon devices, and pending work. Hardware state is owned by concrete PHY drivers.

## Dependencies And Integration Points
Depends on device/module/OF/extcon/notifier/workqueue/uevent infrastructure. Concrete providers like Tegra register here; host/gadget/charger drivers consume it.

## Risks
`usb_add_phy()` enforces unique type and can return `-EBUSY`. Lifetime safety depends on provider refs and devm release. `usb_add_phy_dev()` mutates `dev->type`. Extcon phandle shape changes charger versus VBUS/ID notifier behavior.

## Test Signals
Duplicate registration, OF probe deferral, devm release, module ref failures, SDP/CDP/DCP/ACA extcon events, current clamping, and uevent contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy.c -->
