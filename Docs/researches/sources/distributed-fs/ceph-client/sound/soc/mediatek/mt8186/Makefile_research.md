# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/Makefile

## Purpose

This Kbuild file assembles the MT8186 ASoC platform driver object and the MT8186 machine-driver object. It determines which MT8186 audio implementation files are linked when the relevant kernel configuration symbols are enabled.

## Important APIs, Types, and Data

`snd-soc-mt8186-afe-y` lists the component objects for the platform AFE driver: PCM/probe, audsys clock provider, AFE clock orchestration, GPIO, ADDA, common controls, I2S, hardware gain, PCM DAI, SRC, hostless, TDM, miscellaneous controls, and MT6366 helpers. `obj-$(CONFIG_SND_SOC_MT8186)` links those objects into `snd-soc-mt8186-afe.o`. `obj-$(CONFIG_SND_SOC_MT8186_MT6366)` links the separate `mt8186-mt6366.o` machine driver.

## Control Flow and State

There is no runtime flow. The build-time order affects link composition but not constructor order; platform registration still comes from the C files' module/platform-driver declarations.

## Dependencies and Integration Points

This file integrates with the kernel sound SoC Kbuild hierarchy and with Kconfig symbols. It must stay synchronized with registration callbacks in `mt8186-afe-pcm.c` and exported helpers declared in MT8186 headers.

## Risks

Omitting an object can create undefined symbols or silently remove DAI/control registration. Adding a new DAI implementation without updating this list leaves the code unbuilt even if headers compile elsewhere. The MT6366 common helper being included in the AFE object means codec-board helper dependencies must remain compatible with platform-driver builds.

## Test Signals

Primary validation is `CONFIG_SND_SOC_MT8186=y/m` and `CONFIG_SND_SOC_MT8186_MT6366=y/m` kernel builds. Link errors, missing module aliases, or a probed AFE component lacking expected DAIs are direct signals that this Makefile is out of sync.
