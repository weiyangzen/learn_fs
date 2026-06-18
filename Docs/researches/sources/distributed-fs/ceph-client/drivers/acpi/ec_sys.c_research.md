# sources/distributed-fs/ceph-client/drivers/acpi/ec_sys.c

Purpose: `ec_sys.c` exposes the first ACPI EC through debugfs for diagnostics. It creates `debugfs/ec/ec0/` with read-only metadata and an `io` file that lets privileged users read the 256-byte EC address space, with optional writes behind the dangerous `write_support` module parameter.

Important APIs, types, and functions: the file uses `ec_read()` and `ec_write()` exported by `ec.c`, debugfs helpers, and user-copy helpers. Main functions are `acpi_ec_read_io()`, `acpi_ec_write_io()`, `acpi_ec_add_debugfs()`, `acpi_ec_sys_init()`, and `acpi_ec_sys_exit()`. `EC_SPACE_SIZE` fixes the exposed EC range at 256 bytes.

Control flow: module init checks `first_ec` and creates the debugfs tree. Reads clamp the requested range to EC address space, loop byte-by-byte from `*off`, call `ec_read()`, copy each byte to userspace, and update the file offset. Writes are rejected unless `write_support` is set, then similarly clamp and loop through `get_user()` plus `ec_write()`. Exit recursively removes the debugfs root.

State and persistence: persistent state is limited to the debugfs dentry pointer and the module parameter. EC contents are hardware state owned by firmware. The implementation currently uses `first_ec` even though `acpi_ec_add_debugfs()` accepts an EC pointer; comments note future multi-EC support.

Dependencies and integration: this is a debug companion to the EC driver, not the primary ACPI EC path. It integrates with debugfs and the `ec.c` global EC exports, so it only works after the core driver has found `first_ec`.

Risks: writes can corrupt firmware-controlled EC state and are intentionally gated. The read/write loops return partial lengths on user-copy failures but return EC errors immediately, so tooling must handle short I/O. Use of `first_ec` in debugfs metadata and operations means multi-EC systems are not represented accurately.

Test signals: verify debugfs creation when an EC exists, absence or harmless init when no EC exists, offset clamping at 256 bytes, partial read/write behavior, permissions with and without `write_support`, and that EC access errors propagate to userspace.
