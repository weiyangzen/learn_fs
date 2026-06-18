# sources/distributed-fs/ceph-client/drivers/spi/spi-tegra20-sflash.c

## Purpose
`spi-tegra20-sflash.c` is the SPI host driver for NVIDIA Tegra20's serial flash controller. It is a legacy, small-FIFO controller driver that uses interrupt-driven CPU/PIO transfers rather than DMA and is tailored to the serial flash block's four-word FIFO.

## Important APIs, Types, And Functions
The main state is `struct tegra_sflash_data`, which stores controller/device handles, spinlock, clock/reset/MMIO/IRQ, cached speed, current SPI device and transfer progress, direction flags, FIFO/status shadows, command and DMA-control register shadows, completion, and the current `spi_transfer`. SPI integration uses `tegra_sflash_transfer_one_message()` as the message engine. Transfer helpers include `tegra_sflash_calculate_curr_xfer_param()`, `tegra_sflash_fill_tx_fifo_from_client_txbuf()`, `tegra_sflash_read_rx_fifo_to_client_rxbuf()`, `tegra_sflash_start_cpu_based_transfer()`, and `tegra_sflash_start_transfer_one()`.

## Control Flow
Probe allocates a SPI controller, sets CPOL/CPHA mode support and four chip selects, maps registers, requests the IRQ, obtains the clock and reset, enables runtime PM, resets the controller, writes a default master/software-CS command register, and registers the controller. A message is processed transfer by transfer: setup changes the clock if needed, initializes progress counters, programs first-transfer mode/CS/bit length or later-transfer bit length, sets TX/RX direction, writes the command register, and starts a CPU transfer. CPU transfer enables TX/RX completion interrupts, optionally primes TX FIFO, sets block count, enables DMA-control start semantics, and waits on completion.

The ISR samples status, records TX overflow or RX underflow depending on direction, clears status, and calls `handle_cpu_based_xfer()`. That handler resets the hardware on error or busy status, drains RX, updates current position, completes the transfer if done, or starts the next FIFO-sized chunk.

## State And Persistence
The driver maintains register shadows for the default and active command register plus DMA-control state. Per-transfer progress counters are reset for each transfer. Runtime PM only gates the clock after flushing writes with a readback. System resume writes the saved command register back before resuming the SPI controller. No persistent storage is used.

## Dependencies And Integration Points
It depends on SPI core message APIs, platform resources, OF match `nvidia,tegra20-sflash`, clk/reset, runtime PM, IRQ handling, and MMIO. Unlike newer Tegra SPI drivers, it does not use DMAengine and does not support advanced mode bits beyond CPOL/CPHA.

## Risks
Only four FIFO words are handled per chunk, so performance is limited and interrupt sequencing is critical. The error path resets the controller inside interrupt handling, which should be checked for hardware recovery side effects. The file defines `SPI_FIFO_EMPTY` using `SPI_TX_EMPTY`/`SPI_RX_EMPTY` names that are not otherwise visible in this file, so this source may depend on historical macros or contain dead/buggy macro text in this snapshot. CS behavior is simple and may not cover complex multi-transfer devices as robustly as newer controllers.

## Test Signals
Test serial-flash style 8-bit transfers, RX-only and TX-only behavior, lengths spanning more than four FIFO words, CPOL/CPHA combinations, timeout path, FIFO error path, reset recovery, runtime suspend/resume, and system suspend/resume. Transfer timeout warnings and `CpuXfer ERROR` logs are important diagnostics.
