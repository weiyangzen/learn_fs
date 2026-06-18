# sources/distributed-fs/ceph-client/drivers/hid/hid-nti.c

## Purpose

`hid-nti.c` is a descriptor-fixup quirk driver for the Network Technologies USB-SUN adapter used with pre-USB Sun keyboards. Its only behavior is correcting a wrong logical maximum in the report descriptor so generic HID keyboard handling can interpret key usages correctly.

## Important APIs, Types, and Functions

- `nti_usbsun_report_fixup()` checks for the known bad descriptor signature at offsets 53 and 59 and changes both bytes from `0x65` to `0xe7`.
- The HID device table binds `USB_VENDOR_ID_NTI`/`USB_DEVICE_ID_USB_SUN`.
- `nti_driver` registers the fixup callback and otherwise relies on generic HID behavior.

## Control Flow

When HID core probes the matching adapter, it calls the report-fixup callback before descriptor parsing. If the descriptor is at least 60 bytes and both expected logical-maximum bytes are present, the callback patches them in place and logs the fix. No custom input mapping or runtime event handling is used.

## State and Persistence Behavior

There is no allocated per-device state and no persistent runtime state. The descriptor mutation is in-memory for the current device instance.

## Dependencies and Integration Points

This file depends on HID core report fixup and NTI IDs from `hid-ids.h`. Generic HID input handles all keyboard events after the descriptor is corrected.

## Risks and Edge Cases

- The fixup is exact-offset based and will miss alternate firmware descriptors.
- If a descriptor coincidentally matches those bytes but is not the USB-SUN layout, the patch could be wrong; the narrow VID/PID match limits this risk.
- There is no validation beyond the two byte checks.

## Test Signals

Validate that the known bad descriptor is patched, shorter descriptors are left alone, nonmatching bytes are left alone, and generic keyboard events expose the formerly unreachable Sun key usages after parsing.
