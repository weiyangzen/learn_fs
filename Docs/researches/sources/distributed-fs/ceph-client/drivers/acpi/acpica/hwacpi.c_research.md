# sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwacpi.c

## Purpose
`hwacpi.c` controls ACPI versus legacy system mode transitions and reports the current ACPI hardware mode.

## Important APIs, Types, and Functions
Exports are `acpi_hw_set_mode()` and `acpi_hw_get_mode()`, compiled when `!ACPI_REDUCED_HARDWARE`. They use `acpi_gbl_reduced_hardware`, `acpi_gbl_FADT.smi_command`, `acpi_gbl_FADT.acpi_enable`, `acpi_gbl_FADT.acpi_disable`, `acpi_hw_write_port()`, and `acpi_read_bit_register(ACPI_BITREG_SCI_ENABLE)`.

## Control Flow, State, and Persistence
Reduced-hardware systems always report success/ACPI mode. `acpi_hw_set_mode()` validates that SMI command and enable/disable values exist, then writes the ACPI enable or disable byte to the SMI command port. `acpi_hw_get_mode()` returns ACPI mode if no transition mechanism exists, otherwise reads `SCI_EN`; read failure is treated as legacy mode.

## Dependencies and Integration Points
This file is part of ACPICA hardware initialization and shutdown paths. It depends on normalized FADT contents and port I/O helpers, and it coordinates with fixed-event/GPE setup expectations around mode transitions.

## Risks and Test Signals
Risks include treating absent mode-transition support as success, hardware/firmware not responding to SMI writes, reduced-hardware compile/runtime paths, and SCI_EN read failures causing legacy reports. Tests should cover reduced-hardware mode, missing SMI command, zero enable/disable values, ACPI and legacy transition writes, invalid mode input, SCI_EN true/false, and port I/O error propagation.
