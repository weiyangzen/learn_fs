# `sources/distributed-fs/ceph-client/include/linux/usb/otg.h`

## Purpose

`otg.h` defines the shared USB OTG object and capability model used between USB host controllers, gadget controllers, and PHY/transceiver drivers. It also declares dual-role mode parsing helpers.

## Important APIs, Types, and Constants

- `struct usb_otg` stores default-A role, generic PHY, legacy `usb_phy`, host bus, gadget, current OTG state, and callbacks to set host/peripheral, set VBUS, start SRP, and start HNP.
- `struct usb_otg_caps` records OTG revision and HNP/SRP/ADP support.
- `usb_otg_state_string()` converts OTG state to text.
- Inline wrappers `otg_start_hnp()`, `otg_set_vbus()`, `otg_set_host()`, `otg_set_peripheral()`, and `otg_start_srp()` dispatch optional callbacks or return `-ENOTSUPP`.
- `usb_bus_start_enum()` starts host enumeration on a port.
- `enum usb_dr_mode`, `usb_get_dr_mode()`, and `usb_get_role_switch_default_mode()` describe host/peripheral/OTG/default role policy.

## Control Flow and Lifetimes

PHY/OTG glue creates a `usb_otg`, binds host and gadget sides through `set_host()` and `set_peripheral()`, then role changes drive VBUS, SRP, HNP, and enumeration callbacks. Device-tree or firmware role parsing chooses the initial mode/default.

## State and Persistence Behavior

OTG state is runtime in memory and attached hardware. Host/gadget pointers must remain valid while bound. Capability data may come from firmware and remains stable for the controller.

## Dependencies and Integration Points

It depends on generic PHY, legacy USB PHY, USB bus/gadget definitions, and `usb_phy` OTG state enums. It integrates dual-role controller glue, role-switch code, host enumeration, gadget UDCs, and OF helpers.

## Risks and Edge Cases

Callbacks are optional; callers must handle `-ENOTSUPP`. Binding host/gadget out of order can leave partial OTG state. HNP/SRP should only be attempted when capability and role permit it. Role parsing must tolerate absent or invalid firmware properties.

## Test Signals

Test host-only, peripheral-only, and OTG modes; bind/unbind host and gadget; SRP/HNP role swaps; VBUS control; enum start; firmware `dr_mode` parsing; and disabled callback paths.
