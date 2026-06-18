<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-uniphier.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-uniphier.c

## Purpose

`spi-uniphier.c` is a platform SPI controller driver for Socionext UniPhier SCSSI hardware. It registers a single-chip-select SPI host that can execute transfers by polling, interrupt completion, or DMA depending on transfer size and available DMA channels.

The driver programs SSI clock/frame/data-size registers per transfer, supports SPI modes 0-3, `SPI_CS_HIGH`, `SPI_LSB_FIRST`, word sizes from 1 to 32 bits, and full-duplex semantics forced by `SPI_CONTROLLER_MUST_RX | SPI_CONTROLLER_MUST_TX`.

## Important APIs, Types, and Functions

`struct uniphier_spi_priv` contains MMIO base, physical base for DMA slave addresses, clock, controller pointer, completion, error status, TX/RX byte counters, user buffer pointers, DMA busy bitmask, and cached mode/word/speed parameters.

Register definitions cover SSI control, clock settings, TX/RX word-size registers, frame polarity/start, status, interrupt enable/status/clear, FIFO control, and shared TX/RX data register. `bytes_per_word()` maps bit width to 1, 2, or 4 bytes.

Configuration helpers are `uniphier_spi_set_mode()`, `uniphier_spi_set_transfer_size()`, `uniphier_spi_set_baudrate()`, and `uniphier_spi_setup_transfer()`. FIFO helpers are `uniphier_spi_send()`, `uniphier_spi_recv()`, `uniphier_spi_set_fifo_threshold()`, and `uniphier_spi_fill_tx_fifo()`.

Transfer paths are `uniphier_spi_transfer_one_poll()`, `uniphier_spi_transfer_one_irq()`, and `uniphier_spi_transfer_one_dma()`, selected by `uniphier_spi_transfer_one()`. DMA support is advertised by `uniphier_spi_can_dma()` and completed by `uniphier_spi_dma_rxcb()` / `uniphier_spi_dma_txcb()`. Error and hardware lifecycle hooks are `uniphier_spi_handle_err()`, `uniphier_spi_prepare_transfer_hardware()`, and `uniphier_spi_unprepare_transfer_hardware()`.

`uniphier_spi_probe()` maps resources, enables the clock, requests IRQ, optionally obtains DMA channels, fills controller callbacks, and registers the controller.

## Control Flow

Probe allocates a SPI host, maps one MMIO resource, records its physical address for DMA, enables the clock, requests the platform IRQ, initializes completion, computes min/max speed from the clock divider limits, requests optional `"tx"` and `"rx"` DMA channels, sets `max_dma_len` from DMA burst caps, and registers the controller.

For each transfer, `uniphier_spi_transfer_one()` ignores zero-length transfers, calls `uniphier_spi_setup_transfer()` to cache buffers and counters, reprograms mode/size/speed only when the cached value changed, and resets FIFOs. If DMA is usable and the transfer exceeds FIFO depth in words, the DMA path is used. Otherwise, the function estimates whether the transfer fits within `SSI_POLL_TIMEOUT_US`; short transfers use polling and longer ones use IRQ completion.

Polling repeatedly fills the TX FIFO and drains RX as words become readable. If the polling loop cannot observe RX readiness within the microsecond budget, it falls back to the IRQ path. The IRQ path fills the initial FIFO, enables receive-complete and overrun interrupts, waits for completion, disables interrupts, and returns the collected error.

DMA configures FIFO burst threshold, programs DMA slave configs to SSI TX/RX data register addresses, prepares RX and TX scatter-gather descriptors only for buffers present in the transfer, enables DMA request interrupts, marks busy bits atomically, submits descriptors, and returns nonzero to tell the SPI core that completion is asynchronous. Each DMA callback clears its busy bit and finalizes the current transfer when the opposite direction has also completed.

The IRQ handler acknowledges all relevant interrupt causes, handles receive overrun as `-EIO`, drains RX FIFO on receive-complete status, validates FIFO/counter consistency, refills TX FIFO for the next chunk, and completes when all RX bytes are consumed.

## State and Persistence Behavior

There is no file-backed persistence. Persistent hardware state is limited to SSI registers while the controller is prepared. The driver caches the last configured `mode`, `bits_per_word`, and `speed_hz` to avoid redundant register writes between transfers.

Per-transfer state lives in `tx_bytes`, `rx_bytes`, `tx_buf`, `rx_buf`, `error`, and the `xfer_done` completion. DMA state is tracked with `dma_busy`, where TX and RX callbacks independently clear bits. On error, the driver disables the controller, flushes FIFOs, disables interrupts, and terminates active DMA channels.

## Dependencies and Integration Points

The driver depends on platform resources, device tree compatible `"socionext,uniphier-scssi"`, MMIO, clocks, IRQs, DMAengine, Linux completions, unaligned little-endian helpers, and the SPI controller API.

SPI integration uses `transfer_one`, `set_cs`, prepare/unprepare hardware hooks, `handle_err`, `can_dma`, `max_dma_len`, DMA channels attached to `host->dma_tx` / `host->dma_rx`, and `spi_finalize_current_transfer()` for asynchronous DMA.

## Risks and Edge Cases

`uniphier_spi_set_baudrate()` rounds the divider up to an even value but does not explicitly clamp to the documented 4..254 range before writing the masked low byte. The controller's min/max speed fields should keep callers inside range, but direct or malformed transfer speeds still deserve validation.

The cached-parameter logic sets `is_save_param = false` after reprogramming mode, then sets it true at the end. This works, but the unusual assignment makes future changes easy to misread.

DMA callbacks call `spi_finalize_current_transfer()` from DMA callback context after disabling request interrupts. Races between RX and TX callbacks are mediated by atomic bits; tests should cover TX-only, RX-only, and full-duplex DMA. Error cleanup uses `dmaengine_terminate_async()`, so completion ordering after an error path is worth stress testing.

The polling fallback reuses the same transfer state after a partial polling attempt. That is intentional: bytes already sent/received remain reflected in counters, and the IRQ path continues. Regression tests should ensure fallback does not duplicate or drop words.

## Test Signals

Useful tests include build coverage with DMA enabled/disabled, all SPI modes, `SPI_CS_HIGH`, `SPI_LSB_FIRST`, word sizes 1, 8, 16, 24, and 32, and transfers around the FIFO depth and polling threshold.

Runtime signals should cover polling completion, polling-to-IRQ fallback, IRQ overrun handling, DMA RX-only/TX-only/full-duplex, DMA channel absence, DMA `-EPROBE_DEFER`, suspend/error cleanup through `handle_err`, clock-rate derived speed limits, and removal after active DMA resources are allocated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-uniphier.c -->
