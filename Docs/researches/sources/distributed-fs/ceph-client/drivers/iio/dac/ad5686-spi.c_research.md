# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5686-spi.c

## Purpose
`ad5686-spi.c` is the SPI transport implementation for the shared AD5686/AD567x/AD569x DAC family driver. It handles multiple register map encodings and delegates common IIO behavior to `ad5686.c`.

## Important APIs, Types, And Functions
- `ad5686_spi_write()` emits 2-byte or 3-byte SPI frames depending on `AD5310_REGMAP`, `AD5683_REGMAP`, or `AD5686_REGMAP`.
- `ad5686_spi_read()` implements readback enable plus NOP read for register maps that support readback.
- `ad5686_spi_probe()` calls `ad5686_probe()` with the SPI write/read callbacks.
- SPI IDs map part names to `enum ad5686_supported_device_ids`.

## Control Flow
Probe obtains the SPI ID and delegates to common probe. Runtime writes enter through `st->write` and are encoded according to the chip info’s `regmap_type`. Runtime reads program readback and then clock a NOP frame; AD5310 readback returns `-ENOTSUPP`.

## State And Persistence
The SPI wrapper uses `struct ad5686_state` transfer buffers and chip info selected by common probe. It maintains no independent persistent state.

## Dependencies And Integration Points
The file depends on SPI core, the common `ad5686.h` API, and imports namespace `IIO_AD5686`. Supported parts include AD5310R, AD5672R/74R/76/76R/79R, and AD5681R/82R/83/83R/84/84R/85R/86/86R.

## Risks And Edge Cases
- `AD5683_REGMAP` uses `&d8[1]` of a big-endian 32-bit word for a 3-byte frame; tests should pin byte ordering.
- Unsupported readback for AD5310 means common raw reads can return `-ENOTSUPP`; user ABI behavior should be acceptable for those parts.
- The SPI ID includes `"ad5685"` mapped to `ID_AD5685R` with a comment that the part does not exist; this compatibility alias should not be propagated without review.

## Test Signals
Transport tests should validate per-regmap write frames, readback commands, NOP transfer ordering, AD5310 read failure behavior, and correct chip ID mapping from SPI device IDs.
