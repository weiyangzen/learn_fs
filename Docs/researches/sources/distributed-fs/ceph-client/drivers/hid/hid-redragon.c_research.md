# sources/distributed-fs/ceph-client/drivers/hid/hid-redragon.c

## Purpose

`hid-redragon.c` fixes a malformed Redragon Asura keyboard report descriptor. The keyboard advertises one input item as array data at descriptor bytes 100-101, but the generated key data requires variable input semantics.

## Important APIs, Types, and Functions

- `redragon_report_fixup()`: descriptor fixup hook. If the descriptor is at least 102 bytes and bytes 100-101 are `0x81, 0x00`, it rewrites byte 101 to `0x02`.
- `redragon_devices[]`: matches the Redragon Asura under the Jess vendor ID.
- `redragon_driver`: HID driver with only `.report_fixup` and the ID table.

## Control Flow

HID core invokes `report_fixup` before parsing the descriptor. The function verifies both size and expected byte pattern, logs a device info message when applying the fix, mutates the descriptor in place, and returns the descriptor pointer. No probe override is needed; normal HID core parse/start behavior handles the device after the fixup.

## State and Persistence Behavior

No runtime state is stored. The only mutation is the in-memory report descriptor passed by HID core for the current device instance.

## Dependencies and Integration Points

The driver integrates with HID descriptor parsing through the report-fixup callback. It depends on `hid-ids.h` for the Jess/Redragon IDs and kernel HID module registration.

## Risks and Edge Cases

- The fix is byte-offset-specific. If a firmware variant shifts the item while keeping the same USB ID, the condition will not match.
- If another device with the same ID has valid bytes at that offset, it will be left unchanged because both bytes must match the known malformed pattern.
- The code does not validate surrounding descriptor structure, only the local bytes.

## Test Signals

Descriptor-level tests should feed the known malformed descriptor and confirm byte 101 changes from `0x00` to `0x02`, while shorter or already-correct descriptors are unchanged. Device testing should confirm that key events parse as variable key bits and no parser warnings remain.
