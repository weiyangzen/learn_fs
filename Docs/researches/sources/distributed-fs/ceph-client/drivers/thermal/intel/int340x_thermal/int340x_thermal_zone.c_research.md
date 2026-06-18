# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int340x_thermal_zone.c

## Purpose

`int340x_thermal_zone.c` is the shared thermal-zone implementation for INT340x ACPI participants. It converts ACPI temperature/trip methods into Linux thermal zone operations, including optional LPAT raw-to-temperature conversion.

## Important APIs, Types, and Functions

Exports are `int340x_thermal_zone_add()`, `int340x_thermal_zone_remove()`, and `int340x_thermal_update_trips()`. `int340x_thermal_get_zone_temp()` reads `_TMP`, converts through LPAT when present, otherwise converts deci-Kelvin to millicelsius. `int340x_thermal_set_trip_temp()` writes active/passive auxiliary trip methods `PATn`. `int340x_thermal_read_trips()` collects critical, hot, passive, and active ACPI trips. `int340x_update_one_trip()` refreshes existing trip temperatures.

## Control Flow

Add allocates `struct int34x_thermal_zone`, reads auxiliary trip count from `PATC`, pre-creates writable passive trips, appends standard ACPI trips, reads hysteresis from `GTSH`, obtains an LPAT table, registers a no-hwmon thermal zone with trips, and enables it. Update iterates each registered trip and refreshes its temperature from ACPI, invalidating trips that are no longer available.

## State and Persistence Behavior

The helper owns the zone object, LPAT conversion table, and registered thermal-zone lifetime. Trip data is copied into the thermal core during registration. Firmware remains the source of temperature and trip values; no file-backed persistence exists.

## Dependencies and Integration Points

It depends on ACPI thermal helpers, ACPI LPAT, thermal zone APIs, and unit conversion helpers. INT3402, INT3403, and processor thermal drivers use it to avoid duplicating ACPI zone logic.

## Risks and Test Signals

Risks include trip-count bounds when firmware reports many `PATC` entries, `PATn` name generation limited to indexes 0-9, LPAT conversion failures, and dynamic trip disappearance. Test signals include zones with every ACPI trip type, LPAT and non-LPAT `_TMP` conversion, writable active/passive trip writes, `GTSH` hysteresis, and update behavior after ACPI notifies.
