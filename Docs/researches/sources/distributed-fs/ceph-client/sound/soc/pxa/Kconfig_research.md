# sources/distributed-fs/ceph-client/sound/soc/pxa/Kconfig

Purpose: defines build-time configuration for PXA2xx, PXA SSP, MMP SSPA, and Spitz ASoC support.

Important APIs/types/functions: root `SND_PXA2XX_SOC` selects `SND_PXA2XX_LIB`; AC97 selects new AC97 bus and PXA AC97 library; I2S is tristate selected by boards; SSP depends on `ARCH_PXA`; MMP SSPA depends on `ARCH_MMP`; Spitz selects I2S and WM8750.

Control flow: Kconfig symbols control which CPU DAI, platform, and machine drivers are compiled by the PXA Makefile.

State and persistence: build-time dependency state only.

Dependencies and integration: binds platform architecture symbols, legacy GPIO requirement for compile testing, codec selections, and ALSA library dependencies.

Risks: `SND_PXA2XX_SOC_I2S` has no prompt and is usually selected indirectly. `SND_PXA_SOC_SSP` lacks `COMPILE_TEST`, limiting coverage. AC97 requires `AC97_BUS=n` and selects `AC97_BUS_NEW`.

Test signals: PXA/MMP defconfigs, allyesconfig/allmodconfig dependency checks, and ensuring Spitz selects I2S/WM8750 correctly.
