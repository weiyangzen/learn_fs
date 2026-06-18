# sources/distributed-fs/ceph-client/drivers/spi/spi-microchip-core-spi.c

## Purpose

`spi-microchip-core-spi.c` is the Microchip CoreSPI controller driver for the RTL v5 IP. It implements Motorola-mode SPI transfers through a small byte FIFO, with polling for normal data movement and interrupts for overflow/underflow error reporting.

## Important APIs, Types, And Functions

`struct mchp_corespi` stores MMIO, clock, current TX/RX buffers and lengths, divider, IRQ, and FIFO depth. Main functions are `mchp_corespi_init()`, `mchp_corespi_set_clk_div()`, `mchp_corespi_write_fifo()`, `mchp_corespi_read_fifo()`, `mchp_corespi_transfer_one()`, `mchp_corespi_setup()`, `mchp_corespi_set_cs()`, and `mchp_corespi_interrupt()`.

## Control Flow, State, And Persistence

Probe validates device-tree configuration: only Motorola protocol is supported, mode is fixed by hardware configuration, frame size must be 8, and `microchip,ssel-active` must be enabled to keep CS asserted through a transfer. It maps registers, requests IRQ, enables clock, initializes master mode and interrupts, and registers the host. Each transfer sets the divider, assigns buffers, writes up to FIFO depth bytes, reads the same count back, and loops until all bytes have been clocked. It finalizes synchronously and returns `1` to indicate completion was already handled.

State is volatile hardware configuration and current buffer pointers. No persistent storage exists.

## Dependencies And Integration Points

The file depends on platform/OF properties, clocks, IRQs, MMIO byte access, and SPI core. It matches `microchip,corespi-rtl-v5` and uses GPIO descriptors when chip-selects are GPIO-backed.

## Risks And Test Signals

Risks include reliance on polling loops without data timeout, mismatch between fixed hardware Motorola mode and device mode, active-high CS rejection for native CS, and only 8-bit actual data handling despite a broader bits-per-word mask. Test DT validation failures, mode mismatch rejection, TX/RX/full-duplex transfers, FIFO-depth variations, overflow/underflow IRQ injection, and unbind disabling controller/interrupts.
