
# sources/distributed-fs/ceph-client/drivers/firmware/efi/rci2-table.c

Purpose: validates a Dell Runtime Configuration Interface v2 EFI table and exposes it as a read-only admin sysfs binary file under `/sys/firmware/efi/tables/rci2`.

Important APIs/types/functions: uses `struct rci2_table_global_hdr`, global `rci2_table_phys`, static `checksum()`, and late init `efi_rci2_sysfs_init()`. The sysfs attribute is created with `BIN_ATTR_SIMPLE_ADMIN_RO(rci2)`.

Control flow: late init skips absent tables, maps the header, checks `_RC_` signature, reads full table length, remaps the full table, verifies 16-bit additive checksum equals zero, creates the `tables` kobject, attaches the mapped table as private data, and creates the binary sysfs file.

State and persistence behavior: `rci2_table_phys` is set during EFI table discovery elsewhere; `rci2_base` remains memremapped after successful sysfs creation and backs reads. No mutable runtime state exists after init.

Dependencies and integration points: depends on EFI kobject, memremap, sysfs, and firmware-provided RCI2 table address. User space consumes the binary table.

Risks and test signals: table length is read from firmware after only header mapping, so bogus lengths can cause remap failure. Checksum handles odd byte lengths. Test signals include absent table, bad signature, zero length, bad checksum, odd-length checksum, sysfs file size/content, and kobject creation failure.
