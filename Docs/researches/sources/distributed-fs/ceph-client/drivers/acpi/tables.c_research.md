# sources/distributed-fs/ceph-client/drivers/acpi/tables.c

## Purpose

`tables.c` provides early ACPI table discovery, parsing helpers, MADT entry logging, initrd/builtin ACPI table upgrade support, custom DSDT override hooks, table memory reservation, and boot parameters controlling MADT instance, checksum verification, and 32-bit FADT addresses.

## Important APIs, types, and functions

Core parsing APIs include `acpi_table_print_madt_entry()`, `acpi_table_parse_entries_array()`, `acpi_table_parse_cedt()`, `acpi_table_parse_entries()`, `acpi_table_parse_madt()`, and `acpi_table_parse()`. Early table lifecycle APIs are `acpi_table_upgrade()`, `acpi_os_physical_table_override()`, `acpi_os_table_override()`, `acpi_locate_initial_tables()`, `acpi_reserve_initial_tables()`, `acpi_table_init_complete()`, and `acpi_table_init()`. State includes `initial_tables[]`, `acpi_apic_instance`, `acpi_verify_table_checksum`, and, when enabled, initrd table storage metadata.

## Control flow

Early boot may call `acpi_table_upgrade()` to scan initrd or builtin initramfs files under `kernel/firmware/acpi/`, validate recognized signatures, length, and checksum, reject overrides under lockdown, allocate low physical memory, reserve it, and copy tables in early-mapped chunks. ACPICA calls the physical override hook to replace matching tables only when signature/OEM IDs match and revision increases; remaining non-RSDT/XSDT tables can be installed as additional tables. `acpi_locate_initial_tables()` configures checksum validation and calls `acpi_initialize_tables()`. `acpi_table_init_complete()` installs initrd tables and checks for multiple MADTs. Parse helpers fetch a table instance, call common subtable parsing or a whole-table handler, and release the table.

## State and persistence

Initial table descriptors are `__initdata` used during early boot. Upgraded tables are copied into reserved physical memory and persist as firmware table replacements/additions. The bitmap `acpi_initrd_installed` prevents the same initrd table from being both an override and an install. Kernel taint records unsafe custom DSDT override. `acpi_apic_instance` and checksum/FADT boot-parameter settings persist for boot-time parsing.

## Dependencies and integration points

The file depends on ACPICA table management, memblock and architecture memory reservation, early initrd/cpio scanning, security lockdown policy, kmemleak, ACPI library export macros, APIC/MADT users, and architecture/platform code that registers ACPI probe entries.

## Risks

This is early boot code with little recovery room. Incorrect table validation, copy sizing, or physical reservation can corrupt memory or install bad firmware descriptions. Override policy is security-sensitive and must honor lockdown. MADT instance selection affects interrupt controller topology. Disabling checksum verification is intentional for early mapping limits, but forcing verification can expose firmware checksum defects.

## Test signals

Exercise boot with normal firmware tables, multiple MADT instances, `acpi_apic_instance=`, `acpi_force_table_verification`, `acpi_force_32bit_fadt_addr`, initrd table upgrades with valid/invalid checksum and revision, lockdown rejection, custom DSDT builds, and parse helper users for MADT/CEDT subtables.
