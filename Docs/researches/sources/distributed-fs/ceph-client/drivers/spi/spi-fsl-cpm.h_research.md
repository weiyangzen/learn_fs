# sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-cpm.h

## Purpose
Declares the CPM/QE helper interface used by the classic Freescale SPI driver. It provides real prototypes when Freescale SoC support is enabled and harmless inline stubs otherwise, allowing `spi-fsl-spi.c` to compile across configurations.

## Important APIs, Types, And Functions
The header exposes `fsl_spi_cpm_reinit_txrx()`, `fsl_spi_cpm_bufs()`, `fsl_spi_cpm_bufs_complete()`, `fsl_spi_cpm_irq()`, `fsl_spi_cpm_init()`, and `fsl_spi_cpm_free()`. All functions operate on `struct mpc8xxx_spi`, and transfer execution accepts `struct spi_transfer`.

## Control Flow
There is no runtime control flow in the header. With `CONFIG_FSL_SOC`, calls bind to exported functions from `spi-fsl-cpm.c`. Without it, reinit/complete/irq/free become no-ops, init returns success, and buffer submission returns success.

## State And Persistence
The header owns no state. It defines the compile-time availability of CPM behavior for the parent driver.

## Dependencies And Integration Points
Includes `spi-fsl-lib.h` for `struct mpc8xxx_spi`. It is included by `spi-fsl-spi.c` and `spi-fsl-cpm.c`, bridging generic Freescale SPI code to optional CPM/QE support.

## Risks
The non-FSL stubs return success for buffer submission/init, so callers must only route real CPM transfers here when CPM mode is valid for the build/platform. Mismatch between flags and configuration could otherwise hide missing hardware support until transfer behavior is wrong.

## Test Signals
Build coverage with `CONFIG_FSL_SOC` on and off, CPM mode probe paths, and ensuring CPU-mode transfers do not accidentally depend on CPM symbols are the main signals.
