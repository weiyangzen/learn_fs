# sources/distributed-fs/ceph-client/sound/soc/loongson/Kconfig

## Purpose
Defines build options for Loongson ASoC machine, I2S PCI, I2S platform, and Loongson1 AC97 drivers.

## Important APIs, Types, And Functions
`SND_SOC_LOONGSON_CARD` selects PCI or platform I2S support depending on available buses. `SND_SOC_LOONGSON_I2S_PCI` depends on PCI and selects `REGMAP_MMIO`; `SND_SOC_LOONGSON_I2S_PLATFORM` selects regmap and generic dmaengine PCM. `SND_LOONGSON1_AC97` depends on `LOONGSON1_APB_DMA` and selects AC97 codec, generic dmaengine PCM, and regmap MMIO.

## Control Flow, State, And Persistence
No runtime state. The symbols shape which Loongson audio layers are built.

## Dependencies And Integration Points
Matches the Loongson Makefile and separates LoongArch I2S support from Loongson1 APB DMA AC97 support.

## Risks And Test Signals
Risks include automatically selecting both I2S front ends when the card driver is enabled, and compile gaps for AC97 on non-Loongson1 configurations. Test signals are COMPILE_TEST/allmodconfig and real LoongArch PCI/OF build configurations.
