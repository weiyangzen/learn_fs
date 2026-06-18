# sources/distributed-fs/ceph-client/drivers/hid/hid-keytouch.c

## Purpose

`hid-keytouch.c` replaces the broken report descriptor for the Keytouch IEC keyboard with a known-good boot-keyboard-like descriptor that exposes modifier keys, LEDs, and six key slots.

## Important APIs, Types, and Functions

- `keytouch_fixed_rdesc`: complete replacement HID report descriptor.
- `keytouch_report_fixup(...)`: logs the fixup, replaces `*rsize`, and returns `keytouch_fixed_rdesc`.
- `keytouch_devices`: matches `USB_DEVICE_ID_KEYTOUCH_IEC`.
- `keytouch_driver`: registers the descriptor fixup hook.

## Control Flow

HID core calls `report_fixup` during report parsing. This driver unconditionally swaps the device descriptor with the static replacement for the matched Keytouch IEC device. Generic HID parsing and `hid-input.c` then build the input device from the fixed descriptor.

## State and Persistence Behavior

There is no mutable driver-private state. The replacement descriptor is static read-only data; its effect persists only in the parsed HID device for the current probe.

## Dependencies and Integration Points

The driver relies on HID core descriptor fixup, module registration, and Keytouch USB IDs. All input event behavior after descriptor replacement is delegated to generic HID input.

## Risks and Edge Cases

- The descriptor is an unconditional replacement for the PID. If a hardware revision uses the same ID with a different protocol, the driver will hide it.
- The replacement descriptor is minimal; any vendor-specific extra controls in the original descriptor are intentionally lost.
- Returning a static descriptor is correct for fixup but must remain immutable.

## Test Signals

The Keytouch IEC should parse without HID descriptor errors, expose keyboard keys and LED outputs, and register through generic HID input. Regression tests should compare descriptor size and key/LED capabilities against the fixed descriptor.
