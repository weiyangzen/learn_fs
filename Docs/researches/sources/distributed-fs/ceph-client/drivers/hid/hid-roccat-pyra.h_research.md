# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-pyra.h

## Purpose

`hid-roccat-pyra.h` defines Pyra report sizes, control request values, packed settings/profile/info payloads, mouse/audio report layouts, event type constants, Roccat report payload, and per-device state.

## Important APIs, Types, and Functions

- `PYRA_SIZE_*`: control, info, profile settings/buttons, and settings payload sizes.
- `enum pyra_control_requests`: profile settings/buttons selectors.
- `struct pyra_settings`, `struct pyra_profile_settings`, and `struct pyra_info`: feature-report payload layouts.
- `enum pyra_commands`: report command IDs.
- `struct pyra_mouse_event_button` and audio/button type enums: interrupt report formats.
- `struct pyra_roccat_report` and `struct pyra_device`: userspace event and cached state.

## Control Flow

The C file uses the control request enum to select profile data before reading shared payload commands. Raw button report type constants decide which events update cached values and which are forwarded.

## State and Persistence Behavior

`struct pyra_device` caches active profile/CPI and profile settings. The settings payload's `startup_profile` is zero-based firmware state and persists in the device.

## Dependencies and Integration Points

The header depends on Linux fixed-width types and is part of the binary sysfs and char-device ABI consumed by Roccat tooling.

## Risks and Edge Cases

Profile numbering is mixed: firmware settings use 0-4, several mouse events report 1-5, and userspace reports keep some one-based behavior. Any layout or enum change breaks userspace and firmware protocol.

## Test Signals

Layout-size checks, profile numbering conversion tests, button/audio report parsing, and sysfs attribute size checks should guard this header.
