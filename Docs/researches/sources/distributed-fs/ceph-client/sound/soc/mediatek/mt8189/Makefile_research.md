# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/Makefile

## Purpose

The MT8189 ASoC Makefile wires the platform and machine drivers into the kernel build. It adds the shared MediaTek ASoC include directory, aggregates the MT8189 AFE platform object from its component source files, and conditionally builds the MT8189 platform and NAU8825 machine driver based on Kconfig symbols.

## Important APIs, Types, and Data

The file is Kbuild data rather than C code. `subdir-ccflags-y += -I$(srctree)/sound/soc/mediatek/common` makes common MediaTek headers visible to all compilation units in this folder. `snd-soc-mt8189-afe-objs` declares the object list linked into `snd-soc-mt8189-afe.o`: PCM core, clock control, ADDA DAI, I2S DAI, PCM DAI, and TDM DAI. `obj-$(CONFIG_SND_SOC_MT8189)` enables the platform object, while `obj-$(CONFIG_SND_SOC_MT8189_NAU8825)` enables `mt8189-nau8825.o`.

## Control Flow

There is no runtime control flow. During kernel build, Kbuild expands the conditional object variables according to `.config`. If `CONFIG_SND_SOC_MT8189=y` or `m`, all listed platform objects are compiled and linked as the MT8189 AFE driver. If the NAU8825 machine-driver config is selected, that machine driver is also built.

## State and Persistence

No runtime state is held. The Makefile affects build artifacts and module composition. A stale or missing object entry persists only as a build configuration issue until the Makefile or Kconfig selection changes.

## Dependencies and Integration Points

The platform object list must stay aligned with implemented MT8189 source files and exported functions declared in `mt8189-afe-common.h` and `mt8189-afe-clk.h`. The include path integrates with `../common/mtk-base-afe.h` and other shared MediaTek audio helpers. Kconfig symbols `CONFIG_SND_SOC_MT8189` and `CONFIG_SND_SOC_MT8189_NAU8825` must be defined elsewhere in the sound subsystem.

## Risks

The main risk is build drift. Adding a new DAI implementation without adding it to `snd-soc-mt8189-afe-objs` can leave registration functions unresolved or features absent. Removing or renaming a source file without updating this list breaks builds. If the common include path changes, all local sources using shared MediaTek headers can fail. Machine drivers are conditional separately from the platform driver, so configuration dependencies must prevent selecting a machine driver without the required platform support.

## Test Signals

Useful checks are `make M=sound/soc/mediatek/mt8189`, full kernel builds for built-in and module configurations, `modpost` symbol checks, and boot/probe validation with `CONFIG_SND_SOC_MT8189` and `CONFIG_SND_SOC_MT8189_NAU8825` enabled. Build logs should show every object in `snd-soc-mt8189-afe-objs` compiled exactly once.
