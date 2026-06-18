# sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/Kconfig

## Purpose
Defines the Aquantia PHY driver build option under the PHY driver menu.

## Important APIs, Types, and Functions
The `AQUANTIA_PHY` tristate symbol enables support for Aquantia AQ1202, AQ2104, AQR105, and AQR405-class devices and selects `CRC_ITU_T`, which is needed by the firmware loader for image and mailbox CRC validation.

## Control Flow and State
There is no runtime control flow. Build-time state is whether the Aquantia driver is disabled, built in, or built as a module. Selecting `CRC_ITU_T` ensures the helper is linked whenever the driver can call `crc_itu_t`.

## Dependencies and Integration Points
The symbol is sourced by the parent PHY Kconfig and consumed by `aquantia/Makefile`, which builds the multi-object `aquantia.o` module.

## Risks and Test Signals
Risks are missing helper selects or stale help text that under-represents the many newer AQR devices supported by `aquantia_main.c`. Test signals include `CONFIG_AQUANTIA_PHY=m/y` builds and confirming `CRC_ITU_T` is available for firmware-loading builds.
