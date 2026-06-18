# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-savu.c

## Purpose

`hid-roccat-savu.c` supports the Roccat Savu mouse. It exposes profile/general/buttons/macro/info/sensor reports through common Roccat sysfs attributes and translates special report data into compact Roccat char-device events.

## Important APIs, Types, and Functions

- Generated common attributes for control, profile, general, buttons, macro, info, and sensor.
- `savu_init_specials()` and `savu_remove_specials()`: allocate common device state and connect/disconnect char device on mouse interfaces.
- `savu_report_to_chrdev()`: converts `struct savu_mouse_report_special` into `struct savu_roccat_report`.
- `savu_raw_event()`: filters by USB mouse interface and forwards through the conversion helper.

## Control Flow

Probe parses and starts HID, then initializes only the USB mouse protocol interface. Common sysfs attributes use fixed-size Roccat feature reports. Raw events on the mouse interface are passed to `savu_report_to_chrdev()`, which ignores non-special report numbers, copies the type and two data bytes, and emits the smaller Roccat event payload.

## State and Persistence Behavior

Only common char-device state and a lock persist in RAM. Device profile, macro, button, and sensor settings are firmware state accessed through sysfs.

## Dependencies and Integration Points

The driver depends on `hid-roccat-common.h`, Savu layouts from `hid-roccat-savu.h`, HID/USB mouse-interface filtering, and Roccat char-device APIs.

## Risks and Edge Cases

- Raw-event code does not check `size` before reading report fields.
- The driver does not cache active profile or CPI, so userspace must infer changes from forwarded reports or query firmware.
- Common-helper exact-size and status-polling behavior applies.

## Test Signals

Tests should verify sysfs attribute sizes, mouse-interface gating, special report translation, handling of unclaimed char device, large macro transfer behavior, and remove cleanup.
