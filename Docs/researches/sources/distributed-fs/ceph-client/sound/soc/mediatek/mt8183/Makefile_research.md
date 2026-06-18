# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/Makefile

Purpose: defines the MT8183 ASoC build composition for the platform AFE module and board-specific machine drivers.

Important APIs/types/functions: `snd-soc-mt8183-afe-y` groups `mt8183-afe-pcm.o`, `mt8183-afe-clk.o`, and the DAI implementation objects for I2S, TDM, PCM, hostless, and ADDA. Kconfig objects map `CONFIG_SND_SOC_MT8183` to the aggregate AFE module, `CONFIG_SND_SOC_MT8183_MT6358_TS3A227E_MAX98357A` to the MT6358/TS3A227/MAX98357 machine driver, and `CONFIG_SND_SOC_MT8183_DA7219_MAX98357A` to the DA7219/MAX98357/RT1015 variants.

Control flow: during kernel build, kbuild compiles the listed objects into `snd-soc-mt8183-afe.o` when the platform config is enabled, and separately builds machine-driver modules based on board config symbols.

State and persistence: no runtime state; this file controls build-time object aggregation and module availability.

Dependencies and integration: integrates with kernel kbuild and the MT8183 ASoC Kconfig symbols. The aggregate object must include every sub-DAI implementation referenced by `mt8183-afe-pcm.c` registration callbacks.

Risks: missing an object from `snd-soc-mt8183-afe-y` would create unresolved symbols or absent DAI registrations. Machine drivers can build independently only if their referenced common/platform symbols are available through selected configs.

Test signals: `make M=sound/soc/mediatek/mt8183`, all relevant Kconfig combinations, modpost symbol checks, and boot-time probe of both aggregate AFE and board-specific card modules.
