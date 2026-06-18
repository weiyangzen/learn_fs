# sources/distributed-fs/ceph-client/drivers/acpi/arm64/init.h

## Purpose
Declares ARM64 ACPI initialization entry points shared by `init.c` and optional table parser files.

## Important APIs, Types, And Functions
Declares `acpi_agdi_init()`, `acpi_apmt_init()`, `acpi_iort_init()`, and `acpi_amba_init()`.

## Control Flow
No runtime control flow. The header enables `init.c` to call per-feature initialization functions.

## State And Persistence
No state.

## Dependencies And Integration Points
Includes `<linux/init.h>` for `__init` annotations and ties together the ARM64 ACPI init files.

## Risks
Prototype drift could cause build warnings or incorrect section annotations.

## Test Signals
Build with all optional feature combinations and verify declarations match definitions.
