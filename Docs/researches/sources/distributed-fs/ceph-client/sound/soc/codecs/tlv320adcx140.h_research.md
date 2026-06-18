# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320adcx140.h

## Purpose

`tlv320adcx140.h` is the private register and bit definition header for the TLV320ADCX140 family driver. It defines supported PCM rates/formats, register addresses, bit masks, channel limits, mic-bias encodings, power-control bits, TDM offset masks, and pin-configuration limits used by `tlv320adcx140.c`.

## Important APIs, Types, and Functions

There are no functions or structs. The important symbols are `ADCX140_RATES`, `ADCX140_FORMATS`, register addresses such as `ADCX140_ASI_CFG0`, `ADCX140_CH1_CFG*`, `ADCX140_DSP_CFG*`, `ADCX140_PWR_CFG`, and masks such as `ADCX140_WORD_LEN_MSK`, `ADCX140_INV_MSK`, `ADCX140_PWR_CTRL_MSK`, `ADCX140_TX_OFFSET_MASK`, `ADCX140_MIC_BIAS_*`, and GPIO/GPI/GPO bounds.

## Control Flow

This header has no direct control flow. Its definitions are consumed by the codec driver during regmap setup, DAI format negotiation, DAPM widget declarations, property validation, power sequencing, and ALSA mixer control declarations.

## State and Persistence Behavior

The file owns no runtime state. It defines how driver state maps onto persistent hardware registers and cached regmap entries. Changes to register constants affect resume, power-on cache sync, DAPM, and userspace control behavior.

## Dependencies and Integration Points

The header assumes ASoC PCM format/rate macros and Linux bit helpers are available through the including C file. It is tightly coupled to `tlv320adcx140.c` and the TLV320ADC3140/5140/6140 datasheet.

## Risks and Edge Cases

Incorrect masks for word length, inversion, mic-bias, or power bits can cause silent audio failure or unsafe bias/power states. The register set uses page-windowed addressing in the C file even though most definitions here are low page-zero offsets; future additions must respect the regmap range model.

## Test Signals

Compile coverage of `tlv320adcx140.c`, static comparison against datasheet register tables, and runtime register traces for DAI format, power, mic-bias, and GPIO/GPO property programming validate this header.
