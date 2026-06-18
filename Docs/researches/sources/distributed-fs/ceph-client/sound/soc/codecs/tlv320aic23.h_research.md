# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic23.h

## Purpose

`tlv320aic23.h` is the shared private header for the TLV320AIC23 codec core and its I2C/SPI wrappers. It declares the exported regmap configuration and common probe function, then defines the codec's register addresses, bit values, volume limits, and audio-path constants.

## Important APIs, Types, and Functions

The file declares `extern const struct regmap_config tlv320aic23_regmap` and `int tlv320aic23_probe(struct device *dev, struct regmap *regmap)`. It defines registers `TLV320AIC23_LINVOL` through `TLV320AIC23_RESET`, power bits such as `TLV320AIC23_DAC_OFF`, format bits such as `TLV320AIC23_FOR_I2S`, sample-rate bits such as `TLV320AIC23_USB_CLK_ON`, and volume/sidetone masks.

## Control Flow

The header has no runtime control flow. Its declarations allow bus wrappers to create a regmap and call the transport-neutral core. Its constants are used throughout the core for controls, DAPM, DAI setup, power, and sample-rate selection.

## State and Persistence Behavior

No state is owned here. The macros define the layout of persistent codec registers and cached values. Any change affects both bus transports because they share the common core.

## Dependencies and Integration Points

Forward declarations keep wrapper dependencies small. The header binds `tlv320aic23.c`, `tlv320aic23-i2c.c`, and `tlv320aic23-spi.c` together.

## Risks and Edge Cases

The AIC23 uses 9-bit register values and compact bitfields; wrong masks can corrupt adjacent controls. Constants such as default volume and min/max values drive user-visible ALSA ranges and need datasheet alignment.

## Test Signals

Compile both wrappers, validate register traces for volume/mute/power/format/rate paths, and compare macro values against the TLV320AIC23 datasheet.
