# sources/distributed-fs/ceph-client/drivers/acpi/acpi_configfs.c

## Purpose
`acpi_configfs.c` exposes a configfs interface under `/config/acpi/table` for host-directed dynamic ACPI SSDT table loading, inspection, and unloading.

## Important APIs, Types, And Functions
The central state is `struct acpi_table { config_item, header, index }`. Key functions are `acpi_table_aml_write()`, `get_header()`, `acpi_table_aml_read()`, metadata show functions for table header fields, `acpi_table_make_item()`, `acpi_table_drop_item()`, `acpi_configfs_init()`, and `acpi_configfs_exit()`. The binary attribute is `aml` with `MAX_ACPI_TABLE_SIZE` of 128 KiB.

## Control Flow
Module init registers the `acpi` configfs subsystem and creates the default `table` group. Creating an item allocates an empty `struct acpi_table`. Writing to its `aml` binary attribute checks lockdown policy, rejects duplicate loads, validates the supplied ACPI table length and `SSDT` signature, duplicates the table, and calls `acpi_load_table()` while retaining the returned index. Reads and text attributes require a loaded header. Dropping the item calls `acpi_unload_table(index)` and releases the config item.

## State And Persistence
Loaded SSDTs become live ACPI interpreter state until the configfs item is dropped or the module exits. The driver keeps an in-memory copy of the table header/body and ACPICA table index; it does not persist tables across reboot.

## Dependencies And Integration Points
It depends on configfs, ACPI table load/unload APIs, security lockdown (`LOCKDOWN_ACPI_TABLES`), and ACPICA header formats. It exposes metadata through configfs/sysfs attribute conventions.

## Risks
Dynamic table loading is privileged and potentially dangerous, so lockdown checks are central. Only SSDT signatures are accepted. `acpi_table_drop_item()` calls unload even when no table was loaded, relying on index initialization semantics. The binary read path copies `h->length` when `data` is supplied; callers rely on configfs size handling.

## Test Signals
Tests should cover lockdown denial, invalid length, non-SSDT signature, duplicate writes, successful load/read/show/unload, and cleanup during module exit with active configfs items.
