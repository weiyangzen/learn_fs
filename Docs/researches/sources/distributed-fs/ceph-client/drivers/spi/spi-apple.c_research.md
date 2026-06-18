# sources/distributed-fs/ceph-client/drivers/spi/spi-apple.c

## Purpose
Apple SoC SPI host driver for Asahi-supported Apple controllers, exposing one chip select through the Linux SPI core. It programs Apple-specific MMIO registers for IRQ or short polling transfers, supports CPOL, CPHA, LSB-first, 1 to 32 bits per word, GPIO descriptors, and runtime PM.

## Important APIs, Types, and Functions
`struct apple_spi` holds MMIO base, enabled clock, and a completion for IRQ wakeups. Register helpers wrap relaxed MMIO access. `apple_spi_init()` resets FIFOs, selects IRQ mode, disables delay registers, and leaves CS inactive. `apple_spi_prepare_message()` programs mode bits. `apple_spi_set_cs()` drives the hardware CS bit. `apple_spi_transfer_one()` is the main SPI core callback and delegates setup, FIFO push, FIFO drain, and waits to `apple_spi_prep_transfer()`, `apple_spi_tx()`, `apple_spi_rx()`, and `apple_spi_wait()`.

## Control Flow
Probe allocates a managed SPI controller, maps registers, enables the bus clock, requests the IRQ, enables runtime PM, initializes hardware, and registers the controller. For each transfer, the driver computes a clock divider, sets bits per word in `SHIFTCFG`, resets FIFOs, clears interrupt flags, programs TX/RX word counts, primes TX FIFO, starts the controller, then loops until the requested TX and RX completion bits have been seen. Depending on expected wait time, completion is either polled or IRQ-driven through `apple_spi_irq()`.

## State and Persistence
State is volatile hardware state plus the per-transfer local cursor variables. The driver does not persist configuration outside registers. Runtime PM is automatic through the SPI core, with clock ownership handled by devm clock APIs.

## Dependencies and Integration Points
It integrates with platform devices matched by `apple,t8103-spi` or `apple,spi`, Linux `spi_controller`, clk, IRQ, MMIO, OF, and PM runtime. It relies on SPI core validation for most transfer shape constraints.

## Risks
Timeouts are bounded at 200 ms per wait, but a completed RX transfer can still require a retry loop to pull the final word. `WARN_ON()` catches unexpected FIFO overrun or underrun after completion. Lengths not aligned to the chosen bytes-per-word are converted by integer division, so SPI core validation is important. The clock divider is capped at `0x7ff`, which may silently produce a faster-than-requested low speed.

## Test Signals
Useful signals are probe success, IRQ delivery, no transfer timeout logs, expected `actual_length` from SPI core tests, loopback transfers at 8/16/32 bpw, LSB-first mode tests, and stress tests around RX-only, TX-only, full-duplex, and very slow transfers.
