# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5677-spi.h

## Purpose

`rt5677-spi.h` is the small integration header between the main RT5677 codec driver and the optional SPI DSP support module. It declares the SPI memory access and hotword notification helpers when `CONFIG_SND_SOC_RT5677_SPI` is enabled, and provides harmless fallback stubs when that support is disabled.

## Important APIs and definitions

When `IS_ENABLED(CONFIG_SND_SOC_RT5677_SPI)` is true, the header declares `rt5677_spi_read(u32 addr, void *rxbuf, size_t len)`, `rt5677_spi_write(u32 addr, const void *txbuf, size_t len)`, `rt5677_spi_write_firmware(u32 addr, const struct firmware *fw)`, and `rt5677_spi_hotword_detected(void)`.

When the config is disabled, the read/write/firmware helpers are static inline functions returning `-EINVAL`, and `rt5677_spi_hotword_detected()` is an empty inline function. This lets `rt5677.c` compile without preprocessor conditionals around every call site, while still making runtime attempts fail clearly for operations that require SPI support.

## Control flow

There is no standalone runtime control flow in the header. Compile-time configuration selects either external symbol declarations implemented by `rt5677-spi.c` or local inline fallback bodies. Callers such as DSP firmware loading and hotword interrupt handling in `rt5677.c` can call the helpers unconditionally. With SPI enabled, those calls cross into the SPI driver. With SPI disabled, memory-access calls return failure immediately and hotword notification becomes a no-op.

## State and persistence behavior

The header stores no state. State lives in `rt5677-spi.c` (`g_spi`, `struct rt5677_dsp`, copy work, PCM offsets) or in the main codec private data. The fallback stubs do not persist anything and do not mutate caller buffers.

## Dependencies and integration points

The prototypes use kernel fixed-width type `u32`, `size_t`, and `struct firmware`; including files must have appropriate kernel type declarations available through surrounding includes. The compile-time gate uses `IS_ENABLED()` and `CONFIG_SND_SOC_RT5677_SPI`. The main integration point is `rt5677.c`, which includes this header for DSP firmware loading and hotword notification, while the SPI implementation includes the same header to match exported signatures.

## Risks and edge cases

The fallback return value is `-EINVAL`, not `-ENODEV` or `-EOPNOTSUPP`, so callers need to treat it as a generic failure rather than a precise absence-of-device signal. The empty hotword fallback intentionally drops hotword notifications when SPI support is disabled. Because the header only declares behavior and does not document alignment requirements, callers must rely on `rt5677-spi.c` semantics: reads require 4-byte aligned address and length, and writes require 4-byte aligned address with zero padding for tail bytes.

## Test signals

Compile both enabled and disabled configurations. In the enabled configuration, `rt5677-spi.c` must provide all exported symbols and the main codec should load/link cleanly. In the disabled configuration, `rt5677.c` should still compile, firmware load paths should see `-EINVAL` if they attempt SPI transfer, and hotword notification should not dereference any SPI state.
