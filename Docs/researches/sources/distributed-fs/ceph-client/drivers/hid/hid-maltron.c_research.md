<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-maltron.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-maltron.c

## Purpose

`hid-maltron.c` is a descriptor replacement driver for the Maltron L90 keyboard. The original USB report descriptor is malformed for media-key handling because the consumer-control report lacks explicit logical bounds. This driver recognizes the exact buggy descriptor and replaces it with a patched descriptor that adds logical minimum and maximum items for report ID 3, allowing consumer/media key events to be accepted as valid HID input.

## Important APIs, Types, and Functions

- `maltron_rdesc_o` is the exact original descriptor expected from the device. It includes system-control, consumer-control, and vendor-defined collections.
- `maltron_rdesc` is the replacement descriptor. It is mostly identical but inserts logical minimum `0` and logical maximum `32767` into the consumer-control collection before report count and report size.
- `maltron_report_fixup(struct hid_device *hdev, __u8 *rdesc, unsigned int *rsize)` compares the incoming descriptor size and bytes against `maltron_rdesc_o`; on exact match it returns `maltron_rdesc` and updates `*rsize`.
- `maltron_devices` matches the Alcor/Maltron keyboard USB ID from `hid-ids.h`.
- `maltron_driver` registers only `.report_fixup`.

## Control Flow

During HID probe for the matching device, the HID core calls `maltron_report_fixup` before parsing. The function performs a strict size and `memcmp` check against the known bad descriptor. If it matches, the driver logs that it is replacing the descriptor, changes the descriptor size to the patched descriptor length, and returns the static patched descriptor. If it does not match, the original descriptor pointer is returned unchanged.

There are no raw input handlers or output paths. After descriptor replacement, normal HID input parsing and event delivery are handled by the HID core and generic input layer.

## State and Persistence Behavior

The driver maintains no mutable per-device state and allocates no memory. The only persistent effect is the HID core parsing the returned static descriptor for that device instance. The original device firmware is not modified, and there is no state persisted across unplug or module reload.

## Dependencies and Integration Points

This file depends on HID report fixup, module registration helpers, standard device ID matching, and `memcmp`. It integrates indirectly with generic HID input handling by making the descriptor acceptable to the parser. The descriptor contents define system sleep/wake, consumer control, vendor-defined feature/output reports, and LED outputs, but this driver only patches descriptor metadata.

## Risks and Edge Cases

- The fix applies only to an exact descriptor byte sequence. Any firmware revision with a near-identical but not byte-identical descriptor will bypass the fix.
- Returning a static descriptor is safe for parsing but must remain immutable; no later code should attempt to modify the returned pointer in place.
- The replacement descriptor length differs from the original because logical bounds are inserted. Consumers must use the updated `*rsize`.
- Because the driver is ID-specific and exact-match specific, it has low blast radius but can miss compatible variants.

## Test Signals

Tests should feed the exact `maltron_rdesc_o` and verify that `maltron_report_fixup` returns `maltron_rdesc`, updates the size, and preserves all nonpatched collections. Negative tests should cover wrong size and one-byte descriptor mismatches. Integration signals are successful HID parsing, working media keys from report ID 3, preserved system sleep/wake behavior, and no changes for unrelated Alcor devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-maltron.c -->
