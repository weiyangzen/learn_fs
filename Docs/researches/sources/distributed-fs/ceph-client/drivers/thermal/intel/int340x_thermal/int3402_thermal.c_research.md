# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int3402_thermal.c

## Purpose

`int3402_thermal.c` is the ACPI INT3402 participant driver for memory temperature reporting. It binds INT3402 ACPI platform devices that expose `_TMP`, creates a shared INT340x thermal zone, and forwards firmware thermal notifications to the Linux thermal core.

## Important APIs, Types, and Functions

Key state is `struct int3402_thermal_data`, which stores the ACPI handle and `struct int34x_thermal_zone`. `int3402_thermal_probe()` validates the ACPI companion and `_TMP`, allocates driver data, calls `int340x_thermal_zone_add()`, installs `int3402_notify()`, and stores platform drvdata. `int3402_notify()` handles `INT3402_THERMAL_EVENT` by calling `int340x_thermal_zone_device_update(..., THERMAL_TRIP_VIOLATED)`. `int3402_thermal_remove()` removes the ACPI notify handler and thermal zone.

## Control Flow

Probe succeeds only with an ACPI companion and temperature method. After registration, ACPI device notifications are the runtime trigger: event `0x90` refreshes thermal-zone policy evaluation, while performance-change event `0x80` is intentionally ignored. Removal unwinds notify registration before unregistering the thermal zone.

## State and Persistence Behavior

State is device-managed except for the shared thermal zone object allocated by the INT340x helper and explicitly removed. No values are persisted; the zone reads firmware temperature and trips on demand through ACPI.

## Dependencies and Integration Points

The driver depends on ACPI, platform bus, thermal core, and `int340x_thermal_zone.c`. It integrates with DPTF-style firmware via INT3402 notifications and Linux userspace via the registered thermal zone.

## Risks and Test Signals

Risks are missing `_TMP`, notify-handler registration failure after zone creation, firmware event storms, and assuming every INT3402 device is memory temperature capable. Test signals include module probe/remove on INT3402 ACPI nodes, `_TMP` conversion through the shared zone, ACPI notify `0x90` causing `thermal_zone_device_update()`, and error unwinding after forced notify install failures.
