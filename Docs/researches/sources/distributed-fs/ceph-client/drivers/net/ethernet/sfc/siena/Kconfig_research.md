# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/Kconfig

## Purpose
Exposes the Solarflare SFC9000/Siena driver and optional feature support to kernel configuration.

## Important symbols
`SFC_SIENA` is the main tristate PCI/PTP driver option and selects MDIO and CRC32. `SFC_SIENA_MTD` exposes onboard flash/EEPROM through MTD. `SFC_SIENA_MCDI_MON` enables firmware-managed hwmon sensors. `SFC_SIENA_SRIOV` enables PCI SR-IOV. `SFC_SIENA_MCDI_LOGGING` enables sysfs-controlled MCDI command logging.

## Control flow and integration
These symbols control the Siena Makefile object list and conditional compilation in the driver. Dependency expressions avoid built-in code depending on modular MTD/HWMON providers.

## State and persistence behavior
The state is the kernel build configuration. Runtime behavior changes by adding or removing MTD, hwmon, SR-IOV, and MCDI logging interfaces.

## Dependencies
Integrates with PCI, PTP_1588_CLOCK, MTD, HWMON, PCI_IOV, MDIO, and CRC32 kernel configuration.

## Risks
Incorrect built-in/module dependency constraints can cause link failures. Default-enabled feature options increase compiled surface and debug/management expectations.

## Test signals
Build `SFC_SIENA` as built-in and module with MTD/HWMON/SR-IOV/logging toggled.
