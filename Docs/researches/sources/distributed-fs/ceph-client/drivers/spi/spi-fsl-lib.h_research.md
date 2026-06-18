# sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-lib.h

## Purpose
Defines the shared private structures and function prototypes for the classic Freescale SPI/eSPI drivers. It is the contract between common helper code, CPM support, and `spi-fsl-spi.c`.

## Important APIs, Types, And Functions
`struct mpc8xxx_spi` stores controller-private state including device, MMIO base, TX/RX pointers, CPM/QE PRAM and BDs, current transfer, DMA addresses and map flags, dummy DMA buffers, typed buffer callbacks, remaining count, IRQ, timing, input clock, shifts, mode flags, optional native chip-select metadata, and completion. `struct spi_mpc8xxx_cs` stores per-device buffer callbacks, shifts, and cached hardware mode. `struct mpc8xxx_spi_probe_info` wraps platform data and optional IMMR SPI CS mapping. It also defines big-endian register read/write helpers and prototypes for shared exports.

## Control Flow
The header has no independent runtime flow. Its inline `mpc8xxx_spi_write_reg()` and `mpc8xxx_spi_read_reg()` enforce big-endian MMIO access for classic Freescale registers.

## State And Persistence
It declares all runtime state used by the classic Freescale SPI path. The state is volatile and owned by the SPI controller/device lifecycle.

## Dependencies And Integration Points
Includes `asm/io.h` and uses `struct fsl_spi_platform_data` from Freescale platform headers through included compilation context. Included by `spi-fsl-lib.c`, `spi-fsl-cpm.c`, `spi-fsl-cpm.h`, and `spi-fsl-spi.c`.

## Risks
This header is a private ABI shared by several files. Structure-field changes can break CPM and CPU transfer paths. Conditional fields under `CONFIG_SPI_FSL_SPI` mean build coverage across configurations is important.

## Test Signals
Build tests for all relevant Kconfig combinations, big-endian register access, per-CS state allocation/cleanup, and CPU vs CPM transfer paths are the main signals.
