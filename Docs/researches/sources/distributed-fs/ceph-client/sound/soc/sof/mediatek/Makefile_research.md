# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/Makefile

Purpose: Connects MediaTek SOF Kconfig symbols to object directories.

Important build rules: `CONFIG_SND_SOC_SOF_MTK_COMMON` builds `mtk-adsp-common.o`; `CONFIG_SND_SOC_SOF_MT8195` descends into `mt8195/`; `CONFIG_SND_SOC_SOF_MT8186` descends into `mt8186/`.

Control flow and integration: The common object exports helpers consumed by both SoC subdrivers. Subdirectory Makefiles build SoC-specific platform, clock, and loader units into their module objects.

State and persistence: No runtime state. Build output shape determines module composition and namespace import requirements in the SoC drivers.

Risks: A SoC object depends on common exports, so disabling or misselecting `SND_SOC_SOF_MTK_COMMON` causes unresolved symbols. Directory order is simple but new SoCs must add both Kconfig and Makefile entries.

Test signals: Module build with common only, MT8186 only, MT8195 only, and both SoCs; `modpost` namespace/import checks.
