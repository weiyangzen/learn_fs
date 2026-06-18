# sources/distributed-fs/ceph-client/drivers/hid/hid-monterey.c

## Purpose

`hid-monterey.c` is a small quirk driver for Monterey/Genius KB29E keyboards. It fixes one malformed report descriptor page byte and maps several consumer-page application keys to Linux key codes.

## Important APIs, Types, and Functions

- `mr_report_fixup()` checks descriptor size and bytes at offsets 29 and 30, then changes the usage page from Button (`0x09`) to Consumer (`0x0c`) for the affected descriptor.
- `mr_input_mapping()` maps consumer usages `0x156`, `0x157`, `0x158`, and `0x15c` to `KEY_WORDPROCESSOR`, `KEY_SPREADSHEET`, `KEY_PRESENTATION`, and `KEY_STOP`.
- The HID driver registers `.report_fixup` and `.input_mapping` for the Monterey KB29E VID/PID.

## Control Flow

On bind, HID core calls `mr_report_fixup()` before parsing. If the expected malformed descriptor signature is present, the driver mutates the descriptor in place. During input mapping, it only handles consumer-page usages and leaves all other usages to generic HID.

## State and Persistence Behavior

The driver has no per-device allocation or mutable runtime state. Its only mutation is in-memory descriptor correction during probe.

## Dependencies and Integration Points

It depends on HID core descriptor fixup/input mapping callbacks, Linux input key codes, and Monterey device IDs from `hid-ids.h`. It uses `hid_map_usage_clear()` through `mr_map_key_clear`.

## Risks and Edge Cases

- Descriptor fixup is offset-based and intentionally narrow; firmware variants with shifted descriptors will not be fixed.
- It assumes the listed consumer usages have the intended labels on this keyboard and does not expose configuration.
- There is no probe/remove because generic HID lifecycle is sufficient.

## Test Signals

Validate that the exact bad descriptor is patched, unrelated descriptors remain unchanged, the four consumer usages map to the expected key codes, and all other usages continue through generic HID handling.
