# sources/distributed-fs/ceph-client/sound/soc/Kconfig

## Purpose
`sound/soc/Kconfig` is the top-level configuration menu for ALSA System-on-Chip support. It enables the ASoC core, common helper features, KUnit test toggles, ACPI/USB integration, and sources all platform, codec, SOF, SoundWire utility, and generic machine-driver Kconfig files.

## Important APIs, Types, And Functions
Key symbols are `SND_SOC`, `SND_SOC_AC97_BUS`, `SND_SOC_GENERIC_DMAENGINE_PCM`, `SND_SOC_COMPRESS`, `SND_SOC_TOPOLOGY`, `SND_SOC_TOPOLOGY_BUILD`, `SND_SOC_TOPOLOGY_KUNIT_TEST`, `SND_SOC_CARD_KUNIT_TEST`, `SND_SOC_UTILS_KUNIT_TEST`, `SND_SOC_OPS_KUNIT_TEST`, `SND_SOC_ACPI`, and `SND_SOC_USB`. The file then sources vendor/platform Kconfig files including `sound/soc/adi/Kconfig` and `sound/soc/amd/Kconfig`.

## Control Flow
There is no runtime flow. Build-time flow starts with `menuconfig SND_SOC`; when enabled, helper symbols become selectable or selected by drivers, and sourced Kconfig files add SoC-specific options.

## State And Persistence
Configuration is persisted in `.config`. The selected symbols determine which ASoC core, test, platform, codec, and helper modules are built.

## Dependencies And Integration Points
This file integrates with `sound/soc/Makefile`, ALSA PCM, AC97, regmap I2C/SPI, jack support, compress offload, topology, ACPI matching, USB offload, SOF, codec, SoundWire utility, and all SoC vendor subdirectories.

## Risks And Edge Cases
Top-level select statements affect broad dependency closure. KUnit-only symbols intentionally build fake playback devices and should not be enabled accidentally in normal production configs. Adding a new vendor directory requires matching Kconfig source and Makefile object inclusion.

## Test Signals
Signals include `allmodconfig`, `allyesconfig`, tiny KUnit configs for topology/card/utils/ops tests, and platform-specific builds confirming sourced vendor Kconfigs expose expected symbols only when `SND_SOC` is enabled.
