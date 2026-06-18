# sources/distributed-fs/ceph-client/drivers/spi/spi-bitbang-txrx.h

## Purpose
Provides inline SPI bitbang transmit/receive loops for controllers that implement `setsck()`, `setmosi()`, `getmiso()`, and `spidelay()` before including the header. It covers big-endian/MSB-first and little-endian/LSB-first bit ordering for CPHA 0 and CPHA 1 modes.

## Important APIs, Types, And Functions
The exported inline helpers are `bitbang_txrx_be_cpha0()`, `bitbang_txrx_be_cpha1()`, `bitbang_txrx_le_cpha0()`, and `bitbang_txrx_le_cpha1()`. Each takes `struct spi_device *`, half-period delay in nanoseconds, CPOL, SPI controller no-TX/no-RX flags, a word value, and bit count, then returns the received word shifted into the same scalar.

## Control Flow
Each helper loops once per bit. CPHA0 variants set MOSI on the trailing edge, delay, toggle SCK to the active edge, delay/sample MISO, then return SCK to inactive polarity. CPHA1 variants toggle SCK first, set MOSI on the leading edge, delay, toggle back, delay/sample MISO on the trailing edge. Big-endian helpers shift toward bit 31 and sample into the low bit after left shifts; little-endian helpers shift right and sample into the current high receive bit.

## State And Persistence
The header keeps no persistent state. It does cache `oldbit` locally to avoid repeated MOSI writes when the outgoing bit does not change. All external line state is maintained by the including driver’s `setsck()` and `setmosi()` implementations.

## Dependencies And Integration Points
Including code must define the four low-level line functions/macros and include SPI core definitions for mode flags. The helpers are used by bitbang-style drivers such as `spi-butterfly.c` and can be wired into the `spi_bitbang` framework in `spi-bitbang.c`.

## Risks And Edge Cases
Because this is a header-only template, incorrect or non-inline line functions can make timing unpredictable. `getmiso()` must return only 0 or 1; larger values corrupt received words. The caller must pass valid bit counts and correct CPOL/CPHA pairing. These loops are CPU-bound and can violate device timing on preempted systems or very fast requested clocks.

## Test Signals
Test with logic analyzer traces for SPI modes 0 through 3, MSB/LSB ordering, no-RX and no-TX flags, MOSI idle behavior in the caller, and devices with strict setup/hold timing. Loopback tests can validate returned word shifting for each helper.
