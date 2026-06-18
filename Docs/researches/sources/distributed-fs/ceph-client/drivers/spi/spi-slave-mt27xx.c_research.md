# sources/distributed-fs/ceph-client/drivers/spi/spi-slave-mt27xx.c

## Purpose

`spi-slave-mt27xx.c` implements a MediaTek SPI target controller for MT2712 and MT8195-class hardware. It registers a target-mode SPI controller, supports FIFO and DMA transfers, configures CPOL/CPHA and bit order, and exposes `target_abort` for upper-layer target handlers that need to cancel a pending transaction.

## Important APIs, Types, and Functions

`struct mtk_spi_slave` stores the device, MMIO base, SPI clock, completion, current transfer pointer, abort flag, and compatible-specific limits. `struct mtk_spi_compatible` describes FIFO size and whether RX is mandatory; MT2712 has a 512-byte FIFO and MT8195 has a 128-byte FIFO with `SPI_CONTROLLER_MUST_RX`.

Core hooks are `mtk_spi_slave_prepare_message()`, `mtk_spi_slave_transfer_one()`, `mtk_spi_slave_setup()`, and `mtk_target_abort()`. FIFO and DMA paths are split into `mtk_spi_slave_fifo_transfer()` and `mtk_spi_slave_dma_transfer()`. `mtk_spi_slave_interrupt()` acknowledges hardware status, copies FIFO RX data, unmaps DMA buffers on DMA completion, disables transfer/DMA state, and completes the waiter. Probe allocates a target controller with `spi_alloc_target()`, maps resources, requests IRQ, enables the clock for registration, sets runtime PM, and registers the controller.

## Control Flow

Message preparation writes polarity, phase, MSB/LSB order, and endian bits into `SPIS_CFG_REG`. A transfer reinitializes completion, clears abort state, records the current transfer, and chooses DMA when length exceeds the compatible FIFO size. FIFO mode resets hardware, enables TX/RX according to buffers, preloads TX FIFO in 32-bit words plus remainder, then waits for an IRQ. DMA mode maps TX and/or RX buffers, writes DMA addresses, enables DMA-address mode, enables TX/RX, writes transfer length, starts DMA, then waits for completion. The interrupt path distinguishes DMA and FIFO completion based on `DMA_DONE_ST` plus `DATA_DONE_ST`/`RSTA_DONE_ST`.

## State and Persistence Behavior

Persistent kernel state is per-controller only: current transfer pointer, clock state, compatible data, and completion/abort flags. No filesystem persistence exists. Hardware register state is reset at the start and end of transfers. Runtime/system PM gates the SPI clock while the controller is idle or suspended.

## Dependencies and Integration Points

The driver depends on platform resources, OF compatible data, MMIO, IRQs, completions, DMA mapping, clocks, runtime PM, and the SPI target controller API. Target handlers such as `spi-slave-time` and `spi-slave-system-control` can run on top of this controller.

## Risks and Edge Cases

The DMA path writes `xfer->tx_dma` and `xfer->rx_dma` registers even when the corresponding buffer is absent; those fields must be harmless or preinitialized by SPI core. Successful DMA completion relies on the IRQ handler to unmap buffers and disable DMA, while error paths clean up locally. `mtk_spi_slave_wait_for_completion()` has no timeout, so a missing host transaction or lost interrupt can block indefinitely unless `target_abort` is invoked. `CMD_INVALID_ST` returns `IRQ_NONE` after warning, which may confuse shared IRQ diagnostics while leaving the current transfer uncleared on that path.

## Test Signals

Exercise FIFO and DMA thresholds for both compatibles, TX-only, RX-only, full duplex, non-4-byte remainders, MT8195 mandatory RX behavior, target abort while waiting, command-invalid interrupts, reset-done interrupts, runtime suspend/resume, system suspend/resume, and DMA mapping failures for each direction. IRQ-driven cleanup should be checked for double-unmap and missing-unmap cases.
