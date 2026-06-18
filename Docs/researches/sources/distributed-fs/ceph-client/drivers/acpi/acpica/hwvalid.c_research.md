<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwvalid.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwvalid.c

## Purpose
Implements ACPICA validation for AML system-I/O port accesses. It enforces protected port ranges for DMA, PIC, PIT, RTC/CMOS, PCI config, and related legacy hardware, while preserving compatibility by allowing byte-granular partial access around illegal bytes.

## Important APIs, Types, And Functions
Core routines are `acpi_hw_validate_io_request`, `acpi_hw_read_port`, `acpi_hw_write_port`, and `acpi_hw_validate_io_block`. The central table is `acpi_protected_ports[]` of `struct acpi_port_info`, keyed by port range and `_OSI` dependency, plus globals `acpi_gbl_osi_data` and `acpi_gbl_truncate_io_addresses`.

## Control Flow
Validation accepts only 8/16/32-bit accesses, computes the byte range, rejects requests above 64 KiB, then scans the ordered protected-port table for overlap. Always-illegal ranges and ranges matching the BIOS-selected `_OSI` compatibility level return `AE_AML_ILLEGAL_ADDRESS`. Read/write wrappers optionally truncate addresses to 16 bits, try a whole access first, and on illegal-address status retry one byte at a time, skipping protected bytes but preserving readable/writable unprotected bytes. Block validation repeats request validation for each register-sized element.

## State And Persistence
No persistent state is stored here, but behavior depends on global `_OSI` data and the truncate-I/O-address compatibility flag set during namespace/device initialization.

## Dependencies And Integration Points
Wraps OSL port I/O (`acpi_os_read_port`, `acpi_os_write_port`) and is used by ACPICA region/register access paths. The rules mirror Microsoft ACPI compatibility restrictions.

## Risks And Edge Cases
Incorrect table ordering would break the early-exit scan. Partial-byte fallback can mask firmware bugs and produce synthetic values with skipped bytes zeroed. `_OSI` compatibility changes whether some ports are blocked. Address truncation can redirect accesses on systems with invalid firmware addresses.

## Test Signals
Exercise protected and unprotected ranges, overlap at start/end/full containment, invalid widths, above-64K requests, `_OSI`-dependent behavior, truncate mode, and partial reads/writes spanning protected and unprotected bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwvalid.c -->
