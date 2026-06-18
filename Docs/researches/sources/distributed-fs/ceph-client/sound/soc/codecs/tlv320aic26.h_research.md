# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic26.h

## Purpose

`tlv320aic26.h` defines the TLV320AIC26 register address encoding and symbolic values used by the SPI codec driver. It covers auxiliary data/control pages, audio control registers, filter coefficient registers, PLL registers, fsref divisors, digital audio formats, and sample word lengths.

## Important APIs, Types, and Functions

There are no functions. `AIC26_PAGE_ADDR(page, offset)` builds the 16-bit register address used by regmap. Register constants include `AIC26_REG_AUDIO_CTRL1`, `AIC26_REG_DAC_GAIN`, `AIC26_REG_POWER_CTRL`, `AIC26_REG_PLL_PROG1`, and coefficient registers. Enums `aic26_divisors`, `aic26_datfm`, and `aic26_wlen` provide values consumed by DAI setup.

## Control Flow

The header has no flow of its own. `tlv320aic26.c` uses the register and enum constants during probe reset/power-up, sample-rate PLL programming, format selection, mute, ALSA controls, and keyclick sysfs operations.

## State and Persistence Behavior

No runtime state is defined. The file describes persistent hardware register addresses and values. Since the driver's regmap has 16-bit register addresses, `AIC26_PAGE_ADDR()` is central to all persistent hardware access.

## Dependencies and Integration Points

The header is private to `tlv320aic26.c` and mirrors the TLV320AIC26 datasheet's paged register map.

## Risks and Edge Cases

Address-shift mistakes in `AIC26_PAGE_ADDR()` or enum values would redirect every SPI register access. Word-length and data-format enums share fields in Audio Control 1, so future additions must preserve bit placement.

## Test Signals

Compile the codec driver, trace SPI register addresses for reset/audio-control/PLL paths, and compare generated addresses and bit values with the datasheet.
