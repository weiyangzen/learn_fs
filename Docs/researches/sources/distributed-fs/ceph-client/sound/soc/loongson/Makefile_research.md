# sources/distributed-fs/ceph-client/sound/soc/loongson/Makefile

## Purpose
Builds Loongson I2S PCI, I2S platform, common I2S, AC97, and sound-card modules.

## Important APIs, Types, And Functions
The PCI composite object includes `loongson_i2s_pci.o` and `loongson_dma.o`, and additionally links the common `snd-soc-loongson-i2s.o`. The platform object includes `loongson_i2s_plat.o` and common I2S. The AC97 object is standalone. The card object builds from `loongson_card.o`.

## Control Flow, State, And Persistence
No runtime behavior; this describes module composition.

## Dependencies And Integration Points
Integrates with Loongson Kconfig symbols and ensures both PCI and platform front ends reuse `loongson_i2s.c`.

## Risks And Test Signals
Risks include double-linking the common I2S module if symbols are configured unexpectedly, and stale composite names. Test signals are separate module builds for PCI, platform, card, and AC97 configurations.
