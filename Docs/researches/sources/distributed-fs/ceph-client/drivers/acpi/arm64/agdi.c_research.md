# sources/distributed-fs/ceph-client/drivers/acpi/arm64/agdi.c

## Purpose
Parses the Arm Generic Diagnostic Dump and Reset Interface table and registers a panic-inducing SDEI or interrupt handler for diagnostic dump/reset events.

## Important APIs, Types, And Functions
`struct agdi_data` carries signaling mode, SDEI event, GSIV, NMI use, and IRQ. Main functions are `acpi_agdi_init()`, `agdi_probe()`, SDEI and interrupt probe/remove helpers, and the panic handlers.

## Control Flow
`acpi_agdi_init()` reads the AGDI table, prepares platform data from either GSIV or SDEI event fields, registers a platform device, and then registers the platform driver. Probe chooses interrupt or SDEI mode from the table flags. Interrupt mode registers a GSI, tries `request_nmi()` first, and falls back to `request_irq()`. SDEI mode registers and enables the event.

## State And Persistence
State lives in platform data copied from the ACPI table. Runtime state tracks the registered IRQ and whether it is an NMI. No persistent storage is used.

## Dependencies And Integration Points
Depends on ACPI table access, SDEI, GSI registration, NMI/IRQ APIs, platform devices, and ARM64 init dispatch.

## Risks
The handler intentionally panics the system. Remove paths can fail to unregister an in-progress SDEI event. Interrupt mode must unregister GSI and free the right NMI/IRQ kind.

## Test Signals
Check no-op behavior without AGDI table, interrupt and SDEI modes, NMI fallback to IRQ, GSI registration failure, SDEI unregister retry, and remove cleanup.
