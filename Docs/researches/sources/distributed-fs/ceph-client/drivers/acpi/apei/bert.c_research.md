## sources/distributed-fs/ceph-client/drivers/acpi/apei/bert.c

Purpose: `bert.c` implements APEI Boot Error Record Table support. It maps the BERT boot error region during late init, prints bounded CPER records from the previous boot, clears one-time-polled block status, and releases resources.

Important APIs and functions: `bert_print_all` walks `struct acpi_hest_generic_status` records in the BERT region, validates length and CPER status, prints at most five records shorter than 1024 bytes, counts skipped records, and clears `block_status`. `setup_bert_disable` handles the `bert_disable` boot parameter. `bert_check_table` validates table and region minimum sizes. `bert_init` is registered with `late_initcall`.

Control flow: initialization exits early if ACPI is disabled or `bert_disable` is set, obtains the BERT table with `acpi_get_table`, validates it, reserves the region through APEI resources, maps it with `ioremap_cache`, prints records, unmaps, releases resources, finalizes lists, and drops the ACPI table reference. `AE_NOT_FOUND` is a quiet no-op.

State and dependencies: `bert_disable` is `__initdata`. Firmware-provided BERT memory is persistent across boot until read; this code clears each printed/skipped record's `block_status` in the mapped region. Dependencies include CPER validation/printing, ACPI table services, I/O mapping, and APEI resource reservation.

Integration points: built into the base `apei.o` aggregate, BERT complements GHES/ERST by surfacing unhandled previous-boot hardware errors through kernel logs while leaving full table data available under ACPI table sysfs.

Risks: firmware may provide truncated, invalid, oversized, or excessive records. Region reservation and mapping can fail. Clearing block status mutates firmware error memory and should only happen after validation/walk decisions.

Test signals: no ACPI, disabled parameter, missing table, invalid table length, short region, resource request failure, map failure, valid multiple records, oversized/skipped records, truncated status block, invalid CPER status, zero block status terminator, and cleanup on every error path are important.
