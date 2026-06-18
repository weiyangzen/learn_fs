# sources/distributed-fs/ceph-client/drivers/acpi/arm64/init.c

## Purpose
Provides the ARM64 ACPI architecture initialization fan-out for optional table/device parsers.

## Important APIs, Types, And Functions
Defines `acpi_arch_init()`.

## Control Flow
At architecture ACPI init time, it conditionally calls `acpi_agdi_init()`, `acpi_apmt_init()`, `acpi_iort_init()`, and `acpi_amba_init()` based on build-time config.

## State And Persistence
No local state. It triggers registration side effects in the target modules.

## Dependencies And Integration Points
Depends on the declarations in `init.h` and the Makefile/Kconfig feature symbols.

## Risks
Ordering matters: table parsers that create platform devices run before later driver probes. Missing guards would create unresolved references when optional objects are disabled.

## Test Signals
Use config combinations to ensure each optional init is called only when built and that ACPI boot without optional tables remains quiet.
