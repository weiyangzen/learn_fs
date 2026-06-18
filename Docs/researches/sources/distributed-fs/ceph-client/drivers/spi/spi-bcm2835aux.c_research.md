# sources/distributed-fs/ceph-client/drivers/spi/spi-bcm2835aux.c

## Purpose
Implements the Broadcom BCM2835 auxiliary SPI controller driver. It is a simpler polling/IRQ driver for the auxiliary SPI block and intentionally relies on GPIO chip-selects for correct operation, preserving limited native-CS behavior only for legacy device trees.

## Important APIs, Types, And Functions
`struct bcm2835aux_spi` stores MMIO base, clock, IRQ, precomputed CNTL0/CNTL1 register values, transfer buffers and counters, pending byte count, debugfs counters, and debugfs directory. FIFO helpers `bcm2835aux_rd_fifo()` and `bcm2835aux_wr_fifo()` move up to 3 bytes per hardware word using variable-width mode. Transfer logic is split between `bcm2835aux_spi_transfer_helper()`, polling, IRQ, and common transfer entry functions. SPI core hooks include setup, prepare/unprepare message, transfer_one, and error handling.

## Control Flow
Probe allocates the host, sets mode bits and callbacks, maps registers, enables the clock, validates clock rate, resets the block, requests a shared IRQ, registers the controller, and creates debugfs counters. `prepare_message()` computes CNTL0/CNTL1 according to CPOL and writes initial mode registers. `transfer_one()` computes the speed field, stores TX/RX pointers and lengths, clears pending count, estimates whether the transfer should complete within the polling limit, then chooses polling or IRQ. The common helper drains RX words while RX level is nonzero and writes TX words while pending bytes are below the 12-byte FIFO limit. IRQ mode enables TX-empty and idle interrupts, disables TX-empty once TX is exhausted, and finalizes when RX length reaches zero. Unprepare and error handling reset the hardware.

## State And Persistence
Persistent state is mostly controller resources, precomputed register images, and debugfs counters. Transfer state is `tx_buf`, `rx_buf`, `tx_len`, `rx_len`, and `pending`, where `pending` tracks transmitted bytes not yet received back. CNTL register images are recomputed per message and speed bits are updated per transfer. There is no DMA state and no persistent child-device state.

## Dependencies And Integration Points
The driver depends on Linux SPI, platform resources, OF matching, clocks, shared IRQs, debugfs, and MMIO. It matches `brcm,bcm2835-aux-spi`, advertises `SPI_CPOL`, `SPI_CS_HIGH`, and `SPI_NO_CS`, supports 8-bit words, and uses GPIO descriptors. Native chip select is warned against and only CS0 is tolerated for old DT compatibility.

## Risks And Edge Cases
The auxiliary hardware writes up to 3 bytes per FIFO word in variable-width mode; off-by-one errors in `pending` or RX length can misalign data. Native chip-select behavior is explicitly broken for multiple CS, CS high, `cs_change`, and delays, so board descriptions should use `cs-gpio`. Polling fallback to IRQ depends on the `polling_limit_us` module parameter. The driver does not support SPI_CPHA, so clients requiring other modes must not bind here.

## Test Signals
Test GPIO chip-select transfers, short polling transfers, longer IRQ transfers, TX-only/RX-only/full-duplex buffers whose lengths are not multiples of 3, CPOL mode behavior, polling disabled by setting `polling_limit_us=0`, native-CS warning paths, and error reset. Debugfs counters should show polling, IRQ, and polling-to-IRQ fallback counts.
