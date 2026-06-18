# sources/distributed-fs/ceph-client/drivers/spi/spi-sunplus-sp7021.c

## Purpose
`spi-sunplus-sp7021.c` implements the Sunplus SP7021 SPI controller driver. It can register either a host controller or a target controller depending on the `spi-slave` device property. Host mode uses register/FIFO driven full-duplex transfers split into hardware-sized chunks. Target mode uses the controller's slave DMA registers with manually mapped DMA buffers.

## Important APIs, Types, And Functions
`struct sp7021_spi_ctlr` stores master/slave MMIO windows, IRQ numbers, clock/reset handles, transfer completions, a buffer mutex, mode, active buffer pointers, and progress counters. Host-mode SPI hooks include `sp7021_spi_controller_prepare_message()` and `sp7021_spi_host_transfer_one()`. Target-mode hooks are `sp7021_spi_target_transfer_one()` and `sp7021_spi_target_abort()`. IRQ handlers are split into `sp7021_spi_host_irq()` and `sp7021_spi_target_irq()`. `sp7021_spi_controller_probe()` selects host versus target allocation with `devm_spi_alloc_host()` or `devm_spi_alloc_target()`.

## Control Flow
Probe reads the OF alias for the bus number, selects mode, initializes SPI controller capabilities, maps `master` and `slave` resources, obtains `master_risc` and `slave_risc` IRQs, enables the clock, deasserts reset, installs a reset cleanup action, requests both IRQs, enables runtime PM, and registers the controller. Host transfers are split into chunks of at most `SP7021_SPI_DATA_SIZE` bytes. For each chunk the driver locks `buf_lock`, resets counters, programs the clock divider, primes up to the FIFO unit, enables FIFO/full/finish interrupts, writes transfer lengths and start bit, waits up to one second, clears finish flags, restores CPOL-sensitive config, and unlocks.

The host IRQ reads status counts, drains RX, fills TX, then, once finish or all TX bytes are observed, spins until the expected RX count is drained, clears the master interrupt and finish flag, and completes `isr_done`. Target TX/RX map a single DMA buffer, program slave DMA control/length/address registers, wait for completion, and unmap. Target IRQ acknowledges `DATA_RDY` and completes `target_isr`; target abort completes both target and host completions.

## State And Persistence
Transfer state is in `tx_cur_len`, `rx_cur_len`, `data_unit`, `tx_buf`, `rx_buf`, `xfer_conf`, and completions. Host operations are serialized by `buf_lock`. Runtime and system suspend assert reset; resume deasserts reset and prepares the clock in system resume. No persistent state is stored outside hardware registers and driver memory.

## Dependencies And Integration Points
The driver uses the SPI core, platform resources by name, OF properties, clk/reset APIs, runtime PM, IRQs, and streaming DMA mapping for target mode. Host mode advertises `SPI_CONTROLLER_MUST_RX | SPI_CONTROLLER_MUST_TX`, 8-bit words, GPIO descriptors, 40 kHz to 25 MHz speed, and SPI CPOL/CPHA/CS_HIGH/LSB_FIRST modes. Target mode advertises half-duplex behavior and a target abort callback.

## Risks
Host transfer code assumes both `tx_buf` and `rx_buf` are valid because of the MUST_TX/MUST_RX flags; unusual SPI core behavior around dummy buffers should be watched. The IRQ drains RX in a polling loop until `total_len == rx_cur_len`, which can stall if hardware status stops updating. Target mode manually maps buffers and only supports TX-only or RX-only transfers. System resume calls `clk_prepare_enable()` even though probe used `devm_clk_get_enabled()`, so PM sequencing needs hardware testing. Reset on suspend drops register state.

## Test Signals
Exercise both host and target DT configurations. Host tests should include lengths around 16-byte FIFO units, 255-byte chunk boundaries, CPOL/CPHA/CS_HIGH/LSB modes, timeout paths, and concurrent message serialization. Target tests should verify DMA TX/RX completion, abort behavior, and slave interrupt acknowledgment. Runtime PM and system suspend/resume should be tested because reset is the primary state transition.
