# sources/distributed-fs/ceph-client/drivers/spi/spi-axiado.h

## Purpose
Defines the Axiado SPI host controller register map, bit fields, fixed limits, default values, and private driver state consumed by `spi-axiado.c`. It is not a public subsystem API; it is the hardware contract for the Axiado SPI driver.

## Important APIs, Types, And Functions
The central type is `struct ax_spi`, containing MMIO base, clock handles, cached speeds, transfer buffer pointers, byte counters, FIFO depth, RX word-unpacking state, and RX copy/discard counters. Register offsets cover control registers `AX_SPI_CR1` through `AX_SPI_CR3`, FIFO count registers, clock divider register `AX_SPI_SCDR`, interrupt mask/status/vector registers, and TX/RX FIFO addresses. Bit definitions include controller enable/reset, CPHA/CPOL, read/write enable, read-ignore, host transmit enable, interrupt bits, FIFO threshold values, target-select values, and limits such as `AX_SPI_COMMAND_BUFFER_SIZE`, `AX_SPI_RX_FIFO_DRAIN_LIMIT`, and `AX_SPI_TRX_FIFO_TIMEOUT`.

## Control Flow
This header has no executable control flow, but it shapes driver flow by naming which register bits are written during initialization, transfer setup, interrupt handling, FIFO draining, and `spi-mem` operation sizing. The interrupt constants map directly to the ISR/IMR/IVR logic in `spi-axiado.c`; FIFO and timeout constants bound polling and drain loops.

## State And Persistence
`struct ax_spi` is allocated as SPI controller private data and persists for the lifetime of the platform device. The header distinguishes persistent hardware resources (`regs`, `ref_clk`, `pclk`, `clk_rate`, `tx_fifo_depth`) from per-transfer mutable state (`tx_buf`, `rx_buf`, byte counters, RX staging words). Separate RX staging fields exist for interrupt-driven and polled `spi-mem` contexts.

## Dependencies And Integration Points
The header assumes Linux kernel integer types, `__iomem`, and `struct clk` declarations included by the C file. Its values integrate tightly with Axiado Digital Blocks SPI IP, the Linux SPI controller callbacks, and SPI memory operations.

## Risks And Edge Cases
Several constants are fixed policy rather than discovered hardware state: `FIFO_DEPTH` is hard-coded to 256, threshold values are fixed, and divider min/default/max naming is potentially confusing. If silicon revisions differ, these definitions can silently misconfigure transfers. The target-select values and mask only cover four chip selects. The drain limit of 24 32-bit FIFO reads may be insufficient if stale FIFO state exceeds that amount.

## Test Signals
Header-level validation is indirect: successful driver probe, correct FIFO thresholds, correct interrupt bit clearing, and expected transfer behavior across all supported chip selects indicate that the register definitions match hardware. Static review should verify each field in `struct ax_spi` remains synchronized with the C driver’s documented usage.
