# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc832x_rdb.c

## Purpose
`mpc832x_rdb.c` registers the MPC832x RDB board and contains legacy QUICC Engine SPI/MMC setup for boards without an `mmc-spi-slot` DT node.

## Important APIs, Types, and Functions
With QUICC Engine enabled, `mpc832x_spi_init()` configures par_io pins for SPI and SD-card signals, skips legacy setup if DT already has `mmc-spi-slot`, and registers an `mmc_spi` board-info entry through `fsl_spi_init()`. `of_fsl_spi_probe()` instantiates `mpc83xx_spi` platform devices from OF resources and IRQs. `mpc832x_rdb_setup_arch()` runs common setup and applies OF par_io config for UCC nodes.

## Control Flow, State, and Persistence
Legacy SPI platform devices and board-info registration persist after `machine_device_initcall`. Pinmux state is programmed into par_io hardware.

## Dependencies and Integration Points
It depends on QUICC Engine, par_io helpers, FSL SPI platform data, SPI/MMC core, OF address/IRQ resources, and shared 83xx PCI/IPIC hooks.

## Risks and Test Signals
Risks include duplicate legacy and DT-based MMC setup, hard-coded bus number `0x4c0`, chip-select GPIO pin assumptions, and fallback sysclk selection. Test signals are MMC-over-SPI detection, no duplicate device when `mmc-spi-slot` exists, UCC pin config, and board boot with PCI/IPIC.
