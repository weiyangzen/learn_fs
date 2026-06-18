# File Research: sources/block-storage/lvm2/lib/device/parse_vpd.c

## Purpose
Parses and normalizes SCSI VPD page data into LVM device WWID/serial strings. This supports stable device IDs and multipath/WWID matching.

## Main Functions
- `format_general_id` trims leading/trailing spaces, replaces individual internal spaces with underscores, and skips quotes, non-ASCII, and non-printable characters.
- `format_t10_id` performs similar cleanup for T10 IDs but collapses a run of spaces into a single underscore.
- `_to_hex` converts binary identifier bytes to lowercase hex.
- `parse_vpd_ids` walks VPD page 0x83 designators and adds T10, EUI, NAA, or SCSI-name-string IDs to a `dev_wwid` list.
- `parse_vpd_serial` parses VPD page 0x80 serial data, strips surrounding whitespace, bounds length, and writes a NUL-terminated serial.

## Important Control Flow
`parse_vpd_ids` starts after the four-byte VPD header and advances by `d[3] + 4` for each designator. It recognizes designator types 0x1 (T10 vendor ID), 0x2 (EUI-64/12/16-byte EUI), 0x3 (NAA 8/16-byte), and 0x8 (SCSI name string). SCSI name strings beginning with `eui.` or `naa.` are lowercased and categorized as EUI/NAA; other SCSI name strings are stored with type 8 for multipath checking but are not standard device-ID types.

## Dependencies
Depends on `device.h` and `device_id.h` for `DEV_WWID_SIZE` and `dev_add_scsi_wwid`.

## Risk Notes
- Output normalization must remain compatible with existing `system.devices` IDNAME values.
- The parser clamps overlong T10/name designators to the available buffer but relies on well-formed page iteration lengths.
- `parse_vpd_serial` reads length from bytes 2 and 3 and trims using `in + 4`; callers must pass enough VPD data for that header.
