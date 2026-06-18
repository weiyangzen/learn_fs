# `sources/distributed-fs/ceph-client/include/linux/usb/of.h`

## Purpose

`of.h` declares Open Firmware/device-tree helpers for USB controllers, hubs, devices, interfaces, PHYs, OTG capabilities, connect types, and companion devices.

## Important APIs, Types, and Constants

- `of_usb_get_dr_mode_by_phy()`, `of_usb_get_phy_mode()`, and `of_usb_update_otg_caps()` parse USB role, PHY mode, and OTG capability properties.
- `of_usb_host_tpl_support()` checks target peripheral list support.
- `usb_of_get_connect_type()`, `usb_of_get_device_node()`, `usb_of_has_combined_node()`, and `usb_of_get_interface_node()` map USB topology to firmware nodes.
- `usb_of_get_companion_dev()` resolves companion devices.
- Non-OF or non-USB builds provide safe default stubs returning unknown/false/null/zero.

## Control Flow and Lifetimes

Controller and hub code call these helpers during probe/enumeration to interpret device-tree properties. Returned device nodes or devices are used to configure role, PHY, OTG, port connect type, and interface-specific child devices. Lifetime/refcount details are implemented in OF helper code.

## State and Persistence Behavior

The header itself stores no state. It converts static firmware description into runtime USB configuration decisions.

## Dependencies and Integration Points

It depends on USB, Chapter 9, OTG, PHY, and OF configuration. It integrates device-tree bindings with host controllers, gadget controllers, hubs, onboard devices, and USB interface child devices.

## Risks and Edge Cases

Callers must handle stub defaults when `CONFIG_OF` or `CONFIG_USB_SUPPORT` is disabled. Firmware nodes may be absent, combined, or mismatched with dynamic USB topology. Role and PHY mode parsing must tolerate unknown values. Node reference handling must be correct in implementation users.

## Test Signals

Build with and without OF/USB support, parse `dr_mode`, `phy_type`, OTG capability, and connect-type properties, test hub port child nodes, combined node detection, interface node lookup, companion device resolution, and malformed device-tree data.
