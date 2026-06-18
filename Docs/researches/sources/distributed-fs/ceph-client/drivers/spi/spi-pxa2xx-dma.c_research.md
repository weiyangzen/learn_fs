# sources/distributed-fs/ceph-client/drivers/spi/spi-pxa2xx-dma.c

## Purpose
`spi-pxa2xx-dma.c` provides DMA-engine support for the PXA2xx SSP SPI core. It prepares RX/TX DMA slave descriptors against the SSP data register, starts/stops paired DMA transfers, handles DMA completion versus FIFO-overrun races, and acquires/releases DMA channels for the shared core driver.

## Important APIs, Types, And Functions
- `pxa2xx_spi_dma_setup()` requests compatible TX/RX slave DMA channels using platform/glue-provided filter data.
- `pxa2xx_spi_dma_prepare()` prepares both TX and RX descriptors for a `spi_transfer`, registering the completion callback on RX.
- `pxa2xx_spi_dma_start()` issues pending RX then TX channels and marks `dma_running`.
- `pxa2xx_spi_dma_transfer()` is the IRQ-side DMA transfer handler used by the core to catch SSP FIFO overrun.
- `pxa2xx_spi_dma_transfer_complete()` serializes completion/error handling using `atomic_t dma_running`, clears interrupts/status, disables timeout on newer SSPs, sets message status on error, and finalizes the SPI transfer.
- `pxa2xx_spi_dma_stop()` terminates both DMA channels synchronously.
- `pxa2xx_spi_dma_release()` terminates and releases allocated DMA channels.

## Control Flow
The PXA2xx core calls `pxa2xx_spi_dma_setup()` during probe when platform data requests DMA. For each DMA-mapped transfer, the core sets `drv_data->transfer_handler` to `pxa2xx_spi_dma_transfer()`, calls `pxa2xx_spi_dma_prepare()`, clears SSP status, starts DMA, configures SSCR registers, and enables SSP service. RX completion calls `pxa2xx_spi_dma_callback()`, which delegates to `pxa2xx_spi_dma_transfer_complete(false)`. If the SSP IRQ reports RX overrun first, `pxa2xx_spi_dma_transfer()` terminates channels and completes with error.

## State And Persistence Behavior
The file relies on shared `struct driver_data` from `spi-pxa2xx.h`. DMA state is held in `controller->dma_tx`, `controller->dma_rx`, `xfer->tx_sg`, `xfer->rx_sg`, and `atomic_t dma_running`. It persists only for the controller lifetime. The atomic prevents double finalization when DMA completion and ROR IRQ arrive on different CPUs.

## Dependencies And Integration Points
This file is tightly coupled to `spi-pxa2xx.c` and `spi-pxa2xx.h`, the SPI core's DMA-mapped transfer helpers, DMA engine slave API, PXA SSP register helpers, and platform/PIC glue that supplies DMA filter parameters. It uses `DEFAULT_DMA_CR1`, `MAX_DMA_LEN`, `pxa25x_ssp_comp()`, `read_SSSR_bits()`, `write_SSSR_CS()`, and `clear_SSCR1_bits()` from the shared header.

## Risks
- Both RX and TX channels are mandatory; failure to request RX after TX unwinds TX, but no half-DMA mode exists.
- DMA descriptors are prepared separately; TX descriptor preparation failure after RX success terminates TX only because RX was not submitted yet.
- Error detection depends on SSP overrun status recheck at completion to cover races.
- Burst size and DMA filter correctness come entirely from platform/glue data.

## Test Signals
- DMA setup success and fallback when one channel is missing.
- RX/TX DMA transfers for 8/16/32-bit frames and multiple burst sizes.
- Concurrent DMA completion and FIFO-overrun IRQ races.
- Termination paths from SPI core error handling and controller remove.
- Scatterlist DMA-mapped transfers near `MAX_DMA_LEN`.
