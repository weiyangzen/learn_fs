# sources/distributed-fs/ceph-client/drivers/acpi/acpi_fpdt.c

## Purpose
`acpi_fpdt.c` parses the ACPI Firmware Performance Data Table and exposes firmware boot and S3 suspend/resume timing data under `/sys/firmware/acpi/fpdt`.

## Important APIs, Types, And Functions
It defines FPDT subtable and record structures for FBPT, S3PT, boot, suspend, and resume records. Global record pointers are `record_resume`, `record_suspend`, and `record_boot`. Important functions are generated `*_show()` sysfs readers, `fpdt_address_valid()`, `fpdt_process_subtable()`, and `acpi_init_fpdt()`. Binary attributes `FBPT` and `S3PT` expose raw subtable bytes.

## Control Flow
`acpi_init_fpdt()` obtains the FPDT table, creates the `fpdt` kobject, iterates subtable entries, and processes FBPT or S3PT addresses. `fpdt_process_subtable()` validates the physical address, maps the subtable header, verifies the signature matches the type, remaps the full subtable, walks records by `record_header->length`, creates a sysfs group for the first boot/suspend/resume record of each type, and exposes raw binary attributes for the subtable. On parse errors it removes any groups and binary files it created.

## State And Persistence
Mapped FPDT subtables remain referenced through binary-attribute private pointers and record pointers for sysfs show functions. The data itself is firmware-provided memory. The code does not define an exit path because it is initialized with `fs_initcall()`.

## Dependencies And Integration Points
It depends on ACPI table APIs, ACPI OS physical memory mapping, sysfs/kobject infrastructure, `acpi_kobj`, and x86 physical address width checks when applicable.

## Risks
The record walk relies on firmware record lengths and only guards against zero length; malformed lengths can skip beyond expected layout if still below table length. Some error paths after remapping do not unmap the full subtable on failure. Duplicate records are ignored after logging, so only the first instance is exposed. Address validation is architecture-specific and minimal outside x86 physical-address-width checks.

## Test Signals
Tests should include no FPDT table, invalid high physical addresses, signature/type mismatch, zero-length records, duplicate records, boot-only and S3 records, raw `FBPT`/`S3PT` binary reads, and sysfs timing attribute values.
