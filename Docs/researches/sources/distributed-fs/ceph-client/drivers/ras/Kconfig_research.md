# sources/distributed-fs/ceph-client/drivers/ras/Kconfig

## Purpose
Top-level Kconfig menu for Reliability, Availability, and Serviceability features.

## Important APIs, types, and functions
Defines `menuconfig RAS` with explanatory help text. When enabled, it sources `arch/x86/ras/Kconfig` and `drivers/ras/amd/atl/Kconfig`, and defines `RAS_FMPM`, a tristate FRU Memory Poison Manager depending on `AMD_ATL && ACPI_APEI` and defaulting to module.

## Control flow
No runtime control flow. The `if RAS` block gates submenus and the FMPM symbol.

## State and persistence
Configuration persists in the kernel `.config`. Runtime persistence described here belongs to FMPM, which stores memory poison information through ACPI ERST in UEFI CPER FRU Memory Poison section format.

## Dependencies and integration
Integrates architecture RAS options, AMD ATL, ACPI APEI, and the RAS Makefile. `RAS_FMPM` depends on AMD address translation because poison records need platform-specific address conversion.

## Risks
Disabling `RAS` hides all nested features, including AMD ATL and FMPM. Defaulting FMPM to module when dependencies are met may surprise minimal builds.

## Test signals
Kconfig visibility and dependency tests for `RAS`, `AMD_ATL`, and `RAS_FMPM`, plus build coverage with RAS disabled, built-in, and module-capable configurations.
