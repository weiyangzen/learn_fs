# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/Makefile

## Purpose

This Makefile builds the MT7986 AFE platform composite and optional WM8960 machine driver.

## Important APIs, Types, and Functions

`snd-soc-mt7986-afe-y` links `mt7986-afe-pcm.o` and `mt7986-dai-etdm.o`. `CONFIG_SND_SOC_MT7986` builds the platform object, and `CONFIG_SND_SOC_MT7986_WM8960` builds `mt7986-wm8960.o`.

## Control Flow

Kbuild links ETDM DAI support into the platform object so `mt7986_afe_pcm.c` can call `mt7986_dai_etdm_register()`.

## State and Persistence Behavior

No runtime state; only build composition.

## Dependencies and Integration Points

The platform object depends on the ETDM sub-DAI file. The machine object depends on the platform DAI names and WM8960 codec driver.

## Risks and Edge Cases

Leaving out `mt7986-dai-etdm.o` breaks the machine BE path and the platform link. Building the machine driver without platform/codec support yields no usable card.

## Test Signals

Kbuild both Kconfig symbols and boot with a matching DT card to validate object integration.
