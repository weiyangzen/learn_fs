# sources/distributed-fs/ceph-client/drivers/acpi/sysfs.c

## Purpose

`sysfs.c` builds the ACPI userspace sysfs interface. It exposes ACPICA debug and trace parameters, ACPI table binary files, selected raw table data regions, interrupt/GPE counters and controls, the ACPI preferred PM profile, and hotplug profile controls.

## Important APIs, types, and functions

Under `CONFIG_ACPI_DEBUG`, it defines debug-layer/level descriptors and trace parameter setters/getters. Table exposure uses `struct acpi_table_attr`, `struct acpi_data_attr`, `acpi_table_show()`, `acpi_table_attr_init()`, `acpi_sysfs_table_handler()`, and `acpi_tables_sysfs_init()`. Raw data support handles BERT and CCEL regions through `acpi_data_show()`. Interrupt statistics use `struct event_counter`, `acpi_global_event_handler()`, `counter_show()`, `counter_set()`, `acpi_gpe_apply_masked_gpes()`, and `acpi_irq_stats_init()`. Hotplug profile support is provided by `acpi_sysfs_add_hotplug_profile()`. Initialization entry is `acpi_sysfs_init()`.

## Control flow

Debug parameter reads format current ACPICA bitmasks; writes update ACPICA global debug state and trace method selection while temporarily disabling tracing. Table sysfs init creates `/sys/firmware/acpi/tables`, `data`, and `dynamic`, iterates existing ACPI tables by index, creates binary attributes with instance suffixes as needed, and emits kobject events. Dynamic table installs create entries under `dynamic`. Interrupt stats initialization allocates counters and attributes for all GPEs, fixed events, SCI totals, and error counters, then installs a global ACPI event handler. Counter writes can reset totals, enable/disable/clear/mask/unmask GPEs, enable/disable/clear fixed events, or set counts. `acpi_sysfs_init()` also creates hotplug and `pm_profile` attributes.

## State and persistence

Sysfs kobjects and attribute lists persist for the lifetime of the ACPI core. Table attributes reference ACPICA tables by signature/instance at read time rather than copying table contents. Raw BERT/CCEL attributes map physical memory on each read. Interrupt counters are in memory and resettable through sysfs. Boot parameter `acpi_mask_gpe=` stores an init bitmap that is applied during scan initialization.

## Dependencies and integration points

This file integrates with ACPICA debug globals, ACPICA table manager and dynamic table events, ACPI OS memory mapping, GPE/fixed-event APIs, the global `acpi_kobj`, scan hotplug profiles, kernel parameter infrastructure, and the lockdown/table-upgrade paths indirectly through table visibility.

## Risks

Sysfs layout is a user ABI. Table instance naming must avoid collisions and respect ACPICA reference lifetimes. Raw physical data reads must validate size/address and map only the requested firmware-defined regions. Interrupt control writes can affect system wake and event delivery; invalid handler/status handling must remain strict. Trace method name storage uses a fixed early-boot buffer and requires careful length checks.

## Test signals

Verify table files under `/sys/firmware/acpi/tables`, dynamic table install visibility, BERT/CCEL data reads, ACPICA debug/trace parameter read-write behavior, GPE/fixed-event counter increments, sysfs enable/disable/clear/mask/unmask operations, `acpi_mask_gpe=` boot behavior, hotplug profile creation, and rejected `force_remove=1`.
