# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/Makefile

## Purpose
This Makefile wires the MT8195 ALSA SoC platform and machine drivers into the kernel build. It defines the objects that make up the MT8195 AFE platform module and conditionally builds the MT8195 MT6359 machine driver.

## Important APIs, Types, and Build Targets
The composite object `snd-soc-mt8195-afe-y` consists of `mt8195-audsys-clk.o`, `mt8195-afe-clk.o`, `mt8195-afe-pcm.o`, `mt8195-dai-adda.o`, `mt8195-dai-etdm.o`, and `mt8195-dai-pcm.o`. `obj-$(CONFIG_SND_SOC_MT8195)` includes `snd-soc-mt8195-afe.o`, while `obj-$(CONFIG_SND_SOC_MT8195_MT6359)` includes `mt8195-mt6359.o`.

## Control Flow
There is no runtime control flow. Build control flow is Kbuild-driven: enabling `CONFIG_SND_SOC_MT8195` compiles and links the platform driver aggregate, and enabling `CONFIG_SND_SOC_MT8195_MT6359` compiles the machine driver. The order in `snd-soc-mt8195-afe-y` determines the link order inside the aggregate object but not probe order, which remains platform/driver-core controlled.

## State and Persistence
The file has no runtime state. Its persistent effect is the kernel build graph: object inclusion controls whether MT8195 AFE and machine-driver code is present in the built kernel or module.

## Dependencies and Integration Points
This file integrates the MT8195 source directory with the parent ALSA SoC Kbuild tree and Kconfig symbols. The platform object depends on the clock, PCM, ADDA, ETDM, and PCM DAI sources all building together. The machine driver is separately gated so board support can be included only when the MT6359 card driver is selected.

## Risks
Omitting an object from `snd-soc-mt8195-afe-y` can produce unresolved symbols or missing DAI registration at runtime. Adding a new DAI/source file without updating this Makefile leaves code unbuilt. Misaligned Kconfig dependencies can compile the machine driver without the platform support it expects or omit the machine driver on boards that require it.

## Test Signals
Build tests should cover `CONFIG_SND_SOC_MT8195=y/m` and `CONFIG_SND_SOC_MT8195_MT6359=y/m`. Useful signals are clean compile/link output, presence of `snd-soc-mt8195-afe` symbols or module, successful registration of ADDA/ETDM/PCM DAIs, and MT8195 MT6359 machine-driver probe when the machine config is enabled.
