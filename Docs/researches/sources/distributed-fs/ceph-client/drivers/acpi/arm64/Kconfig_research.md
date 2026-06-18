# sources/distributed-fs/ceph-client/drivers/acpi/arm64/Kconfig

## Purpose
Declares ARM64 ACPI feature symbols for IORT, GTDT, AGDI, APMT, and MPAM.

## Important APIs, Types, And Functions
This is Kconfig metadata rather than C code. It defines `ACPI_IORT`, `ACPI_GTDT`, `ACPI_AGDI`, `ACPI_APMT`, and `ACPI_MPAM`. `ACPI_AGDI` has a user-visible prompt and depends on `ARM_SDE_INTERFACE`.

## Control Flow
The symbols control which ARM64 ACPI implementation files are built by the sibling Makefile.

## State And Persistence
Configuration state is persisted in kernel build configuration.

## Dependencies And Integration Points
Feeds the ARM64 ACPI Makefile and feature-specific init calls in `init.c`.

## Risks
Incorrect dependencies can build code without required architecture support or hide needed table parsers.

## Test Signals
Validate defconfig and randconfig coverage, especially AGDI with and without SDEI, and ensure built objects match enabled symbols.
