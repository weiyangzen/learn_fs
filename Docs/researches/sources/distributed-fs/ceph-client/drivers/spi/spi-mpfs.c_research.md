# sources/distributed-fs/ceph-client/drivers/spi/spi-mpfs.c

## Purpose

`spi-mpfs.c` drives the Microchip PolarFire SoC SPI controller. It performs polling-based FIFO transfers, supports 1- to 32-bit words, direct chip-select control, per-transfer clock generation, and interrupt-based overflow/underflow error handling.

## Important APIs, Types, And Functions

`struct mpfs_spi` stores MMIO, clock, current buffers and lengths, divider mode/value, pending slave-select register value, IRQ, and bytes per frame. Important functions are `mpfs_spi_init()`, `mpfs_spi_set_clk_gen()`, `mpfs_spi_calculate_clkgen()`, `mpfs_spi_set_mode()`, `mpfs_spi_set_framesize()`, `mpfs_spi_set_xfer_size()`, FIFO helpers, `mpfs_spi_transfer_one()`, `mpfs_spi_prepare_message()`, `mpfs_spi_set_cs()`, and `mpfs_spi_interrupt()`.

## Control Flow, State, And Persistence

Probe allocates a host, reads `num-cs`, maps registers, requests a shared IRQ, enables the clock, initializes master Motorola mode, BIGFIFO, direct CS mode, interrupts, frame size, and controller enable, then registers the host. Prepare programs CPOL/CPHA with a temporary controller disable. `set_cs()` defers CS assertion in `pending_slave_select` to avoid target-visible glitches while registers requiring disable are changed. Transfer calculates the best clock divider mode, sets frame size, resets FIFOs, writes pending CS, then loops writing and reading FIFO chunks until all frames are complete before finalizing synchronously.

State is volatile register configuration plus cached pending CS and divider values. No persistent storage exists.

## Dependencies And Integration Points

The driver depends on platform/OF, clocks, MMIO, interrupts, and SPI core. It matches `microchip,mpfs-spi`, supports GPIO descriptors, and currently defines no PM ops.

## Risks And Test Signals

Risks include polling loops without timeout, frame-count quirks between CONTROL and FRAMESUP, CS deferral correctness, divider-mode edge cases, alignment/casting for 16/32-bit buffers, and finalization from both error IRQ and transfer path. Test all word sizes, active-high/active-low CS, low/high clock requests, long transfers above 16-bit frame count, overflow/underflow injection, and repeated probe/remove.
