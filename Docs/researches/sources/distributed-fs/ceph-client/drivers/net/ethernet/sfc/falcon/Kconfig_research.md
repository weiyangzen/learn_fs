# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/Kconfig

## Purpose
This Kconfig fragment defines build-time configuration for the legacy Solarflare SFC4000/Falcon driver. `SFC_FALCON` enables the main network driver, and `SFC_FALCON_MTD` optionally exposes onboard flash/EEPROM as MTD devices for boot configuration updates.

## Important APIs, Types, and Functions
The file defines two symbols rather than C APIs. `SFC_FALCON` is a tristate depending on `PCI` and selecting `MDIO`, `CRC32`, `I2C`, and `I2C_ALGOBIT`. `SFC_FALCON_MTD` is a bool depending on `SFC_FALCON`, `MTD`, and a built-in/module compatibility condition that prevents built-in Falcon code from depending on modular MTD.

## Control Flow
Kconfig control flow is dependency resolution. Enabling `SFC_FALCON` permits the `sfc-falcon` module or built-in object to be built. Enabling `SFC_FALCON_MTD` causes `mtd.o` to be included by the Makefile and enables the MTD code paths guarded by `CONFIG_SFC_FALCON_MTD`.

## State and Persistence
The only persistence is generated kernel configuration. At runtime this affects whether the driver can be loaded and whether flash/EEPROM partitions appear as MTD devices.

## Dependencies and Integration Points
This integrates with the kernel networking, PCI, MDIO, I2C, CRC32, and MTD subsystems. The Makefile consumes `CONFIG_SFC_FALCON` and `CONFIG_SFC_FALCON_MTD` to build `sfc-falcon.o` and optional `mtd.o`.

## Risks
Incorrect dependency constraints can create invalid built-in/module combinations or missing subsystem symbols. The default `SFC_FALCON_MTD=y` means enabling MTD alongside the driver exposes device flash interfaces unless explicitly disabled, which may matter for systems that want to avoid flash write surfaces.

## Test Signals
Configuration tests should cover built-in and module combinations: `SFC_FALCON=m`, `SFC_FALCON=y`, `MTD=m`, `MTD=y`, and `SFC_FALCON_MTD` enabled/disabled. Build signals are successful linkage and the expected `sfc-falcon` module name.
