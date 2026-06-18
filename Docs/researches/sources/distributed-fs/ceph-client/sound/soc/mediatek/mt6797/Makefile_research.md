# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/Makefile

## Purpose

This Makefile defines the MT6797 AFE composite platform driver and MT6351 machine driver build entries.

## Important APIs, Types, and Functions

`snd-soc-mt6797-afe-y` links `mt6797-afe-pcm.o`, `mt6797-afe-clk.o`, `mt6797-dai-pcm.o`, `mt6797-dai-hostless.o`, and `mt6797-dai-adda.o`. `CONFIG_SND_SOC_MT6797` builds the platform object, and `CONFIG_SND_SOC_MT6797_MT6351` builds the machine card.

## Control Flow

Kbuild combines sub-DAI implementation objects with the platform probe object so the registration callbacks resolve at link time.

## State and Persistence Behavior

No runtime state; it controls compiled object composition.

## Dependencies and Integration Points

The platform object depends on all sub-DAI files because `mt6797-afe-pcm.c` calls each `mt6797_dai_*_register()` callback. The machine driver depends on the platform and MT6351 codec names being present.

## Risks and Edge Cases

Dropping a sub-DAI object breaks links or removes routes expected by the MT6351 card. Enabling only the machine driver without a matching platform/codec DT stack leaves no card.

## Test Signals

Kbuild with `CONFIG_SND_SOC_MT6797=y/m` and `CONFIG_SND_SOC_MT6797_MT6351=y/m` should link cleanly; runtime should enumerate all FE/BE DAIs.
