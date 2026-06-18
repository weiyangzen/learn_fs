# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/storage_common.c

## Purpose
This file provides shared descriptors and logical-unit helper functions for USB mass-storage gadget functions. It centralizes FS/HS/SS bulk endpoint descriptors, interface descriptors, backing-file open/close logic, CD-ROM address formatting, and configfs/sysfs show/store helpers for LUN attributes.

## Important APIs, types, and functions
Exported descriptor objects include `fsg_intf_desc`, FS/HS/SS bulk IN and OUT endpoint descriptors, SuperSpeed companion descriptors, and descriptor arrays. `fsg_lun_open()` opens and validates a file or block device as LUN backing storage, sets block size and sector counts, handles CD-ROM minimum/maximum sizing, and updates read-only state. `fsg_lun_close()` releases the backing file. `fsg_lun_fsync_sub()` flushes writable media. Attribute helpers include `fsg_show_ro()`, `fsg_store_ro()`, `fsg_show_file()`, `fsg_store_file()`, `fsg_store_cdrom()`, `fsg_store_removable()`, `fsg_store_nofua()`, `fsg_store_inquiry_string()`, and `fsg_store_forced_eject()`.

## Control flow
Mass-storage functions import and patch shared descriptors during their bind paths, typically assigning endpoint addresses after autoconfiguration. LUN file changes flow through `fsg_store_file()`: prevent removal is checked, a trailing newline is stripped in place, `filesem` is taken for writing, and the helper either opens a new medium or closes the existing one while setting unit-attention sense data. `fsg_lun_open()` tries read-write first unless initially read-only, falls back to read-only on access/EROFS failures, validates regular or block devices, checks readability/writability, computes logical block size, enforces CD-ROM constraints, closes any prior medium, and installs the new file.

## State and persistence
The function mutates `struct fsg_lun`: backing `filp`, file length, sector count, `ro`, `initially_ro`, removable/CD-ROM flags, no-FUA flag, sense data, block size fields, and inquiry string. Backing files are persistent external objects, but the gadget stores only open file references and in-memory LUN state. Caller-provided `filesem` protects media changes and path display.

## Dependencies and integration points
The file depends on block device, VFS, USB composite, SCSI/storage constants, and `storage_common.h`. It exports symbols to mass-storage function implementations such as file-backed mass storage and related composite functions. It uses Linux VFS helpers like `filp_open()`, `fput()`, `i_size_read()`, `file_path()`, and `vfs_fsync()`.

## Risks and edge cases
`fsg_store_file()` casts away const and edits the input buffer to strip a newline, which assumes the caller supplies mutable sysfs/configfs storage. Read-only changes are rejected while media is open, but CD-ROM store uses a read lock while calling the same helper. Opening block devices depends on logical block-size reporting and size alignment. Forced eject clears `prevent_medium_removal` and detaches media regardless of host state, intentionally bypassing normal SCSI removal protection.

## Test signals
Test descriptor export consumers at FS/HS/SS, open regular files and block devices read-write and read-only, fallback on EROFS/EACCES, too-small and too-large CD-ROM images, ro/cdrom/removable/nofua attribute transitions, forced eject while prevented, path display for open and empty media, inquiry string formatting, and fsync behavior when toggling no-FUA.
