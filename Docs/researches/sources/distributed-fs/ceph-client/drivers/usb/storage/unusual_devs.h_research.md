# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_devs.h

## Purpose

`unusual_devs.h` is the main usb-storage unusual-device database. It maps hundreds of vendor/product/revision ranges to protocol overrides, transport overrides, initializer functions, and `US_FL_*` quirk flags, then appends generic `USUAL_DEV()` class matches for standard mass-storage subclasses and transports.

## Important APIs, Types, and Functions

The file is pure macro data and requires `UNUSUAL_DEV`, `COMPLIANT_DEV`, and `USUAL_DEV` to be defined by the includer. It contains roughly 340 device/class entries. Important fields are VID, PID, bcdDevice min/max, short vendor/product names, protocol (`USB_SC_*`), transport (`USB_PR_*`), initializer such as `usb_stor_euscsi_init` or `sierra_ms_init`, and flags such as `US_FL_IGNORE_RESIDUE`, `US_FL_FIX_CAPACITY`, `US_FL_FIX_INQUIRY`, `US_FL_SINGLE_LUN`, `US_FL_IGNORE_UAS`, `US_FL_BROKEN_FUA`, `US_FL_NO_REPORT_OPCODES`, and `US_FL_ALWAYS_SYNC`.

## Control Flow

`usb.c` expands this file into `us_unusual_dev_list[]`, which is parallel to `usb_storage_usb_ids[]` from `usual-tables.c`. `storage_probe()` uses the matched USB ID index to locate the matching unusual metadata, then `get_device_info()`, `get_transport()`, and `get_protocol()` configure `struct us_data`. Initializers run in `usb_stor_acquire_resources()` before the control thread starts. `usual-tables.c` also expands the file into the public USB device ID table used for module matching.

## State and Persistence Behavior

The file has no runtime storage of its own, but it determines per-device in-memory flags and function pointers. Those flags affect SCSI scanning, inquiry data, cache/FUA behavior, residue interpretation, UAS fallback, capacity handling, and reset behavior. There is no filesystem persistence.

## Dependencies and Integration Points

It depends on usb-storage protocol constants, transport constants, initializer declarations from headers such as `sierra_ms.h` and `option_ms.h`, and quirk flag definitions from `linux/usb_usual.h`. It integrates with both the kernel module alias table and usb-storage's runtime metadata table; line-for-line alignment between those expansions is part of the contract.

## Risks and Edge Cases

This table is high-risk because entries are compatibility policy. Overly broad revision ranges can apply quirks to devices that no longer need them; overly narrow ranges can leave broken firmware on the generic path. Vendor/product strings are reused for fake inquiry data and should stay within legacy size expectations when `US_FL_FIX_INQUIRY` is used. The parallel-table invariant between `usb_storage_usb_ids[]` and `us_unusual_dev_list[]` must be preserved.

## Test Signals

Run compile checks for table expansion, verify module aliases, and regression-test representative devices for each major flag: ignored devices, fixed inquiry, capacity fixes, bad residues, single LUN, SCM multi-target, UAS ignore, broken FUA, sync-cache behavior, and initializer-backed devices. Static checks should confirm each non-NULL initializer is declared and linked.
