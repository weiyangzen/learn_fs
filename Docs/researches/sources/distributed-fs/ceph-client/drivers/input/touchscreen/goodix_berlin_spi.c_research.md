# sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix_berlin_spi.c

## Purpose
`goodix_berlin_spi.c` is the SPI transport wrapper for the Goodix Berlin core. It implements custom regmap bus operations that prepend Goodix SPI read/write flags, big-endian 32-bit addresses, and revision-specific dummy bytes before delegating device behavior to the common core.

## Important APIs, types, and functions
- SPI framing constants define read/write flags (`0xf1`/`0xf0`), 4-byte register width, and revision A/D read dummy and prefix lengths.
- `goodix_berlin_spi_read()` allocates one TX/RX buffer, writes read flag plus big-endian address and dummy bytes, performs `spi_sync()`, and copies payload after the configured prefix.
- `goodix_berlin_spi_write()` builds write flag plus address plus payload and performs `spi_sync()`.
- `goodix_berlin_spi_regmap_conf` supplies custom `.read` and `.write` callbacks for a 32-bit-register/8-bit-value regmap.
- `goodix_berlin_spi_probe()` forces SPI mode 0 and 8 bits per word, sizes regmap raw read/write limits from `spi_max_transfer_size()`, initializes regmap, and calls `goodix_berlin_probe()`.
- `gt9897_data` uses revision A addresses and 4 dummy bytes; `gt9916_data` uses revision D addresses and 3 dummy bytes.

## Control flow
SPI device matching selects IC data, probe configures the SPI controller, creates a regmap with transfer-size limits that account for Goodix prefixes, and calls the core. Runtime event and PM paths are core-owned; every core regmap operation routes through the custom SPI framing callbacks.

## State and persistence
The wrapper keeps no persistent private state except the regmap and SPI device configuration. IC-data read prefix/dummy lengths are essential per-device constants used on every read.

## Dependencies and integration points
The file integrates the SPI core, custom regmap accessors, OF/SPI ID matching, the input subsystem through a BUS_SPI ID, and the exported Berlin core PM/groups/probe functions.

## Risks
- `goodix_berlin_spi_write()` computes `len = count - 4`; malformed regmap calls shorter than 4 bytes would underflow, though regmap should honor `reg_bits = 32`.
- `spi_max_transfer_size()` minus prefix length can underflow if a controller reports an unexpectedly tiny maximum.
- Endianness is protocol-specific: regmap stores native u32 at the front of buffers, but the wire address is big-endian.
- Wrong dummy length for a compatible shifts all read data and causes checksum or device-confirm failures.

## Test signals
- Build with `CONFIG_TOUCHSCREEN_GOODIX_BERLIN_SPI`.
- Probe GT9897 and GT9916 compatibles and verify both read-prefix variants.
- Exercise raw register sysfs reads/writes through SPI and touch events with large enough transfer sizes for first and remaining-contact reads.
