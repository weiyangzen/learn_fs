# `sources/distributed-fs/ceph-client/include/linux/usb/role.h`

## Purpose

`role.h` defines the USB role-switch framework API used by dual-role controllers and Type-C/OTG glue to select none/host/device roles through firmware-described switch objects.

## Important APIs, Types, and Constants

- `enum usb_role` defines `USB_ROLE_NONE`, `USB_ROLE_HOST`, and `USB_ROLE_DEVICE`.
- Callback types `usb_role_switch_set_t` and `usb_role_switch_get_t` define setter/getter signatures.
- `struct usb_role_switch_desc` describes firmware node, device, set/get callbacks, driver data, name, module owner, and option flags such as allowing userspace control.
- APIs include set/get role, get by device or fwnode, put, register, unregister, set/get driver data, and `usb_role_string()`.
- Disabled `CONFIG_USB_ROLE_SWITCH` builds provide stubs returning `-EOPNOTSUPP`, `USB_ROLE_NONE`, `ERR_PTR(-ENODEV)`, or no-op.

## Control Flow and Lifetimes

A provider registers a role switch with callbacks. Consumers acquire it from a device or fwnode, call `usb_role_switch_set_role()` when Type-C/OTG policy changes, query current role as needed, and release with `usb_role_switch_put()`. Provider unregisters during teardown.

## State and Persistence Behavior

Role state is runtime hardware/framework state. Driver data persists for the switch lifetime. Firmware node links provide discovery but no mutable persistence.

## Dependencies and Integration Points

It depends on device/fwnode infrastructure and optional role-switch Kconfig. It integrates Type-C port managers, dual-role USB controllers, mux/orientation code, and userspace-controllable role switching.

## Risks and Edge Cases

Consumers must handle absent role-switch support and error pointers. Role changes may require coordinated VBUS, PHY, host, and gadget sequencing outside this API. Userspace control can conflict with policy engines if not gated.

## Test Signals

Build with/without role switch support, register provider switches, get by fwnode/device, set host/device/none roles, test userspace role changes, unregister while consumers hold references, and verify string conversion.
