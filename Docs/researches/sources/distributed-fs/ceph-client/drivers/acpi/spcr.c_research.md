# sources/distributed-fs/ceph-client/drivers/acpi/spcr.c

## Purpose

`spcr.c` parses the ACPI Serial Port Console Redirection table and turns it into Linux early console and preferred console configuration. It also detects UART-specific firmware errata for Qualcomm QDF2400/QDF2432 PL011-compatible hardware and APM/HPE X-Gene 16550-compatible UARTs.

## Important APIs, types, and functions

The exported global `qdf2400_e44_present` informs the PL011 driver about the Qualcomm busy-bit erratum. `qdf2400_erratum_44_present()` checks SPCR OEM fields for affected Qualcomm SoCs. `xgene_8250_erratum_present()` checks OEM fields for X-Gene 16550 register alignment issues. The public init function is `acpi_parse_spcr(bool enable_earlycon, bool enable_console)`.

## Control flow

`acpi_parse_spcr()` exits if ACPI is disabled or the SPCR table is missing. It derives `iotype` from the GAS address-space and access-width fields, maps the SPCR interface type to a console driver name (`pl011`, `uart`, or `sbi`), derives baud rate from precise baud rate or the encoded baud-rate field, applies Qualcomm and X-Gene errata overrides, formats a static console option string, optionally calls `setup_earlycon()`, optionally calls `add_preferred_console()`, and releases the table with `acpi_put_table()`.

## State and persistence

The console option buffer is static init storage. `qdf2400_e44_present` persists after parsing so later UART probing can apply the workaround even if the console itself is not using SPCR. No ACPI table data is retained after `acpi_put_table()`.

## Dependencies and integration points

The file depends on ACPICA table access, ACPI DBG2/SPCR constants, Linux console and earlycon registration, serial core naming conventions, and UART drivers that consume the chosen names and erratum flag.

## Risks

Wrong interface mapping or iotype selection can make early console unusable, which is especially costly for bring-up and headless systems. Access-width validation must remain conservative around broken firmware. Erratum detection is OEM-field based and may miss new affected revisions or overmatch if firmware reuses IDs incorrectly.

## Test signals

Boot with SPCR-specified PL011, 16550, SBSA, BCM2835, and RISC-V SBI consoles; verify earlycon and preferred console strings; test unsupported interface/baud paths; confirm QDF2400/QDF2432 and X-Gene erratum platforms select the expected workaround behavior.
