# sources/distributed-fs/ceph-client/drivers/acpi/acpi_lpat.c

## Purpose
`acpi_lpat.c` parses ACPI `LPAT` packages and provides linear conversion between raw sensor values and temperatures for thermal-related ACPI devices.

## Important APIs, Types, And Functions
Exported APIs are `acpi_lpat_raw_to_temp()`, `acpi_lpat_temp_to_raw()`, `acpi_lpat_get_conversion_table()`, and `acpi_lpat_free_conversion_table()`. The main data contract is `struct acpi_lpat_conversion_table`, containing an array of `struct acpi_lpat` raw/temperature points and a count.

## Control Flow
`acpi_lpat_get_conversion_table()` evaluates the `LPAT` object, requires a package with an even count of at least four integers, copies values into an allocated integer array, casts it as `struct acpi_lpat` points, and returns a table wrapper. Conversion functions find the adjacent segment containing the requested raw or temperature value and linearly interpolate between endpoints. The free helper releases both the point array and wrapper.

## State And Persistence
Conversion tables are caller-owned heap allocations. The file stores no global state.

## Dependencies And Integration Points
It depends on ACPI object evaluation and the public `<acpi/acpi_lpat.h>` definitions. Thermal and sensor drivers can call it when firmware provides LPAT calibration data.

## Risks
Conversion divides by `delta_raw` or `delta_temp`; malformed tables with duplicate raw or temperature endpoints can divide by zero. `temp_to_raw()` only handles ascending temperature ranges, while `raw_to_temp()` accepts either raw direction. The parser does not sort points or validate monotonicity.

## Test Signals
Tests should cover absent LPAT, malformed package count/type, successful parse/free, ascending and descending raw interpolation, out-of-range `-ENOENT`, and duplicate endpoint handling.
