# sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwregs.c

## Purpose
`hwregs.c` implements generic ACPI GAS register validation and read/write access plus fixed ACPI register helpers for PM1/PM2/timer/SMI and ACPI status clearing.

## Important APIs, Types, and Functions
Exports include `acpi_hw_validate_register()`, `acpi_hw_read()`, `acpi_hw_write()`, `acpi_hw_clear_acpi_status()`, `acpi_hw_get_bit_register_info()`, `acpi_hw_write_pm1_control()`, `acpi_hw_register_read()`, and `acpi_hw_register_write()`. Local helpers are `acpi_hw_get_access_bit_width()`, `acpi_hw_read_multiple()`, and `acpi_hw_write_multiple()`. Important inputs are `struct acpi_generic_address`, FADT GAS fields, `acpi_gbl_bit_register_info`, hardware locks, and fixed-register IDs.

## Control Flow, State, and Persistence
Access-width selection distinguishes FADT register-style GAS from region-style GAS, uses `access_width` when needed, rounds bit ranges to supported widths, enforces a 32-bit maximum for system I/O, and clamps to caller maximum. Validation rejects NULL/zero-address/unsupported-space/invalid-access-width registers and ensures requested register width fits the caller maximum. Generic read/write loops over access-width chunks in system memory or I/O and uses bit insertion/extraction to assemble or split a 64-bit value. Status clearing takes the hardware raw lock, clears PM1 fixed status, then clears all GPE blocks. Fixed register read/write dispatch handles PM1 A/B pairs, masks PM1 control write-only bits on read, preserves required PM1/PM2 control bits on write, writes zero to preserved PM1 status bits, and treats SMI command as port I/O. Multiple-register helpers OR PM1 A/B reads and write the same bit pattern to both blocks.

## Dependencies and Integration Points
This file underpins ACPICA public register accessors and sleep/event code. It integrates FADT register normalization, OS memory access, port I/O helpers, fixed-event/GPE event code, and hardware locking.

## Risks and Test Signals
Risks include access-width calculation for unusual GAS bit offsets, partial multi-access reads/writes after an error, reserved/write-only/preserved bit masking, optional PM1B handling, zero-address optional registers, reduced-hardware compile paths, and I/O-space width limits. Tests should cover FADT-style and region-style GAS inputs, memory and I/O reads/writes at 8/16/32/64 widths, invalid spaces/access widths, bit offsets spanning multiple accesses, PM1 status/enable/control read-write semantics, PM2 preservation, PM timer and SMI command access, PM1B absent/present, status clearing under lock, and GPE clear failure propagation.
