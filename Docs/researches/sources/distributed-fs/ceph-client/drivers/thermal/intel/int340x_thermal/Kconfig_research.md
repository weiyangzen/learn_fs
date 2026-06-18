# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/Kconfig

## Purpose
Kconfig definitions for ACPI INT340x thermal support. It defines the main `INT340X_THERMAL` feature, ACPI thermal relationship helper `ACPI_THERMAL_REL`, optional INT3406 display thermal driver, and `PROC_THERMAL_MMIO_RAPL`.

## Important APIs, Types, and Functions
No runtime APIs. Main symbols are `INT340X_THERMAL`, `ACPI_THERMAL_REL`, `INT3406_THERMAL`, and `PROC_THERMAL_MMIO_RAPL`.

## Control Flow
When `INT340X_THERMAL` is selected, it pulls in thermal netlink, ACPI relationship parsing, ACPI fan, ACPI thermal library, Intel SoC DTS IOSF core, Intel TCC, ACPI platform profile, and optional processor thermal MMIO RAPL if powercap is enabled. Additional options are visible only inside the `if INT340X_THERMAL` block.

## State and Persistence
No runtime state. Selections persist in kernel config.

## Dependencies and Integration Points
Integrates ACPI thermal firmware objects (INT3400 master and INT3401-INT340B slaves), userspace policy daemons such as thermald, display thermal management, ACPI fan, platform profile, and Intel processor thermal modules.

## Risks and Edge Cases
The main symbol has broad `select` behavior; selecting it can force several ACPI/Intel subsystems into the build. Missing dependencies for optional display or RAPL pieces would surface at build time.

## Test Signals
Kconfig tests should verify symbol visibility and selected dependencies for `INT340X_THERMAL`, with and without `POWERCAP`, and with `ACPI_VIDEO` for INT3406.
