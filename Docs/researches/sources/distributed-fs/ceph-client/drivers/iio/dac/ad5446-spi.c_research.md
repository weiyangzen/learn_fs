
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5446-spi.c

## Purpose
`ad5446-spi.c` is the SPI transport front-end for the AD5446 common single-channel DAC core. It supports many ADI and compatible TI SPI DACs with 16-bit or 24-bit write formats and per-chip channel/reference metadata.

## Important APIs, types, and functions
- `ad5446_write()` sends a 16-bit big-endian value over SPI.
- `ad5660_write()` sends a 24-bit big-endian value over SPI for AD5660/AD5662-like parts.
- `ad5446_spi_probe()` resolves match data and delegates to common `ad5446_probe()`.
- Numerous `struct ad5446_chip_info` constants define resolution, storage, shift, optional internal vref, powerdown support, and write callback.
- SPI ID and OF tables map ADI/TI compatible names to chip info.

## Control flow
Probe resolves chip info from match data and calls the common core. Runtime writes are routed through the chip-specific write callback selected in chip info. The common core handles IIO registration, raw validation, caching, powerdown, and scale.

## State and persistence behavior
Transport state is stored in the common `ad5446_state` DMA-aligned 16/24-bit buffer. Chip metadata is static. DAC and powerdown state are cached in the common core and written to hardware.

## Dependencies and integration points
Depends on SPI, OF/SPI ID matching, unaligned 24-bit writes, and exported common core namespace `IIO_AD5446`.

## Risks and edge cases
- `ad5446_spi_probe()` retrieves `id->name` even though match data comes from SPI/OF; OF-only instantiation still needs a valid SPI ID mapping.
- Many compatibles alias to similar chip info; scale/shift mistakes affect user-visible voltage conversion and wire format.
- 24-bit writes use `put_unaligned_be24()` into a 3-byte buffer, so buffer alignment and DMA safety rely on the union in common state.

## Test signals
Verify 16-bit and 24-bit SPI payloads for representative chips, internal-vref fallback variants, TI compatible aliases, powerdown-capable vs non-powerdown channel ext info, and common raw cache behavior while powered down.
