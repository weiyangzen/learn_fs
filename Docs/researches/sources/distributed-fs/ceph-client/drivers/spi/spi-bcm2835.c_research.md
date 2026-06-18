# sources/distributed-fs/ceph-client/drivers/spi/spi-bcm2835.c

## Purpose
Implements the primary Broadcom BCM2835 SPI controller driver used on Raspberry Pi-class SoCs. It supports polling, interrupt, and DMA transfer modes, software/GPIO chip select handling, debugfs counters, runtime setup per SPI device, and platform registration for `brcm,bcm2835-spi`.

## Important APIs, Types, And Functions
`struct bcm2835_spi` holds controller resources, transfer pointers/counters, DMA prologue bookkeeping, debugfs counters, current target state, DMA activity flags, and reusable DMA descriptors. `struct bcm2835_spidev` holds per-device precomputed CS register values plus a reusable RX-DMA descriptor used to clear RX FIFO during TX-only DMA transfers. Transfer helpers include FIFO byte and 32-bit count routines, `bcm2835_spi_reset_hw()`, IRQ handler `bcm2835_spi_interrupt()`, polling/IRQ/DMA transfer functions, DMA callbacks, DMA setup/release, `bcm2835_spi_setup()`, and `bcm2835_spi_prepare_message()`.

## Control Flow
Probe allocates a host, configures SPI core callbacks and limits, maps registers, enables the core clock, initializes optional DMA, clears FIFOs, requests a shared IRQ, registers the controller, and creates debugfs counters. For each device, setup allocates per-target state, prepares reusable DMA descriptors when DMA is available, precomputes CS register values, and handles native-CS-to-GPIO fallback for legacy device-tree users. During a transfer, the driver computes the clock divider, sets 3-wire receive mode if needed, stores TX/RX pointers and lengths, then chooses polling for short transfers, DMA for large DMA-capable transfers, or IRQ otherwise. Polling loops fill/read FIFOs until complete or falls back to IRQ after a module-parameter-controlled time limit. IRQ mode fills TX FIFO, enables interrupts, drains RX FIFO on RX threshold/full events, refills TX on DONE, and finalizes when all RX bytes arrive. DMA mode may transmit a CPU prologue to align sglist entries, starts TX DMA early, starts RX DMA late, and finalizes in RX or TX callbacks depending on transfer direction.

## State And Persistence
Persistent state includes MMIO base, clock handle/rate, IRQ, debugfs counters, DMA channels/descriptors, and per-device CS/DMA state. Mutable transfer state includes `tx_buf`, `rx_buf`, `tx_len`, `rx_len`, active `tfr`, prologue byte counts, spillover flag, current target pointer, and DMA active flags. The driver mutates mapped scatterlist DMA addresses/lengths during the DMA prologue and restores them with `bcm2835_spi_undo_prologue()` before completion/error handling. Debugfs counters persist until driver removal and provide runtime mode-use observability.

## Dependencies And Integration Points
The driver depends on Linux SPI, DMAengine, DMA mapping, OF address lookup, GPIO descriptors and lookup tables, debugfs, interrupts, clocks, and platform resources. It advertises `SPI_CPOL`, `SPI_CPHA`, `SPI_CS_HIGH`, `SPI_NO_CS`, and `SPI_3WIRE`, and only supports 8-bit words. Device-tree matching is `brcm,bcm2835-spi`.

## Risks And Edge Cases
DMA handling is the highest-risk area: FIFO access width changes with DMA enable, sglist prologue mutation must be reversed exactly, and TX-only/RX-only transfers use cyclic descriptors with race handling between TX and RX callbacks. Hardware quirks require writing the DONE bit and clearing FIFOs; missing reset paths can leave the controller wedged. Native chip-select support is intentionally redirected to GPIO for documented lines and has legacy lookup-table complexity. Polling timeout heuristics depend on estimated byte time and can affect latency. The maximum DMA transfer size is capped at 65532 bytes because of the 16-bit DLEN register.

## Test Signals
Test short transfers that stay in polling mode, longer IRQ transfers, DMA transfers above 96 bytes, TX-only/RX-only/full-duplex DMA, vmalloc-backed buffers with non-4-byte first sg entries, 3-wire reads, CS GPIO fallback, mode changes before chip-select assertion, error cancellation, and remove/shutdown reset. Debugfs counters should reflect transfer lane selection. DMA mapping or prologue bugs usually show as shifted data, corrupted first bytes, DMA residue warnings, or stuck transfer finalization.
