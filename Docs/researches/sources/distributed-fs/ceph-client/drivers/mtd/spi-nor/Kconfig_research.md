# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/Kconfig

Purpose: Kconfig menu for the SPI NOR subsystem and its software write-protection policy.

Important APIs/types/functions: `menuconfig MTD_SPI_NOR` enables the SPI NOR framework, depends on MTD and SPI master support, and selects SPI_MEM. `MTD_SPI_NOR_USE_4K_SECTORS` controls default small-sector erase use. The SWP choice selects one of disable-all, disable-only-volatile, or keep-current behavior. It sources controller Kconfig entries.

Control flow and state: not runtime code, but it shapes build-time availability and defaults. The selected symbols drive compiled objects and behavior in SPI NOR core and related parsers/drivers.

Dependencies and integration: integrates with `drivers/mtd/spi-nor/Makefile`, controller Kconfig, and code paths checking `CONFIG_MTD_SPI_NOR_USE_4K_SECTORS` such as `qcomsmempart.c`. Risks include default 4 KiB sectors breaking UBIFS or firmware partition expectations, SWP policy changing write availability, and duplicate `depends on MTD` line noise. Test signals include config matrix builds for each SWP choice, 4K-sector enabled/disabled behavior, and controller submenu visibility.
