# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/Makefile

## Purpose
Kbuild fragment for MT8365 ASoC support. It defines which object files make up the MT8365 platform AFE module and which machine-driver object is built for the MT8365 plus MT6357 codec card.

## APIs, Types, and Functions
The file declares `snd-soc-mt8365-pcm-y` as a composite object containing `mt8365-afe-clk.o`, `mt8365-afe-pcm.o`, `mt8365-dai-adda.o`, `mt8365-dai-dmic.o`, `mt8365-dai-i2s.o`, and `mt8365-dai-pcm.o`. It wires `obj-$(CONFIG_SND_SOC_MT8365)` to `snd-soc-mt8365-pcm.o` and `obj-$(CONFIG_SND_SOC_MT8365_MT6357)` to `mt8365-mt6357.o`.

## Control Flow, State, and Persistence
There is no runtime state. Build-time control flow is driven by Kconfig: enabling `CONFIG_SND_SOC_MT8365` builds the platform component with all listed sub-DAI implementation objects linked together; enabling `CONFIG_SND_SOC_MT8365_MT6357` builds the matching machine driver.

## Dependencies and Integration
This Makefile is consumed by the kernel sound/soc/mediatek build. The composite object depends on all listed MT8365 source files sharing internal symbols such as `mt8365_afe_enable_main_clk()`, `mt8365_dai_adda_register()`, `mt8365_dai_dmic_register()`, and the I2S/PCM registration functions. The machine driver depends on the platform component being available through ALSA SoC registration and device-tree matching.

## Risks and Test Signals
Risks include omitting a source object that provides a registration callback used by `mt8365-afe-pcm.c`, building machine support without the platform driver selected, or stale object names after source renames. Test signals are successful kernel/module builds for both Kconfig symbols, no unresolved MT8365 symbols at link/modpost time, and runtime probe of both the platform device and MT8365-MT6357 sound card.
