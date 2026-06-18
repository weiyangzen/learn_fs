# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int340x_thermal_zone.h

## Purpose

`int340x_thermal_zone.h` declares the common INT340x thermal-zone contract shared by ACPI participant drivers.

## Important APIs, Types, and Functions

Constants define ten active trips plus critical/hot/passive defaults. `struct active_trip` describes a candidate active trip. `struct int34x_thermal_zone` stores the ACPI device, auxiliary trip count, Linux thermal zone, caller private data, and LPAT table. Prototypes expose add/remove/update helpers. Inline helpers set/get private data and wrap `thermal_zone_device_update()`.

## Control Flow

The header has no runtime control flow. It establishes the call contract used by individual participant drivers during probe, notification handling, and remove.

## State and Persistence Behavior

The structure is runtime-only state allocated by `int340x_thermal_zone_add()` and released by `int340x_thermal_zone_remove()`. The private-data pointer lets caller drivers associate their own context without changing the shared helper.

## Dependencies and Integration Points

The header depends on `acpi/acpi_lpat.h` and thermal-core declarations from included users. It is the integration point between INT340x participant drivers and the shared zone implementation.

## Risks and Test Signals

Risks are ABI-like local coupling: changes to `struct int34x_thermal_zone` or inline update helpers affect all participant drivers. Test signals are compile coverage across INT3402/INT3403/processor users and runtime update calls through the inline wrapper.
