# sources/distributed-fs/ceph-client/drivers/misc/hisi_hikey_usb.c

## Purpose
`hisi_hikey_usb.c` controls USB role routing and hub/type-C power on HiKey boards. It relays a board-level hub role switch to an underlying device role switch while manipulating GPIOs and a hub regulator.

## Important APIs, Types, and Functions
`struct hisi_hikey_usb` stores GPIO descriptors, regulator, role switches, current role, mutex, and work item. Helpers are `hub_power_ctrl()`, `usb_switch_ctrl()`, `usb_typec_power_ctrl()`, `relay_set_role_switch()`, `hub_usb_role_switch_set()`, `hisi_hikey_usb_of_role_switch()`, `hisi_hikey_usb_probe()`, and `hisi_hikey_usb_remove()`.

## Control Flow
Probe allocates state, gets the `hub-vdd` regulator, and if `usb-role-switch` is present, acquires OTG switch/type-C VBUS/reset GPIOs, gets the underlying device role switch, initializes work, and registers a new hub role switch. Role changes store the requested role under mutex and schedule work. The worker powers off/on the correct path, selects hub or Type-C routing, then sets the underlying role switch.

## State and Persistence
State is per platform device and devm-managed. The persistent external state is GPIO level and regulator enablement. The current role is cached in memory until removed.

## Dependencies and Integration Points
It depends on GPIO descriptors, regulator framework, USB role-switch framework, firmware properties, and the `hisilicon,usbhub` compatible. It is board-glue code between the connector/user role-switch consumers and underlying USB controller role switch.

## Risks and Edge Cases
`remove()` unregisters the role switch but does not cancel pending work, so late work could access unregistered state. `relay_set_role_switch()` ignores the return from `usb_role_switch_set_role()`. Regulator `is_enabled` errors are treated like boolean status. Probe without `usb-role-switch` only obtains the regulator and remove powers the hub off.

## Test Signals
Test host, device, and none role transitions, GPIO/regulator ordering, missing optional reset GPIO, probe deferral for regulator or device role switch, removal with queued work, and role-switch error handling through fault injection.
