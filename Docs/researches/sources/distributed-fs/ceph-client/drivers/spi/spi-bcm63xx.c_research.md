# sources/distributed-fs/ceph-client/drivers/spi/spi-bcm63xx.c

## Purpose
Implements the legacy Broadcom BCM63xx SPI controller driver for BCM6338/6348 and BCM3368/6358/6262/6368-style register layouts. It handles one FIFO-sized message batch at a time, supports only basic CPOL/CPHA and 8-bit words, and works around the controller’s inability to keep chip select active by merging transfers when possible.

## Important APIs, Types, And Functions
`struct bcm63xx_spi` stores completion, MMIO base, IRQ, layout-specific register offsets, FIFO size, message-control metadata, TX/RX IO pointers, clock, and platform device. Register-layout tables `bcm6348_spi_reg_offsets` and `bcm6358_spi_reg_offsets` adapt the same logic to two hardware families. Important functions include `bcm63xx_spi_setup_transfer()`, `bcm63xx_txrx_bufs()`, `bcm63xx_spi_transfer_one()`, `bcm63xx_spi_interrupt()`, `bcm63xx_spi_max_length()`, probe/remove, and suspend/resume.

## Control Flow
Probe chooses the register layout from OF match or platform ID, gets IRQ/clock/reset, allocates the host, maps registers, requests IRQ, sets SPI core callbacks and limits, initializes clock/reset/interrupt state, enables runtime PM, and registers the controller. Message execution walks transfers, grouping them until `cs_change` or end-of-message, while rejecting total lengths beyond FIFO size, speed changes between grouped transfers, or delays that would require CS to remain asserted. `bcm63xx_txrx_bufs()` copies TX data into the hardware message FIFO, writes dummy bytes for read-only transfers to satisfy a hidden FIFO-length accumulator, programs message control and command registers, enables command-done interrupt, waits for completion, and copies RX data back.

## State And Persistence
Persistent state is register layout, FIFO size, clock, IO pointers, and completion. Per-message state is local to transfer grouping and `bcm63xx_txrx_bufs()`. The driver does not keep per-device controller state beyond SPI core fields. Suspend suspends the controller and disables the clock; resume reenables the clock and resumes the controller.

## Dependencies And Integration Points
The driver depends on Linux SPI, platform/OF matching, clocks, reset controls, interrupts, completions, runtime PM, and MMIO. It supports platform IDs `bcm6348-spi` and `bcm6358-spi` plus OF compatibles `brcm,bcm6348-spi` and `brcm,bcm6358-spi`. It exposes `transfer_one_message` rather than `transfer_one` because it must merge transfers to approximate CS behavior.

## Risks And Edge Cases
The controller can only transfer FIFO-sized batches, and delays or speed changes inside grouped messages are rejected. Prepend support is limited to one small leading TX transfer before RX and only up to seven bytes. Read-only transfers require dummy TX writes due to hidden hardware accounting. Interrupt handling always returns handled after clearing status, so shared IRQ behavior depends on interrupt routing. Big-endian builds use `iowrite16be()` for 16-bit writes, while byte accesses remain byte-order independent.

## Test Signals
Test both register layouts, full-duplex and half-duplex transfer groups, small TX prepend followed by RX, read-only dummy-fill behavior, FIFO-limit rejection, delay and speed-change rejection, command-done timeout, suspend/resume, and legacy platform-data instantiation. Good signals are correct `actual_length`, absence of shifted RX data after prepend, and clean interrupt completion.
