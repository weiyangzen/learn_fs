# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic26.c

## Purpose

`tlv320aic26.c` is a self-contained SPI ASoC driver for the TI TLV320AIC26 low-power codec. It registers playback and capture DAIs, programs PLL/audio interface settings, exposes PCM and keyclick controls, creates a small DAPM graph, and provides a sysfs keyclick debug trigger.

## Important APIs, Types, and Functions

`struct aic26` stores the SPI device, regmap, component pointer, clock-provider flag, data format, MCLK, and keyclick parameters. DAI callbacks are `aic26_hw_params()`, `aic26_mute()`, `aic26_set_sysclk()`, and `aic26_set_fmt()`. Component probe is `aic26_probe()`. SPI binding is handled by `aic26_spi_probe()` with `aic26_regmap`. Sysfs support is `keyclick_show()` and `keyclick_store()`.

## Control Flow

SPI probe allocates state, initializes a 16-bit register/16-bit value regmap, stores defaults, and registers the component/DAI. Component probe resets the codec, powers it up, defaults Audio Control 3 to master mode, and creates the `keyclick` sysfs file. During stream setup, `set_sysclk()` records an MCLK in the 2-50 MHz range, `set_fmt()` records master/slave and serial data format, and `hw_params()` maps rate/width to PLL, fsref divisor, and audio-control values.

## State and Persistence Behavior

Runtime state is kept in `struct aic26`: MCLK, master/slave mode, data format, and component pointer. Register state is held by regmap and hardware; there is no explicit regcache default table. The sysfs file is devm-associated through component lifetime indirectly, but no remove callback removes it explicitly.

## Dependencies and Integration Points

Dependencies include SPI, regmap, ASoC, sysfs device attributes, and `tlv320aic26.h`. It integrates as an SPI driver named `tlv320aic26-codec`, DAI `tlv320aic26-hifi`, stereo playback/capture, DAPM pins `MICIN`, `AUX`, `HPL`, and `HPR`.

## Risks and Edge Cases

`aic26_hw_params()` can use uninitialized `reg` when neither clock-provider nor 48 kHz fsref branch assigns it, so this path deserves scrutiny. It maps S8 to 16-bit word length. MCLK must be configured before stream setup. Keyclick sysfs writes update bit `0x800` under mask `0x8000`, which appears inconsistent and should be verified.

## Test Signals

Run probe/reset/power-up tests over SPI, validate MCLK range rejection, all supported sample rates and formats, master/slave DAI formats, mute and keyclick controls, sysfs keyclick behavior, and static analysis for uninitialized register writes in `aic26_hw_params()`.
