# sources/distributed-fs/ceph-client/drivers/spi/spi-st-ssc4.c

## Purpose

`spi-st-ssc4.c` is a host-mode SPI driver for the STMicroelectronics SSC4 serial controller. It uses FIFO/interrupt-driven PIO, GPIO chip selects, runtime PM, and supports 8- and 16-bit transfers with CPOL/CPHA, LSB-first, loopback, and CS-high modes.

## Important APIs, Types, and Functions

`struct spi_st` stores MMIO base, SSC clock, device, current TX/RX pointers, bytes per word, remaining word count, current baud rate, and completion. `spi_st_setup()` configures baud rate, mode bits, data width, loopback, FIFO enable, and controller enable. `spi_st_transfer_one()` sets per-transfer pointers, chooses 8- or 16-bit packing, preloads TX FIFO, enables TX-empty interrupt, waits for completion, restores control register if it temporarily packed even 8-bit transfers as 16-bit, finalizes the transfer, and returns the byte count. `spi_st_irq()` drains RX FIFO, refills TX FIFO, and completes when words are exhausted.

## Control Flow

Probe allocates a host, gets and enables the SSC clock, maps registers, disables I2C mode, resets SSC, temporarily sets target mode before pin reconfiguration, maps the IRQ, enables runtime PM, and registers the controller. Setup requires `max_speed_hz` and a valid CS GPIO, computes `SSC_BRG`, writes mode/data-width bits into `SSC_CTL`, enables TX/RX FIFOs and the controller, and clears stale status by reading `SSC_RBUF`. Transfers proceed FIFO-batch by FIFO-batch under IRQ control.

## State and Persistence Behavior

No persistent storage exists. Per-device setup writes global controller registers, so configuration is changed for each SPI device setup. Runtime suspend disables interrupts, selects sleep pinctrl state, and disables the clock; runtime resume re-enables the clock and default pinctrl state.

## Dependencies and Integration Points

The driver depends on platform/OF resources, `irq_of_parse_and_map()`, clocks, pinctrl PM states, GPIO descriptors for chip select, completions, and the SPI controller API. It sets `auto_runtime_pm` and `use_gpio_descriptors`.

## Risks and Edge Cases

`spi_st_transfer_one()` waits without timeout, so missing TX-empty interrupts can hang. It returns `t->len` after calling `spi_finalize_current_transfer()`, whereas modern `transfer_one` implementations typically return 0 when complete; this pattern may rely on SPI core compatibility. Even-length 8-bit transfers are packed as 16-bit words, which changes byte ordering through `ssc_write_tx_fifo()`/`ssc_read_rx_fifo()` and needs device-level validation. Setup rejects devices without GPIO CS, so native-CS designs are unsupported.

## Test Signals

Test 8-bit odd/even lengths, 16-bit transfers, TX-only, RX-only, full duplex, CPOL/CPHA combinations, LSB-first, loopback, CS-high via GPIO descriptors, baud-rate min/max rejection, runtime suspend/resume, missing IRQ, and interrupt loss while a transfer is pending.
