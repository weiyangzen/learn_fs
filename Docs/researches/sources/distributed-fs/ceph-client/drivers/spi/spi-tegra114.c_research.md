# sources/distributed-fs/ceph-client/drivers/spi/spi-tegra114.c

## Purpose
`spi-tegra114.c` implements the NVIDIA Tegra114/Tegra124/Tegra210 SPI controller driver. It supports native and GPIO chip select handling, 4-32 bits per word, LSB first, 3-wire, dual TX/RX, hardware CS timing, per-device tap delays, PIO transfers for FIFO-sized chunks, and DMA transfers through coherent bounce buffers for larger chunks.

## Important APIs, Types, And Functions
`struct tegra_spi_data` is the main controller state: device/controller handles, spinlock, clock/reset/MMIO/IRQ, cached speed, current transfer progress, DMA buffers/channels/descriptors, completion objects, register shadows, CS timing registers, and SoC data. `struct tegra_spi_soc_data` controls whether an interrupt-mask register exists; `struct tegra_spi_client_data` stores optional per-device TX/RX tap delays.

Core functions include `tegra_spi_probe()`, `tegra_spi_remove()`, `tegra_spi_setup()`, `tegra_spi_cleanup()`, `tegra_spi_set_hw_cs_timing()`, `tegra_spi_transfer_one_message()`, `tegra_spi_setup_transfer_one()`, and `tegra_spi_start_transfer_one()`. Data movement is split between FIFO helpers (`tegra_spi_fill_tx_fifo_from_client_txbuf()`, `tegra_spi_read_rx_fifo_to_client_rxbuf()`) and DMA helpers (`tegra_spi_copy_client_txbuf_to_spi_txbuf()`, `tegra_spi_copy_spi_rxbuf_to_client_rxbuf()`, `tegra_spi_start_tx_dma()`, `tegra_spi_start_rx_dma()`).

## Control Flow
Probe allocates the controller, reads `spi-max-frequency`, configures SPI core capabilities, maps registers, gets IRQ/clock/reset, allocates RX and TX DMA channels and coherent buffers, enables runtime PM, resets hardware, initializes default command and timing shadows, requests a threaded IRQ, and registers the controller. Device setup parses optional `nvidia,tx-clk-tap-delay` and `nvidia,rx-clk-tap-delay`, unmasks interrupt registers on SoCs that need it, configures CS polarity, and leaves default command state in hardware.

Message transfer iterates each `spi_transfer`. For the first transfer it clears status, programs mode, bit order, 3-wire, CS selection, GPIO CS, HW/SW CS mode, and tap delays. Each transfer computes packing and chunk size, programs TX/RX enable bits and chip select, flushes FIFOs, then chooses DMA when the chunk exceeds the 64-word FIFO and DMA buffers are available, otherwise PIO. Completion is driven by the threaded IRQ. CPU handling drains/fills FIFO and starts the next chunk until the transfer length is consumed. DMA handling waits for DMA completion callbacks, copies bounce-buffer data when needed, then starts the next chunk or completes. Timeouts terminate DMA, dump registers, flush FIFOs, reset the controller, and invalidate last CS cache.

## State And Persistence
The driver caches register values in `def_command1_reg`, `def_command2_reg`, `command1_reg`, `dma_control_reg`, `spi_cs_timing1`, and `spi_cs_timing2`. Runtime transfer progress uses `cur_pos`, `cur_rx_pos`, `cur_tx_pos`, `curr_dma_words`, `cur_direction`, and `curr_xfer`. Per-device tap-delay data is allocated in setup and freed in cleanup. Suspend/resume restores command registers and resets last-used CS tracking; runtime PM gates only the SPI clock. There is no durable state outside the device and driver memory.

## Dependencies And Integration Points
The driver integrates with the SPI core, OF platform matching, clk/reset, runtime PM, threaded IRQs, DMAengine, GPIO descriptors, and device-tree child properties. Compatible strings cover `nvidia,tegra114-spi`, `nvidia,tegra124-spi`, and `nvidia,tegra210-spi`. It exposes `transfer_one_message` instead of `transfer_one` so it can manage CS transitions across multi-transfer messages.

## Risks
PIO/DMA chunking relies on accurate packed/unpacked byte accounting for unusual bits-per-word values. DMA uses coherent bounce buffers and per-chunk copies, so cache sync and length rounding are sensitive. The timeout path resets hardware and invalidates CS state, but failed transfers may leave attached devices mid-command. CS behavior is complex because GPIO CS, hardware CS for single transfers, software CS, `cs_change`, and delays interact. Hardware CS timing rejects non-SCK delay units and clamps values. `SPI_INTR_MASK` behavior differs by SoC data, making match data important.

## Test Signals
High-value tests include all supported word sizes, packed and unpacked lengths, FIFO-boundary and DMA-boundary transfers, dual transfers, 3-wire mode, GPIO CS versus native CS, `cs_change` and delay behavior, per-device tap delays, hardware CS setup/hold/inactive timing, timeout/error injection, runtime PM autosuspend, and suspend/resume register restore. Debug dumps from `tegra_spi_dump_regs()` and FIFO error bits are key diagnostic signals.
