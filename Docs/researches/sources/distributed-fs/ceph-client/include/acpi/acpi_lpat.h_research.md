<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi_lpat.h -->
# sources/distributed-fs/ceph-client/include/acpi/acpi_lpat.h

## Purpose
`acpi_lpat.h` declares Linux helpers for ACPI LPAT conversion tables, which translate between raw sensor values and temperatures. LPAT is used by thermal and power-management code that obtains linear piecewise conversion data from firmware.

## Important APIs, types, and functions
The main data types are `struct acpi_lpat`, with `temp` and `raw` points, and `struct acpi_lpat_conversion_table`, with a point array and count. When `CONFIG_ACPI` is enabled, exported helpers are `acpi_lpat_raw_to_temp()`, `acpi_lpat_temp_to_raw()`, `acpi_lpat_get_conversion_table()`, and `acpi_lpat_free_conversion_table()`. Disabled builds provide simple stubs returning zero or `NULL`.

## Control flow
Enabled implementations obtain an LPAT package from an ACPI handle, build a conversion table, and perform interpolation or nearest-segment conversion in either direction. Callers free the allocated table after use. In non-ACPI builds, control flow short-circuits through inline stubs.

## State and persistence behavior
The conversion table is caller-owned runtime memory derived from firmware data. The raw LPAT source persists only in ACPI tables/methods; this header owns no global state.

## Dependencies and integration points
It depends on ACPI handle types and `CONFIG_ACPI`. Thermal drivers and Intel platform power/thermal code are typical consumers. The helper abstracts firmware encoding so drivers can reason in temperatures instead of device-specific raw values.

## Risks and test signals
Risks include malformed LPAT packages, non-monotonic points, divide-by-zero interpolation segments, overflow during conversion, memory leaks if callers skip `acpi_lpat_free_conversion_table()`, and misleading non-ACPI stubs returning zero. Test signals include valid multi-point tables, out-of-range raw/temp values, duplicate raw or temp points, package parse failures, and builds with `CONFIG_ACPI=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi_lpat.h -->
