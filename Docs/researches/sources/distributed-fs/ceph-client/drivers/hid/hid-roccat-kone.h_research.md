# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-kone.h

## Purpose

`hid-roccat-kone.h` defines the original Kone firmware payloads, command IDs, mouse event format, Roccat event ABI, and cached device state.

## Important APIs, Types, and Functions

- Configuration structs: `kone_keystroke`, `kone_button_info`, `kone_light_info`, `kone_profile`, and `kone_settings`.
- Enumerations for button types, button numbers, keystroke actions, polling rates, mouse events, and command IDs.
- `struct kone_mouse_event`: 12-byte interrupt report with a `struct_group(wipe, ...)` region used for duplicate suppression.
- `struct kone_roccat_report`: three-byte userspace event with event, value, and macro key.
- `struct kone_device`: complete cached state for the driver.

## Control Flow

The C file reads and writes the packed structs as complete firmware payloads. Raw interrupt reports are cast to `kone_mouse_event`; event values select profile/DPI updates or userspace forwarding. Command enum values are passed directly as USB control values.

## State and Persistence Behavior

Profiles and settings represent persistent firmware state. `struct kone_device` mirrors those payloads in RAM and adds volatile active-profile/DPI, firmware version, and duplicate-suppression state.

## Dependencies and Integration Points

The header depends on Linux types and packed layout support. Its structs are exposed indirectly through binary sysfs files, so they are both firmware and userspace ABI.

## Risks and Edge Cases

The large packed profile layout is checksum-sensitive. Field comments document multiple firmware-version-dependent meanings, so validation must consider firmware version. `struct_group(wipe, ...)` is relied on by the duplicate suppression code and should not be rearranged casually.

## Test Signals

Layout-size checks for `kone_profile`, `kone_settings`, and `kone_mouse_event`; checksum tests; command-value tests; and event parsing tests should accompany any changes.
