# sources/distributed-fs/ceph-client/drivers/spi/spi-lp8841-rtc.c

## Purpose

`spi-lp8841-rtc.c` is a minimal platform SPI host for the ICP DAS LP-8841 RTC wiring. It bitbangs a DS1302-like 3-wire, LSB-first, active-high chip-select bus through an MMIO byte register.

## Important APIs, Types, And Functions

`struct spi_lp8841_rtc` stores the mapped I/O byte and current output state. Helpers `setsck()`, `setmosi()`, and `getmiso()` manipulate CLK/MOSI/MISO bits. `bitbang_txrx_be_cpha0_lsb()` clocks one LSB-first word. SPI hooks are `spi_lp8841_rtc_setup()`, `spi_lp8841_rtc_set_cs()`, and `spi_lp8841_rtc_transfer_one()`.

## Control Flow, State, And Persistence

Probe allocates a host, sets half-duplex flags, supports only `SPI_CS_HIGH | SPI_3WIRE | SPI_LSB_FIRST`, maps MMIO, and registers the controller. Setup rejects unsupported active-low, MSB-first, or non-3-wire clients. Transfers are either TX-only or RX-only; TX clears nWE and clocks bytes out, RX sets nWE and clocks bytes in. Each transfer finalizes synchronously.

Runtime state is just the output bit shadow and MMIO register. No persistent storage is used.

## Dependencies And Integration Points

The driver depends on platform/OF, MMIO, delay helpers, and SPI core. It matches `icpdas,lp8841-spi-rtc` and is intended to host an RTC protocol device above it.

## Risks And Test Signals

Risks include strict mode limitations, busy sleep timing, synchronous finalize semantics, and no support for simultaneous TX/RX buffers. Test with the RTC client using read/write register operations, mode rejection tests, CS timing on a scope, and unbind/rebind resource cleanup.
