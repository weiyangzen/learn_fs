# sources/distributed-fs/ceph-client/drivers/spi/spi-tegra20-slink.c

## Purpose
`spi-tegra20-slink.c` implements the Tegra20/Tegra30 SLINK SPI controller driver. It supports CPOL/CPHA/CS_HIGH, native chip selects, packed 8/16-bit transfers, CPU FIFO transfers, DMA transfers through coherent bounce buffers, and Tegra30-specific CS hold-time capability.

## Important APIs, Types, And Functions
`struct tegra_slink_data` stores the SPI controller, SoC chip data, clock/reset/MMIO/IRQ, DMA channels and buffers, completions, active transfer progress, packed-transfer state, register shadows, and status fields. `struct tegra_slink_chip_data` exposes the `cs_hold_time` capability. SPI callbacks are `tegra_slink_setup()`, `tegra_slink_prepare_message()`, `tegra_slink_transfer_one()`, and `tegra_slink_unprepare_message()`.

Data movement is handled by FIFO helpers (`tegra_slink_fill_tx_fifo_from_client_txbuf()`, `tegra_slink_read_rx_fifo_to_client_rxbuf()`), DMA bounce-buffer helpers (`tegra_slink_copy_client_txbuf_to_spi_txbuf()`, `tegra_slink_copy_spi_rxbuf_to_client_rxbuf()`), and DMA start/completion helpers. IRQ handling uses a hard IRQ `tegra_slink_isr()` to snapshot status and wake `tegra_slink_isr_thread()` for CPU or DMA continuation.

## Control Flow
Probe allocates a devm SPI host, reads max speed, maps registers and physical address, obtains clock/reset, initializes Tegra OPP data, allocates RX/TX DMA channels and coherent buffers, enables runtime PM, resets hardware, requests a threaded IRQ, initializes default command registers, and registers the controller. Setup updates CS polarity in the default command register under the spinlock. `prepare_message()` clears status, sets software CS active state, selects the message chip select in command2, and programs CPOL/CPHA idle behavior.

Each transfer sets clock rate through OPP, resets progress counters, computes packed/unpacked transfer parameters, programs bit length and TX/RX enable bits, writes command2 before command to avoid a chip-select spike, and chooses DMA for more than 32 FIFO words. CPU mode primes FIFO and uses completion interrupts. DMA mode copies to/from coherent buffers for unpacked mode, starts DMA descriptors, enables packed mode when needed, then enables controller DMA. The threaded IRQ waits for DMA completions, copies RX results, advances progress, and starts more chunks until done.

## State And Persistence
Register state is shadowed in `command_reg`, `command2_reg`, `dma_control_reg`, `def_command_reg`, and `def_command2_reg`. Transfer state is per-message and protected by `lock` in IRQ continuation. Runtime PM gates the clock after a readback flush. System resume restores command registers before resuming the SPI controller. DMA buffers persist for the lifetime of the device and are freed on remove.

## Dependencies And Integration Points
Dependencies include SPI core, OF matching for `nvidia,tegra20-slink` and `nvidia,tegra30-slink`, clk/reset, Tegra OPP helpers, runtime PM, IRQ threading, DMAengine, coherent DMA allocation, and MMIO. The controller advertises four native chip selects and message-level callbacks.

## Risks
Packed/unpacked byte accounting and DMA length rounding are central correctness risks. DMA setup is mandatory in probe; if either channel fails, probe fails rather than falling back to PIO. Error handling in DMA path appears to assert reset twice without deasserting in one branch, which is a suspicious recovery path requiring hardware validation. The controller write helper readbacks most registers, so ordering assumptions are explicit but performance-sensitive. CS spike avoidance depends on command2-before-command ordering.

## Test Signals
Test Tegra20 and Tegra30 compatibles, 8/16-bit packed transfers, non-packed word sizes, FIFO-size and DMA-size boundaries, TX-only/RX-only/full-duplex-like SPI core messages, CS_HIGH and `cs_change`, OPP/clock rate changes, DMA timeout/error injection, and suspend/resume. Watch `CpuXfer`/`DmaXfer` error logs, FIFO status bits, and DMA completion timeouts.
