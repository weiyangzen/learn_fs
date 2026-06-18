# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/Makefile

Purpose: build recipe for the SPI NOR framework and manufacturer tables.

Important APIs/types/functions: `spi-nor-objs` aggregates core files (`core.o`, `sfdp.o`, `swp.o`, `otp.o`, `sysfs.o`), manufacturer modules including `atmel.o`, optional `debugfs.o`, and emits `spi-nor.o` under `CONFIG_MTD_SPI_NOR`. It also descends into `controllers/` when SPI NOR is enabled.

Control flow and state: build-time only. Object list order determines what is linked into the composite SPI NOR module/built-in object.

Dependencies and integration: depends on Kconfig symbol `CONFIG_MTD_SPI_NOR` and `CONFIG_DEBUG_FS`. Risks include missing manufacturer object registration, controller directory not built when expected, and debugfs object coverage. Test signals include built-in and module builds, debugfs enabled/disabled builds, and verifying `spi_nor_atmel` and other manufacturer tables link.
