# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-savu.h

## Purpose

`hid-roccat-savu.h` defines the Savu special mouse report layout, report number, button-event type constants, and compact Roccat userspace event layout.

## Important APIs, Types, and Functions

- `struct savu_mouse_report_special`: report number, zero byte, event type, and two data bytes.
- `SAVU_MOUSE_REPORT_NUMBER_SPECIAL = 3`: raw-event selector.
- `enum savu_mouse_report_button_types`: profile, quicklaunch, timer, CPI, sensitivity, and multimedia event type values.
- `struct savu_roccat_report`: type plus two data bytes sent to userspace.

## Control Flow

The C file casts report 3 data to `savu_mouse_report_special`, copies the type and data bytes into `savu_roccat_report`, and forwards it through the Roccat char device.

## State and Persistence Behavior

The header defines no persistent driver state. It describes interrupt-event payloads only; profile and button configuration state are handled by feature reports in `hid-roccat-savu.c`.

## Dependencies and Integration Points

It depends on Linux fixed-width types and is consumed by the Savu driver. The event type values are part of the userspace ABI.

## Risks and Edge Cases

The event enum documents data semantics but the C file does not validate them. Layout changes would break char-device consumers.

## Test Signals

Layout-size checks and event-type coverage for report 3 should accompany changes.
