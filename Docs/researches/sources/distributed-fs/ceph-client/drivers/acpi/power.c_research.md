<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/power.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/power.c

## Purpose
`power.c` manages ACPI Power Resources: firmware objects that represent software-controllable power or clock planes shared by ACPI devices. It extracts power-resource references from device packages, creates ACPI power-resource devices, maintains reference counts, turns resources on/off for device D-state and wake transitions, exposes sysfs links, and handles resume/unused-resource quirks.

## Important APIs, Types, and Functions
Important types are `struct acpi_power_resource`, `struct acpi_power_resource_entry`, and `struct acpi_power_dependent_device`. Public functions include `acpi_extract_power_resources()`, `acpi_power_resources_list_free()`, `acpi_device_power_add_dependent()`, `acpi_device_power_remove_dependent()`, `acpi_power_add_remove_device()`, `acpi_power_wakeup_list_init()`, `acpi_device_sleep_wake()`, `acpi_enable_wakeup_device_power()`, `acpi_disable_wakeup_device_power()`, `acpi_power_get_inferred_state()`, `acpi_power_on_resources()`, `acpi_power_transition()`, `acpi_add_power_resource()`, `acpi_resume_power_resources()`, `acpi_turn_off_unused_power_resources()`, and `acpi_power_resources_init()`.

## Control Flow and State
Power resource extraction validates ACPI reference packages, skips duplicates, creates missing power-resource devices, and inserts entries ordered by firmware resource order. `acpi_add_power_resource()` evaluates the power resource object for system level/order, initializes state from `_STA` or turns it on if state cannot be read, ties and adds the ACPI device, creates `resource_in_use`, and appends it globally. On transitions, the target D-state resources are powered on first, then current-state resources are powered off, preserving power during state changes. Wake enable increments `prepare_count`, powers wake resources, and calls `_DSW` or `_PSW`; wake disable reverses that when the count reaches zero. Resume re-reads resource states and powers on referenced resources that firmware left off, including an HP GP12/PXP off-on quirk.

## State and Persistence
Persistent state includes the global ordered `acpi_power_resource_list`, each resource's cached state, reference count, order/system level, dependent device list, and wake prepare counts in ACPI devices. Firmware methods `_ON`, `_OFF`, `_STA`, `_DSW`, and `_PSW` mutate platform power state. DMI quirk booleans persist after init.

## Dependencies and Integration Points
The file depends on ACPI device core, power-resource package parsing, sysfs, runtime PM, suspend/resume, DMI, ACPI sleep internals, and device power state data in `struct acpi_device`. It integrates with PCI and other bus drivers that add dependents so devices can be runtime-resumed when a shared resource turns back on.

## Risks and Test Signals
Risks include reference-count imbalance leaving rails on/off, firmware `_STA` failures causing forced `_ON`, rollback complexity when list power-on/off partially fails, sysfs link creation failures hiding resource topology, DMI quirk coverage for buggy firmware, and concurrent access requiring the global and per-resource locks. Test signals are correct power resource sysfs groups/links, `resource_in_use` values, D-state transitions preserving dependencies, wake enable/disable counts, suspend/hibernate resume of referenced resources, unused resources turning off except quirked systems, and no inaccessible devices after thaw.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/power.c -->
