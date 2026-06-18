# sources/distributed-fs/ceph-client/drivers/spi/spi-jcore.c

## Purpose

`spi-jcore.c` is a simple J-Core SPI controller driver. It implements byte-at-a-time polling transfers over two MMIO registers, supports three chip selects, CPOL/CPHA/CS-high, a programmable clock divider, and optional reference-clock discovery.

## Important APIs, Types, and Functions

`struct jcore_spi` stores the SPI host, MMIO base, cached CS and speed register bits, current speed, and reference clock frequency. `jcore_spi_wait()` polls the busy bit. `jcore_spi_program()` writes cached CS/speed state to the control register. `jcore_spi_chipsel()` updates active-low/high CS bits through `set_cs`. `jcore_spi_baudrate()` calculates divider bits. `jcore_spi_txrx()` performs the transfer and finalizes it.

## Control Flow

Probe allocates a host, sets fixed capabilities, manually requests and maps MMIO, reads optional `ref_clk` rate with a 50 MHz default, initializes all CS bits high, programs a default 400 kHz speed, and registers the controller. For each transfer, the driver updates baudrate if needed, then for every byte waits idle, writes TX data or zero, starts transfer by writing control with `XMIT`, waits idle again, reads RX data if requested, and finalizes the current transfer.

## State and Persistence Behavior

Cached CS and speed bits persist in `struct jcore_spi` and are reprogrammed whenever CS or speed changes. There is no DMA, IRQ, runtime PM, or persistent storage. Attached devices see persistent effects only from SPI commands sent over the bus.

## Dependencies and Integration Points

The driver depends on platform/OF compatible `jcore,spi2`, MMIO resources, optional clock provider `ref_clk`, and the SPI core. It uses devm resource helpers for mapping and controller registration after manual memory-region request.

## Risks and Edge Cases

Transfers are purely polling and byte-at-a-time, so throughput is low and CPU-bound. `jcore_spi_txrx()` calls `spi_finalize_current_transfer()` and returns `0` on success, which is unusual because many synchronous `transfer_one` implementations either return 0 without finalizing or return 1 for async; this should be checked against SPI core expectations for this code version. Timeout is a fixed loop count rather than time-based, so it varies with CPU speed. Probe error paths use `-EBUSY` for several mapping/resource failures.

## Test Signals

Test probe with and without `ref_clk`, all three chip selects, CPOL/CPHA/CS-high, speed divider extremes, TX-only/RX-only/full-duplex byte streams, busy timeout injection before command and after command, and SPI core completion semantics for synchronous versus explicitly finalized transfers.
