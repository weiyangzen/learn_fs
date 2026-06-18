# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-arvo.h

## Purpose

`hid-roccat-arvo.h` defines the Arvo keyboard wire-format structs, command IDs, special-report bit masks, Roccat char-device event format, and per-device state used by `hid-roccat-arvo.c`.

## Important APIs, Types, and Functions

- Packed feature-report structs: `arvo_mode_key`, `arvo_button`, `arvo_info`, `arvo_key_mask`, and `arvo_actual_profile`.
- `enum arvo_commands`: command/report IDs for mode key, button, info, key mask, and actual profile.
- `struct arvo_special_report`: three-byte interrupt report with action/button encoded in `event`.
- `ARVO_SPECIAL_REPORT_EVENT_MASK_ACTION` and `_BUTTON`: masks used to split event action and button index.
- `struct arvo_roccat_report`: user-visible char-device event containing profile, button, and action.
- `struct arvo_device`: cached driver state.

## Control Flow

The header has no executable control flow, but its command IDs and packed layouts are the contract for USB feature-report transactions. The C file fills `command` fields before writes and casts raw interrupt data to `arvo_special_report` before emitting `arvo_roccat_report`.

## State and Persistence Behavior

The `arvo_actual_profile` comment states profile selection is persistent in firmware. `struct arvo_device` caches the actual profile in memory and stores the char-device minor and mutex used by sysfs and event paths.

## Dependencies and Integration Points

The header depends only on Linux fixed-width integer types and mutex visibility from including C files. It is tightly coupled to Roccat common feature-report helpers and `linux/hid-roccat.h` event delivery.

## Risks and Edge Cases

The ABI is byte-size sensitive. Any padding, enum value change, or command mismatch would break userspace tools and device communication. Several fields are documented as unknown, so validation is necessarily limited.

## Test Signals

Build-time layout checks or static assertions for packed sizes would be valuable. Runtime tests should confirm command IDs and report sizes match the values used by sysfs binary attributes and raw-event translation.
