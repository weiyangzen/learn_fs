# File Research: sources/block-storage/lvm2/lib/device/online.h

## Purpose
Declares pvscan online-state structures, logging wrappers, and APIs for transient PV/VG online files.

## Main Contents
- `struct pv_online` stores list linkage, optional matched device pointer, devno, PVID, VG name, and devname from online files.
- `log_print_pvscan` and `log_error_pvscan` avoid duplicate `pvscan[pid]` prefixes when output is already going to udev/journal style output.
- Function declarations cover PV online file read/create/exists, VG online create/remove, directory setup, PV online listing, VG lookup listing, list cleanup, lookup-file removal, and VG removal cleanup.

## Dependencies
Includes command context and device definitions for ID/name lengths and device objects.

## Risk Notes
The logging macros depend on `cmd->udevoutput`; callers outside pvscan-like contexts should ensure the command context is valid.
