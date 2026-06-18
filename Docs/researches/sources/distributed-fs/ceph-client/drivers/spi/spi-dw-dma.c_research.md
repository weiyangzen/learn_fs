# sources/distributed-fs/ceph-client/drivers/spi/spi-dw-dma.c

## Purpose
Implements the DMA backend for the Synopsys DesignWare SPI core. It plugs into `struct dw_spi_dma_ops` so the shared DW SPI core can initialize DMA channels, decide whether a transfer is DMA-capable, set up controller DMA registers, execute transfers, and stop or release DMA resources. It has two channel-acquisition paths: Intel Medfield-specific PCI DMA discovery and generic named `rx`/`tx` DMA channels.

## Important APIs, Types, And Functions
Key entry points are `dw_spi_dma_setup_mfld()` and `dw_spi_dma_setup_generic()`, both exported in namespace `SPI_DW_CORE`. They install either `dw_spi_dma_mfld_ops` or `dw_spi_dma_generic_ops` into `dws->dma_ops`. Initialization flows through `dw_spi_dma_init_mfld()` or `dw_spi_dma_init_generic()`, then `dw_spi_dma_caps_init()` and `dw_spi_dma_maxburst_init()`. Transfer work is split across `dw_spi_dma_setup()`, `dw_spi_dma_transfer()`, `dw_spi_dma_transfer_all()`, and `dw_spi_dma_transfer_one()`. Completion is driven by DMA callbacks `dw_spi_dma_tx_done()` and `dw_spi_dma_rx_done()` plus the DW interrupt handler callback `dw_spi_dma_transfer_handler()`.

## Control Flow
After channel allocation, the driver records channels in both `struct dw_spi` and the SPI controller. A transfer is eligible only when its length exceeds FIFO depth and the current word width is supported by DMA address-width capabilities. Setup configures slave directions, bus widths, DMA thresholds, `DW_SPI_DMACR`, interrupt masks, and the DW core transfer handler. Normal transfers submit TX and optional RX scatterlists once, starting RX before TX. If the DMA engine cannot safely traverse large SG lists in hardware, `dw_spi_dma_transfer_one()` virtually splits TX/RX SGs into matched one-entry chunks to avoid RX FIFO overflow.

## State And Persistence
State is runtime-only in `struct dw_spi`: channel pointers, burst levels, SG burst limit, supported address widths, `dma_chan_busy` bits, DMA completion, and the data-register DMA address. No persistent storage is used. Cleanup terminates live channels and releases them; `dw_spi_dma_stop()` terminates only channels whose busy bits remain set.

## Dependencies And Integration Points
Depends on Linux DMAengine, DMA mapping/scatterlist infrastructure, PCI lookup for Medfield, and the DW SPI register helpers from `spi-dw.h`. It integrates with the shared DW core via `dws->dma_ops`, `dws->transfer_handler`, and SPI controller `can_dma`, `dma_rx`, and `dma_tx` fields.

## Risks
The main risk is synchronization between TX and RX DMA. The code explicitly starts RX first, limits TX bursts, waits for residual FIFO drain, and chunks SG lists when SG hardware traversal may race. Timeout estimates depend on effective bus speed, so wrong speed metadata can cause false timeouts or long waits. TX-only DMA requires a TX buffer; `dw_spi_dma_setup()` rejects missing `tx_buf`.

## Test Signals
Useful tests include long full-duplex SG transfers with mismatched SG boundaries, TX-only transfers, FIFO-sized transfers that must stay PIO, DMA timeout injection, unsupported word-width fallback, suspend/remove during DMA, and Medfield/generic channel allocation failure paths.
