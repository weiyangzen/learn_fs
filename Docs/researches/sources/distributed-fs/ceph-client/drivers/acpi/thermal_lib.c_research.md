# sources/distributed-fs/ceph-client/drivers/acpi/thermal_lib.c

## Purpose

`thermal_lib.c` provides reusable helpers for reading ACPI thermal trip-point temperatures from firmware. It centralizes ACPI method evaluation, sanity-range filtering, and conversion between ACPI deci-Kelvin and Linux thermal millicelsius APIs.

## Important APIs, types, and functions

`acpi_trip_temp()` is the private evaluator and validator. Namespaced GPL exports for ACPI thermal internals are `acpi_active_trip_temp()`, `acpi_passive_trip_temp()`, `acpi_hot_trip_temp()`, and `acpi_critical_trip_temp()`, returning deci-Kelvin or `THERMAL_TEMP_INVALID`. Generic thermal exports are `thermal_acpi_active_trip_temp()`, `thermal_acpi_passive_trip_temp()`, `thermal_acpi_hot_trip_temp()`, and `thermal_acpi_critical_trip_temp()`, returning millicelsius. Constants `TEMP_MIN_DECIK` and `TEMP_MAX_DECIK` bound plausible firmware values.

## Control flow

Each public helper builds or supplies the ACPI object name (`_ACx`, `_PSV`, `_HOT`, `_CRT`), evaluates it as an integer, treats evaluation failure as `-ENODATA`, marks out-of-range values invalid, and optionally converts valid deci-Kelvin temperatures to millicelsius.

## State and persistence

The file has no mutable persistent state. It only returns evaluated firmware values to callers.

## Dependencies and integration points

It depends on `acpi_evaluate_integer()`, ACPI device handles, `THERMAL_TEMP_INVALID`, and unit conversion helpers. `thermal.c` imports the `ACPI_THERMAL` namespace for deci-Kelvin helpers; other thermal drivers can use the generic millicelsius wrappers.

## Risks

Range filtering is policy: too narrow a range can hide valid platform trips, while too broad a range can expose bogus firmware values to thermal policy. `_ACx` IDs are limited to 0 through 9 to match ACPI active trip naming. Callers must distinguish evaluation failure from an invalid but successfully evaluated temperature.

## Test signals

Unit or mocked ACPI evaluations should cover valid trips, out-of-range trips, missing methods, invalid active IDs, conversion to millicelsius, and integration with `thermal.c` trip initialization.
