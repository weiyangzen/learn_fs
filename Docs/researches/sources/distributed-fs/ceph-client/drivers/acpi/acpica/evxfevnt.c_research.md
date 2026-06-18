# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evxfevnt.c

## Purpose
`evxfevnt.c` provides external interfaces for switching ACPI mode and controlling fixed ACPI events on non-reduced hardware.

## Important APIs, Types, And Functions
Exports are `acpi_enable`, `acpi_disable`, `acpi_enable_event`, `acpi_disable_event`, `acpi_clear_event`, and `acpi_get_event_status`. It relies on `acpi_gbl_fadt_index`, `acpi_gbl_reduced_hardware`, `acpi_gbl_fixed_event_info`, `acpi_gbl_fixed_event_handlers`, `acpi_hw_get_mode`, `acpi_hw_set_mode`, `acpi_read_bit_register`, and `acpi_write_bit_register`.

## Control Flow
`acpi_enable` validates that ACPI tables exist, no-ops on reduced-hardware or already-ACPI systems, requests ACPI mode through hardware, then polls up to 30,000 times at 100 microseconds per loop for mode confirmation. `acpi_disable` no-ops on reduced hardware or already-legacy systems, otherwise requests legacy mode. Fixed event enable/disable validates the event index, writes the enable bit, reads it back, and returns `AE_NO_HARDWARE_RESPONSE` if the bit did not change. Clearing writes the status bit with `ACPI_CLEAR_STATUS`. Status reads combine installed-handler, enable-bit, and status-bit information into `acpi_event_status`.

## State And Persistence
The ACPI/legacy mode transition changes platform hardware state. Fixed event operations update PM register bits. Handler presence is read from global handler slots but handler registration itself lives in `evxface.c`.

## Dependencies And Integration Points
These APIs are used by subsystem enable/disable code and fixed-event handler registration. They integrate with FADT-derived register metadata, ACPICA hardware access helpers, and event names for diagnostics. The whole module is excluded when reduced hardware support removes fixed event registers.

## Risks
Hardware may ignore mode or enable-bit transitions, and the code explicitly reports that as no response. The long ACPI-mode polling loop can add startup latency on slow firmware. Callers must not assume fixed events exist on reduced-hardware systems because these functions compile out or no-op in that configuration.

## Test Signals
Mock hardware tests should verify ACPI-mode success, timeout, already-enabled mode, missing FADT, fixed event bad-index rejection, enable/disable readback failure, status flag composition, and clear-status writes.
