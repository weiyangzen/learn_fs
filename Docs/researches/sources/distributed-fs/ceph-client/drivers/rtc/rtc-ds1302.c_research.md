# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1302.c

## Purpose
Dallas/Maxim DS1302 SPI RTC driver. It provides basic clock burst read/write operations and validates enough control-register behavior during probe to detect the chip.

## Important APIs, types, and functions
- Register constants encode DS1302 shifted address plus read/write command bits.
- `ds1302_rtc_set_time()` first writes the control register to enable writes, then sends an eight-byte clock burst ending with write-disable.
- `ds1302_rtc_get_time()` reads a clock burst and decodes BCD fields into a 2000-based year.
- `ds1302_probe()` validates SPI word length, speed, and mode, reads the control register, retries suspicious values, writes write-disable if needed, verifies detection, stores the SPI device as driver data, and registers the RTC.

## Control flow
All time operations use stack buffers and `spi_write_then_read()` to avoid nonportable DMA from arbitrary stack segments. Probe rejects incompatible SPI configuration before any RTC registration.

## State and persistence behavior
Time and write-protect state persist in DS1302 registers. The driver stores the `spi_device` as its own driver data; no private struct is needed.

## Dependencies and integration points
Depends on SPI, RTC class, BCD helpers, optional OF compatible `"maxim,ds1302"`, and SPI device ID `"ds1302"`.

## Risks
- No alarm, RAM, or trickle charger support despite constants for RAM/TCR.
- The driver assumes 2000+ years and does not expose range metadata.
- SPI mode requirements are validated only for CPHA and speed; board polarity assumptions rely on board setup.
- No oscillator halt/validity checks.

## Test signals
Probe rejection for bad bits-per-word, excessive speed, and CPHA; control-register detection path; clock burst read/write round trip; and write-protect behavior after set-time.
