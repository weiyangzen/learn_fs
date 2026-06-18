# `sources/distributed-fs/ceph-client/include/linux/usb/phy.h`

## Purpose

`phy.h` defines the legacy USB PHY abstraction used by host, gadget, OTG, charger, and extcon-aware controller drivers. It provides PHY type/interface/event enums, OTG state enum, `struct usb_phy`, I/O access hooks, registration/get/put APIs, power/suspend/wakeup helpers, connect/disconnect notification, charger-current helpers, and notifier registration.

## Important APIs, Types, and Constants

- `enum usb_phy_interface`, `enum usb_phy_events`, `enum usb_phy_type`, and `enum usb_otg_state` describe PHY mode, cable events, PHY class, and OTG state machine states.
- `struct usb_phy_io_ops` supplies low-level register read/write hooks for ULPI-style PHY access.
- `struct usb_charger_current` records current ranges for SDP, DCP, CDP, and ACA charger types.
- `struct usb_phy` holds device metadata, flags, type, last event, OTG pointer, I/O device/ops, extcon devices and notifiers, charger state/current/work, atomic notifier chain, root-hub port status/change, multi-PHY list node, and callbacks for init/shutdown/VBUS/power/suspend/wakeup/connect/disconnect/charger detection.
- Registration and lookup APIs include `usb_add_phy()`, `usb_add_phy_dev()`, `usb_remove_phy()`, `usb_get_phy()`, devm getters, node/phandle getters, and `usb_put_phy()`.
- Inline helpers wrap I/O, init/shutdown, VBUS, set power, suspend, wakeup, connect/disconnect, notifier registration, and type-to-string conversion; disabled `CONFIG_USB_PHY` builds return `-ENXIO` or no-op.

## Control Flow and Lifetimes

PHY providers initialize `struct usb_phy`, register it, and implement callbacks. Controllers obtain a PHY by type, phandle, or node, call `usb_phy_init()`, drive VBUS/power/suspend/wakeup as role and PM state changes, notify connect/disconnect, and release it with `usb_put_phy()` or devm cleanup. Extcon and charger events update `last_event`, charger state, and notifier chains.

## State and Persistence Behavior

`usb_phy` is persistent runtime state for a PHY device. Charger current/state, last event, extcon notifiers, OTG pointer, port status/change, and notifier chain are mutable in memory. Hardware PHY registers persist until reset/power loss.

## Dependencies and Integration Points

It depends on extcon, notifier chains, USB core types, and UAPI charger definitions. It integrates with host controllers, gadget UDCs, OTG glue, device-tree PHY lookup, charger detection, root-hub status propagation, and legacy PHY drivers.

## Risks and Edge Cases

The legacy `usb_phy` API coexists with generic PHY, so mixed users must avoid double power management. Optional callbacks silently no-op in many wrappers, which can hide missing board support. Notifiers are atomic and callbacks must be context-safe. Charger current updates are side effects of `usb_phy_set_power()`. Disabled-config stubs must be handled.

## Test Signals

Build with and without `CONFIG_USB_PHY`, register/get/put PHYs, exercise extcon VBUS/ID events, charger detection and current reporting, host/gadget connect notifications, suspend/wakeup, ULPI read/write failures, notifier chains, and devm phandle/node cleanup.
