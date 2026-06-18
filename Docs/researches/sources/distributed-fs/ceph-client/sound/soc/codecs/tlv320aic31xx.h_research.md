# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic31xx.h

## Purpose

`tlv320aic31xx.h` is the private definition header for the TLV320AIC31xx/DAC31xx ASoC driver. It defines supported rates/formats, codec variant flags, platform data, the paged register-address macro, register constants, and masks for clocking, interface format, power/status, interrupts, GPIO1, mute, headset detection, output common-mode voltage, and mic bias.

## Important APIs, Types, and Functions

Important types are `enum aic31xx_type`, encoding AIC3100/AIC3110/AIC3120/AIC3111/DAC3100/DAC3101 feature bits, and `struct aic31xx_pdata` for legacy platform data. Key macros include `AIC31XX_REG(page, reg)`, `AIC31XX_RATES`, `AIC31XX_FORMATS`, `AIC31XX_JACK_MASK`, register addresses from `AIC31XX_PAGECTL` through page-1 analog registers, and bit masks such as `AIC31XX_PLL_CLKIN_MASK`, `AIC31XX_IFACE1_*`, `AIC31XX_DACMUTE_MASK`, `AIC31XX_HSD_*`, and `AIC31XX_MICBIAS_MASK`.

## Control Flow

The header has no runtime flow. The C driver consumes these definitions during regmap setup, clock programming, DAI format negotiation, DAPM power-status polling, IRQ decoding, jack reporting, firmware coefficient writes, and variant-specific control/widget registration.

## State and Persistence Behavior

No state is allocated here. The definitions describe hardware register layout and variant capability bits that determine persistent register programming and runtime feature exposure.

## Dependencies and Integration Points

The header depends on ASoC rate/format and jack constants and Linux bit helpers through its including context. It integrates OF/ACPI/I2C match data with the variant-specific control and DAPM paths in `tlv320aic31xx.c`.

## Risks and Edge Cases

Variant bit definitions drive whether capture, DAC-only, mono/stereo speaker, and miniDSP behavior are exposed; wrong flags can register an invalid topology. Interrupt and volatile status masks must match hardware or jack/overflow/short-circuit reporting becomes misleading. Paged register addresses must remain consistent with regmap range configuration.

## Test Signals

Compile coverage, variant probe tests for every compatible string, register trace comparison for PLL/interface/jack/power paths, and datasheet review of masks and page offsets validate this header.
