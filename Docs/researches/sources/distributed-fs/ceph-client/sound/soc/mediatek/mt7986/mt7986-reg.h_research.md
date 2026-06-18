# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/mt7986-reg.h

## Purpose

This header defines MT7986 AFE register offsets and bitfields for top clocks, engine clocks, IRQs, ETDM IN/OUT, connection matrix, and DL/VUL memory interfaces.

## Important APIs, Types, and Functions

It declares offsets for IRQ control/status/clear/config registers, ETDM IN5/OUT5 controls, connection matrix registers, memif monitor/current/base/end registers with MSB support, `AFE_MAX_REGISTER`, IRQ masks, DL0/VUL0 control fields, and ETDM field macros built with `BIT()`/`GENMASK()`.

## Control Flow

No executable flow. Platform and ETDM files use these macros in regmap config, runtime PM, IRQ handling, memif data tables, DAPM controls, and ETDM parameter programming.

## State and Persistence Behavior

The header maps persistent hardware state. `mt7986-afe-pcm.c` marks current/monitor/status registers volatile to avoid caching live hardware values.

## Dependencies and Integration Points

Included by MT7986 PCM and ETDM files. Values must align with the MMIO resource and hardware programming guide.

## Risks and Edge Cases

ETDM fields use mask macros with `FIELD_PREP`; mismatched masks cause invalid packed values. `AFE_MAX_REGISTER` stops at `AFE_VUL0_CON0`, so any later register addition needs regmap range updates. 64-bit DMA address fields depend on base/end/current MSB offsets being correct.

## Test Signals

Regmap traces for runtime PM, IRQ config/clear, memif DMA setup, and ETDM format/rate setup validate the map.
