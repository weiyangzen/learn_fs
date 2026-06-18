# sources/distributed-fs/ceph-client/drivers/mmc/host/of_mmc_spi.c

## Purpose
`of_mmc_spi.c` is a small OpenFirmware/fwnode adapter for the generic MMC-over-SPI driver. It builds `struct mmc_spi_platform_data` from firmware properties when the SPI device has no explicit platform data.

## Important APIs, Types, And Functions
`struct of_mmc_spi` wraps `mmc_spi_platform_data` and a detect IRQ. `mmc_spi_get_pdata()` allocates the wrapper, parses voltage OCR with `mmc_of_parse_voltage()`, configures card-detect IRQ callbacks or polling, reads high-speed capability properties, and installs `dev->platform_data`. `mmc_spi_put_pdata()` frees firmware-created platform data. `of_mmc_spi_init()` and `of_mmc_spi_exit()` request/free the threaded detect IRQ.

## Control Flow
The SPI MMC driver calls `mmc_spi_get_pdata()` during setup. If platform data already exists or the device has no firmware node, the existing pointer is returned. Otherwise firmware-derived data is allocated, populated, and stored on the device. On teardown, `mmc_spi_put_pdata()` frees only firmware-generated data.

## State And Persistence
The only stored state is heap-allocated platform data attached to `dev->platform_data`. It persists for the SPI device lifetime and is not durable.

## Dependencies And Integration Points
This file integrates firmware property parsing, OF IRQ/SPI device information, MMC core voltage parsing, and the generic `mmc_spi` platform-data contract. Its exported symbols are consumed by the MMC SPI host driver.

## Risks And Test Signals
Risks are mostly lifecycle-related: freeing only data owned by this adapter, avoiding misuse when real platform data exists, and ensuring `dev_get_drvdata()` already provides the `mmc_host` before voltage parsing. Test signals include DT SPI MMC probe, high-speed property propagation, IRQ versus polling detect selection, and clean remove without leaks or double frees.
