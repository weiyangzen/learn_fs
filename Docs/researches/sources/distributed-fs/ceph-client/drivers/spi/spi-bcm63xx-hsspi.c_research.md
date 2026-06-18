# sources/distributed-fs/ceph-client/drivers/spi/spi-bcm63xx-hsspi.c

## Purpose
Implements the Broadcom BCM63xx High Speed SPI controller driver for older broadband SoCs and compatible `bcmbca-hsspi-v1.0` hardware. It supports a 512-byte FIFO, dual-bit transfers, polling or interrupt completion modes, a prepend optimization for multi-transfer messages, and a dummy-chip-select workaround for hardware that cannot keep CS asserted through idle gaps.

## Important APIs, Types, And Functions
`struct bcm63xx_hsspi` stores completion, bus/message mutexes, platform/clock resources, MMIO base and FIFO pointer, base speed, chip-select polarity cache, sysfs-controlled wait/transfer modes, prepend metadata, and the prepend buffer. Sysfs attributes `wait_mode` and `xfer_mode` expose runtime policy. Core helpers include `bcm63xx_prepare_prepend_transfer()`, `bcm63xx_hsspi_do_prepend_txrx()`, `bcm63xx_hsspi_do_dummy_cs_txrx()`, `bcm63xx_hsspi_do_txrx()`, `bcm63xx_hsspi_set_clk()`, `bcm63xx_hsspi_set_cs()`, and `bcm63xx_hsspi_transfer_one()`.

## Control Flow
Probe obtains IRQ, registers, clocks, optional reset, allocates the host, initializes mutexes/completion, sets SPI controller capabilities, clears interrupts, caches default CS polarity, enables clock gating behavior, requests IRQ, enables runtime PM, creates sysfs attributes, and registers the controller. For each SPI message, the driver locks `msg_mutex`, tries prepend mode unless forced to dummy-CS mode, and either executes a merged/prepended transfer or falls back to dummy-CS transfer. Prepend mode combines leading half-duplex writes into controller prepend bytes and sends one final transfer. Dummy-CS mode asserts the real target manually, selects an inactive dummy CS in hardware, runs each transfer in FIFO-sized chunks, handles delay and cs_change semantics, then restores CS. Completion can be interrupt-driven via `done` or polling by watching ping-pong busy status.

## State And Persistence
`wait_mode` and `xfer_mode` persist as mutable sysfs-controlled driver state until changed or driver removal. `cs_polarity` caches per-CS polarity and is updated in setup. `prepend_cnt`, `md_start`, and `prepend_buf` are per-message scratch protected by `msg_mutex`. `bus_mutex` protects global control register changes for CS and clock polarity. System suspend disables clocks after suspending the SPI controller; resume reenables clocks and resumes the controller.

## Dependencies And Integration Points
The driver depends on Linux SPI, `spi-mem` support probing, platform resources, clocks `hsspi` and optional `pll`, optional reset control, IRQs, sysfs, mutexes, completions, runtime PM, and OF matching. It advertises CPOL/CPHA/CS_HIGH plus RX/TX dual mode and 8-bit words. Compatible strings are `brcm,bcm6328-hsspi` and `brcm,bcmbca-hsspi-v1.0`.

## Risks And Edge Cases
The prepend eligibility rules are strict: delays, `cs_change`, unsupported transfer ordering, prepend length over 15, total FIFO overrun, or single-bit after multi-bit transitions can force dummy-CS fallback or fail when prepend mode is forced. Dummy-CS mode is a hardware workaround and caps speed to 25 MHz in auto mode for safety. The transfer code mutates `t->speed_hz` when falling back, which may surprise callers if they inspect transfer state later. Sysfs mode changes race are mitigated by `msg_mutex`, but operational policy can change at runtime. Interrupt mode must clear stale status before enabling to avoid spurious completions.

## Test Signals
Test prependable flash-style messages, non-prependable messages requiring dummy CS, forced prepend failure, forced dummy-CS mode, dual RX/TX operations, FIFO boundary lengths, sysfs wait-mode switching, timeout behavior in polling and IRQ modes, CS polarity setup, suspend/resume, and `spi-mem` default support negotiation. Warnings about forced dummy-CS speed reduction and errors about non-prependable forced prepend mode are important signals.
