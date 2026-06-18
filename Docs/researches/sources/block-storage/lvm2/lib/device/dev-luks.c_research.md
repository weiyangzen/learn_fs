# File Research: sources/block-storage/lvm2/lib/device/dev-luks.c

## Purpose
Detects LUKS signatures at the start of a device.

## Core Behavior
`dev_is_luks()` reads six bytes at offset 0 and compares them with `LUKS\xba\xbe`. It sets `offset_found` to 0 when provided, returns 1 for a match, 0 for no match, and -1 if the read fails.

## Integration
Used by device-type/signature checks to avoid treating encrypted containers as plain LVM PV candidates.

## Risk Notes
Only the primary header at offset 0 is checked here; the `full` parameter is unused.
