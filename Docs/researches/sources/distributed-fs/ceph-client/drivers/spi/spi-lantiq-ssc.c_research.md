# sources/distributed-fs/ceph-client/drivers/spi/spi-lantiq-ssc.c

## Purpose

`spi-lantiq-ssc.c` is the SPI host-controller driver for Lantiq SSC and Intel LGM SSC hardware. It registers a platform SPI controller, maps SSC registers, configures clocks/FIFOs/interrupts/chip-selects, and moves SPI transfers through the hardware TX/RX FIFOs.

## Important APIs, Types, And Functions

The key state is `struct lantiq_ssc_spi`, which stores the SPI controller, MMIO base, gate/FPI clocks, hardware-variant config, FIFO sizes, current buffers, byte counters, speed, bits-per-word, and an ordered workqueue. `struct lantiq_ssc_hwcfg` abstracts SoC differences in interrupt wiring, IRQ status/ack registers, FIFO masks, and RX/TX interrupt bits.

Core helpers are register accessors, FIFO level/free/reset/flush helpers, `hw_setup_speed_hz()`, `hw_setup_bits_per_word()`, `hw_setup_clock_mode()`, `lantiq_ssc_hw_init()`, and `hw_setup_transfer()`. SPI framework hooks are `lantiq_ssc_setup()`, `lantiq_ssc_set_cs()`, `lantiq_ssc_prepare_message()`, `lantiq_ssc_unprepare_message()`, `lantiq_ssc_transfer_one()`, and `lantiq_ssc_handle_err()`. Interrupt paths are `lantiq_ssc_xmit_interrupt()`, `lantiq_ssc_err_interrupt()`, and `intel_lgm_ssc_isr()`.

## Control Flow, State, And Persistence

Probe selects hardware data from OF, allocates a controller, maps MMIO, requests variant-specific IRQs, enables clocks, reads FIFO sizes from the ID register, initializes FIFOs and controller state, then registers the SPI host. Each message enters config mode to update CPOL/CPHA/LSB/loopback and returns to active mode. Each transfer reprograms speed/word size only when cached values differ, then enables TX and/or RX.

Transfers are interrupt-driven. TX buffers initially fill the TX FIFO; RX-only transfers write `RXREQ` chunks sized to avoid FIFO overflow. Full-duplex reads wait for the expected RX fill corresponding to the last TX fill, while half-duplex RX handles the controller's 32-bit receive behavior and final partial bytes through `STAT.RXBV`. Completion is deferred to `lantiq_ssc_bussy_work()`, which waits for the hardware busy flag to clear before calling `spi_finalize_current_transfer()`.

Persistent runtime state is hardware register state plus cached transfer settings and in-flight pointers/counters protected by a spinlock. There is no disk persistence.

## Dependencies And Integration Points

The file depends on Linux platform/OF, clock, interrupt, workqueue, PM runtime headers, and SPI core. It supports compatibles `lantiq,ase-spi`, `lantiq,falcon-spi`, `lantiq,xrx100-spi`, and `intel,lgm-spi`; legacy Lantiq builds can use `clk_get_fpi()`. Internal chip-selects use SSC GPO registers, while GPIO chip-selects are delegated through SPI core descriptors.

## Risks And Test Signals

Risks include busy-waiting in the full-duplex RX path, subtle RX-only partial-byte handling, FIFO overflow at high clocks if `RXREQ` sizing is wrong, and timeout sensitivity in the final busy-bit work item. The Intel LGM IRQ-ack path differs from older Lantiq variants and needs separate coverage. Test signals include SPI loopback, TX-only/RX-only/full-duplex transfers at 8/16/32 bpw, GPIO and internal CS polarity tests, high-clock FIFO stress, injected error IRQs, and remove/probe clock and workqueue cleanup.
