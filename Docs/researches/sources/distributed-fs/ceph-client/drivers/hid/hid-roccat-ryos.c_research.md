# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-ryos.c

## Purpose

`hid-roccat-ryos.c` supports Roccat Ryos MK, Glow, and Pro keyboards. It exposes many keyboard configuration, macro, lighting, and talk feature reports through common Roccat sysfs attributes and forwards special reports to the Roccat char device.

## Important APIs, Types, and Functions

- `struct ryos_report_special`: five-byte report number 3 event payload.
- Generated common attributes for profile, key groups, key mask, light, macro, info, reset, light control, talk, stored lights, custom lights, and light macro.
- `ryos_init_specials()` and `ryos_remove_specials()`: allocate common device state and connect/disconnect char device on protocol 0 interface.
- `ryos_raw_event()`: forwards report 3 to the char device.

## Control Flow

Probe requires USB, parses and starts HID, and initializes only interface protocol 0. Initialization allocates `struct roccat_common2_device`, initializes its lock, and connects a char device sized for `struct ryos_report_special`. Sysfs attributes are supplied by a class named `ryos` and use exact-size common helper transfers. Raw events on other interfaces or non-report-3 data are ignored; report 3 is forwarded as raw bytes if the char device is claimed.

## State and Persistence Behavior

Driver state is limited to common char-device state and a mutex. Keyboard profiles, macros, and lighting state live in firmware and are accessed on demand through sysfs feature reports.

## Dependencies and Integration Points

The driver uses Roccat common helpers, HID/USB, class sysfs groups, and `linux/hid-roccat.h` event forwarding. It does not have a separate header in this work item; report constants and layouts are local.

## Risks and Edge Cases

- `ryos_raw_event()` does not validate `size` before checking and forwarding `data[0]`.
- Large lighting and macro payload sizes make short USB transfer handling important.
- Common-helper status polling can block indefinitely on repeated busy status.

## Test Signals

Tests should verify all bin attribute sizes/modes, protocol-interface gating, report-3 char-device forwarding, large macro/light transfers, failed char-device registration, and remove cleanup.
