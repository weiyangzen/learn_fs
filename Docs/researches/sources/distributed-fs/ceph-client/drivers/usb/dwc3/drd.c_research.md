# sources/distributed-fs/ceph-client/drivers/usb/dwc3/drd.c

## Purpose
`drd.c` implements DWC3 dual-role support. It connects role decisions from usb-role-switch, extcon, or the DWC3 OTG block to the core role-switch worker in `core.c`, and it programs OTG registers for simple host/device operation without full SRP/HNP support.

## Important APIs, Types, and Functions
Exported/internal integration functions are `dwc3_drd_init()`, `dwc3_drd_exit()`, `dwc3_otg_init()`, `dwc3_otg_exit()`, `dwc3_otg_update()`, and `dwc3_otg_host_init()`. Key helpers are `dwc3_otg_enable_events()`, `dwc3_otg_disable_events()`, `dwc3_otg_clear_events()`, `dwc3_otgregs_init()`, `dwc3_otg_get_irq()`, `dwc3_otg_host_exit()`, `dwc3_otg_device_init()`, `dwc3_otg_device_exit()`, `dwc3_drd_update()`, extcon notifier `dwc3_drd_notifier()`, and role-switch callbacks when `CONFIG_USB_ROLE_SWITCH` is enabled.

## Control Flow
`dwc3_drd_init()` prefers a USB role switch when the `usb-role-switch` property is present. Otherwise, it registers an extcon notifier if an extcon exists; extcon host state maps to host/device `GCTL.PrtCapDir` requests. Without role switch or extcon, it uses the DWC3 OTG block: obtains an OTG IRQ, clears/disables events, requests a threaded IRQ, initializes OTG registers, and schedules OTG role handling through `dwc3_set_mode(DWC3_GCTL_PRTCAP_OTG)`.

OTG IRQ top half reads and clears OEVT, filters non-OTG events, and wakes the thread. The thread handles pending host restart and requeues OTG mode evaluation. `dwc3_otg_update()` reads ID status unless told to ignore it, exits the current OTG sub-role, sets `current_otg_role`, initializes host or device OTG register flow, invokes glue `pre_set_role`, and starts `dwc3_host_init()` or `dwc3_gadget_init()`.

## State and Persistence Behavior
DRD state is stored in `struct dwc3`: `current_dr_role`, `desired_dr_role`, `current_otg_role`, `desired_otg_role`, `otg_restart_host`, `edev`, `edev_nb`, `role_sw`, `role_switch_default_mode`, and `otg_irq`. No persistence exists beyond the live driver instance. IRQ and notifier registrations are unwound by `dwc3_drd_exit()`.

## Dependencies and Integration Points
This file integrates extcon, usb-role-switch, OF platform population for connector devices, DWC3 OTG registers, gadget/host init and exit, event-buffer setup/cleanup for device role, and optional glue callbacks. It relies on the role-switch workqueue logic in `core.c` for non-OTG mode changes.

## Risks
Role switching is concurrency-sensitive: extcon/role-switch callbacks, debugfs mode writes, OTG IRQ thread, and PM can all touch role state. OTG register programming intentionally avoids SRP/HNP, so it is suitable for simple dual-role but not full OTG negotiation. Cleanup must match the current live role because users may change role through debugfs. A failed `dwc3_host_init()` or `dwc3_gadget_init()` leaves role registers updated but functionality unavailable.

## Test Signals
Test usb-role-switch set/get, extcon host cable notification, raw OTG ID changes, debugfs mode changes, unload while in each role, and suspend/resume around role changes. Hardware signals include VBUS assertion in host, gadget enumeration in device, OTG IRQ delivery, and no duplicate notifier/IRQ registration after reprobe.
