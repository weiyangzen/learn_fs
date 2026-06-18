# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/Makefile

## Purpose

`sound/soc/mediatek/mt8188/Makefile` defines the object composition for the MT8188 ASoC platform driver and machine driver under Kbuild. It selects which `.o` files are linked into `snd-soc-mt8188-afe.o` and which machine-card object is built for the MT8188/MT6359 configuration. The complete 16-line file was read.

## Important APIs, Types, and Functions

There are no C APIs, types, or functions. Kbuild variables are `snd-soc-mt8188-afe-y`, `obj-$(CONFIG_SND_SOC_MT8188)`, and `obj-$(CONFIG_SND_SOC_MT8188_MT6359)`. The platform aggregate includes `mt8188-afe-clk.o`, `mt8188-afe-pcm.o`, `mt8188-audsys-clk.o`, `mt8188-dai-adda.o`, `mt8188-dai-dmic.o`, `mt8188-dai-etdm.o`, and `mt8188-dai-pcm.o`; the machine driver builds `mt8188-mt6359.o`.

## Control Flow

Kbuild evaluates this file during kernel build. If `CONFIG_SND_SOC_MT8188` is enabled, it builds and links the listed platform objects into `snd-soc-mt8188-afe.o`. If `CONFIG_SND_SOC_MT8188_MT6359` is enabled, it builds the machine driver object. There is no runtime control flow in the Makefile itself.

## State and Persistence Behavior

The file has no runtime state. Its build-time state is the selected kernel configuration and the object list generated from `*-y` variables.

## Dependencies and Integration Points

It integrates with the Linux Kbuild system and the parent MediaTek ASoC Makefile. Object names must match source files in the same directory and Kconfig symbols must match the MediaTek sound Kconfig definitions. The platform aggregate is the link boundary for the MT8188 AFE driver.

## Risks and Edge Cases

Missing an object from `snd-soc-mt8188-afe-y` can produce unresolved symbols or silently omit a DAI from the platform driver. Adding an object without the matching source file breaks builds. Kconfig symbol drift between Makefile and Kconfig prevents expected drivers from building. Object order can matter if initcall or linker-section assumptions exist, though this file mostly uses ordinary driver objects.

## Test Signals

Run kernel build or at least `make M=sound/soc/mediatek/mt8188` with `CONFIG_SND_SOC_MT8188` and `CONFIG_SND_SOC_MT8188_MT6359` enabled. Check that `snd-soc-mt8188-afe.o` contains all intended platform objects and that disabling each Kconfig symbol removes the corresponding object from the build.
