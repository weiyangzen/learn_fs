# sources/distributed-fs/ceph-client/drivers/base/physical_location.c

## Purpose
Adds optional ACPI physical-location metadata to devices and exposes it through a `physical_location` sysfs attribute group.

## Important APIs, Types, And Functions
`dev_add_physical_location()` is the core entry point. It reads ACPI `_PLD` data into `struct acpi_pld_info`, allocates `dev->physical_location`, and copies panel, vertical position, horizontal position, dock, and lid flags. Sysfs show functions map enum values to strings for `panel`, `vertical_position`, `horizontal_position`, `dock`, and `lid`. `dev_attr_physical_location_group` publishes these attributes under a named group.

## Control Flow
Callers first check device physical location support through `dev_add_physical_location()`. The function refuses devices without an ACPI companion or without retrievable PLD data, allocates the driver-core physical-location object, copies fields, frees ACPI memory, and returns whether metadata was installed. Sysfs reads assume `dev->physical_location` is present and translate stored values without re-querying firmware.

## State And Persistence
The copied physical-location fields live in `dev->physical_location` for the lifetime of the device. They are derived from firmware and are not persisted locally. The sysfs group provides read-only ABI state to userspace.

## Dependencies And Integration
Depends on ACPI companion discovery, `acpi_get_physical_device_location()`, ACPI memory freeing, driver core device storage, sysfs, and `str_yes_no()` for boolean attributes. The paired header supplies no-op stubs when ACPI is disabled.

## Risks And Test Signals
Risks include assuming sysfs attributes are installed only when `dev->physical_location` is non-NULL, firmware enum values outside known ranges, and memory leaks if callers do not release the device field in core teardown. Test signals are ACPI devices with valid and missing `_PLD`, sysfs string output for all enum cases, and non-ACPI builds using the stubbed header.
