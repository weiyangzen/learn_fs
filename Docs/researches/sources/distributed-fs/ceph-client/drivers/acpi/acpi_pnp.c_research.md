# sources/distributed-fs/ceph-client/drivers/acpi/acpi_pnp.c

## Purpose
`acpi_pnp.c` identifies ACPI devices that should be treated as legacy PNP devices and registers an ACPI scan handler for a curated list of PNP-compatible IDs.

## Important APIs, Types, And Functions
The large `acpi_pnp_device_ids[]` table lists HIDs for storage, TPMs, keyboards, mice, serial/modem, IR, parallel ports, watchdogs, sound devices, touchscreens, and wildcard-style entries such as `WACFXXX`. Important functions are `matching_id()`, `acpi_pnp_match()`, `acpi_pnp_attach()`, exported `acpi_is_pnp_device()`, and `acpi_pnp_init()`.

## Control Flow
`acpi_pnp_init()` adds the scan handler. Matching compares a candidate ID to each table entry: lengths and first three bytes must match, positions 3 through 6 must be hex digits in the candidate, and the table can use `X` as a wildcard. Attach returns true to mark the ACPI device as handled by the PNP scan handler. `acpi_is_pnp_device()` checks whether a device's handler pointer is the PNP handler.

## State And Persistence
The only persistent state is the registered scan handler and handler association on matched ACPI devices. No per-device private data is allocated.

## Dependencies And Integration Points
It depends on ACPI scan infrastructure, ACPI device IDs, ctype helpers, and PNP/legacy bus coordination. `acpi_platform.c` uses related filtering to avoid creating duplicate platform devices for these classes.

## Risks
The ID table contains duplicates and many legacy IDs; changing it can alter which subsystem binds a device. `matching_id()` requires seven-character IDs, so nonstandard length IDs will not match. Wildcard behavior is limited to the numeric suffix positions.

## Test Signals
Tests should cover exact matches, lowercase hex candidate IDs, wildcard table entries, length mismatch, non-hex suffix rejection, duplicate IDs, and `acpi_is_pnp_device()` for matched and unmatched devices.
