<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-ortek.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-ortek.c

## Purpose
This is a small HID descriptor-fix driver for Ortek-family keyboards/trackpads and a Skycable wireless presenter. The supported devices have incorrect logical maximum values in their report descriptors, causing consumer/page usages to be truncated or misinterpreted by generic HID parsing.

## Important APIs, types, and functions
The primary callback is `ortek_report_fixup`, installed in `ortek_driver.report_fixup`. It receives the mutable descriptor buffer and descriptor size before HID parsing. The device table binds Ortek PKB-1700, WKB-2000, iHome IMAC-A210S, and Skycable wireless presenter IDs from `hid-ids.h`.

## Control flow
There is no custom probe/remove path. HID core matches one of the IDs, calls `ortek_report_fixup` during parse, and then generic HID handling continues. The fixup checks exact descriptor offsets: for Ortek descriptors it changes byte 55 after a `0x25` logical maximum item from `0x01` to `0x92`; for Skycable it changes byte 53 from `0x01` to `0x65`. If the size/byte pattern does not match, the descriptor is returned unchanged.

## State and persistence behavior
The driver has no persistent state and allocates no per-device data. Its only mutation is in-place descriptor repair during enumeration.

## Dependencies and integration points
It depends only on HID core, module infrastructure, device headers, and `hid-ids.h`. After descriptor repair, all runtime input event generation is delegated to generic HID input handling.

## Risks and test signals
The risk is offset-specific descriptor patching: a firmware variant with a similar product ID but different descriptor layout may not be repaired or could be repaired incorrectly if the byte guard is too weak. The guards check descriptor length and local byte patterns. Test signals are descriptor dumps before/after fixup, successful parsing of high consumer usages, and no regression for the four listed device IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-ortek.c -->
