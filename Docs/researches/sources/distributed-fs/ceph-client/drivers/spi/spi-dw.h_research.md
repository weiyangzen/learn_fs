# sources/distributed-fs/ceph-client/drivers/spi/spi-dw.h

## Purpose
Defines the shared private interface for the DesignWare SPI driver family. It centralizes register offsets, bitfields, capability flags, transfer/DMA state structures, register access helpers, chip reset/shutdown helpers, and core function declarations consumed by MMIO, PCI, DMA, and the DW core implementation.

## Important APIs, Types, And Functions
Important types are `struct dw_spi_cfg`, `struct dw_spi_dma_ops`, and `struct dw_spi`. The header defines virtual IP IDs for PSSI/HSSI, version comparison macros, capability flags `DW_SPI_CAP_CS_OVERRIDE` and `DW_SPI_CAP_DFS32`, register offsets from `DW_SPI_CTRLR0` through `DW_SPI_CS_OVERRIDE`, CTRLR0/TMOD/SR/interrupt/DMACR bitfields, and mem-op buffer sizing helpers. Inline APIs include `dw_readl()`, `dw_writel()`, `dw_read_io_reg()`, `dw_write_io_reg()`, `dw_spi_enable_chip()`, `dw_spi_set_clk()`, `dw_spi_mask_intr()`, `dw_spi_umask_intr()`, `dw_spi_reset_chip()`, and `dw_spi_shutdown_chip()`.

## Control Flow
The header itself has no runtime control flow, but its helpers define common sequences: mask/unmask interrupt bits by read-modify-write of `IMR`, reset by disabling the engine, masking interrupts, clearing interrupt status, deselecting CS, and re-enabling, and shutdown by disabling the engine and baud clock. DMA setup declarations become no-ops when `CONFIG_SPI_DW_DMA` is disabled.

## State And Persistence
`struct dw_spi` is the central runtime state: controller pointer, IP/version/capabilities, register base and physical address, IRQ, FIFO/depth/frequency metadata, chip-select callback, current transfer pointers and lengths, memory-op buffer, word width, handler pointer, sample delay state, mem ops, DMA channels and completion, and optional debugfs data. All state is volatile kernel driver state.

## Dependencies And Integration Points
Depends on kernel bitfield/io/scatterlist/debugfs/SPI MEM headers. It is included by DesignWare platform, PCI, DMA, and core files. Exported declarations are implemented by the shared core and used by bus glue modules under namespace `SPI_DW_CORE`.

## Risks
The header is a cross-module ABI inside the driver family. Register offset or bitfield mistakes affect every DW backend. `__raw_readl()`/`__raw_writel()` helpers assume the DW register endianness/ordering expected by the supported platforms, while data-register access can vary by `reg_io_width`.

## Test Signals
Compile coverage with and without `CONFIG_SPI_DW_DMA`, PSSI/HSSI variant detection, register-width access tests, reset/shutdown behavior, interrupt masking, DMA ops linkage, and SPI MEM buffer boundary tests are useful signals.
