# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-afe-common.h

## Purpose

This header defines the MT2701 AFE private contract: memory-interface IDs, back-end DAI IDs, IRQ IDs, base-clock IDs, PLL-domain constants, I2S path metadata, SoC variant flags, and private driver state.

## Important APIs, Types, and Functions

- `MT2701_PLL_DOMAIN_0_RATE` and `MT2701_PLL_DOMAIN_1_RATE` identify MCLK parent-rate families.
- Memif enum covers DL1-DL5, multichannel DLM, UL1-UL5, DLBT, ULBT, and IO DAI IDs for I2S and MRG BT.
- IRQ enum defines three ASYS IRQ lines.
- `enum audio_base_clock` indexes named clocks acquired in the clock driver.
- `struct mt2701_i2s_data` maps one I2S control register to ASRC FS shift/mask fields.
- `struct mt2701_i2s_path` stores path refcounts, occupation flags, clock handles, MCLK rate, and per-direction register metadata.
- `struct mt2701_soc_variants` distinguishes MT2701 from MT7622 one-heart-mode behavior.
- `struct mt2701_afe_private` is platform-private state used across PCM and clock code.

## Control Flow

There is no executable flow. The enums drive array indexes in the PCM file, and the structs are initialized at probe before DAI callbacks and runtime PM use them.

## State and Persistence Behavior

`mt2701_i2s_path.on[]`, `occupied[]`, and `mclk_rate` are in-memory state that persists while the platform device is bound. Clock handles are devm-owned. Register state is not stored here but is addressed through included `mt2701-reg.h`.

## Dependencies and Integration Points

The header includes ALSA SoC, CCF, regmap, local register definitions, and the common `mtk-base-afe` infrastructure. It is shared by clock-control, PCM platform, and machine drivers.

## Risks and Edge Cases

Enum ordering is an ABI inside the driver because memif arrays, DAI IDs, and route IDs depend on it. `MT2701_IO_*` values follow `MT2701_MEMIF_NUM`, so adding memifs can shift all IO IDs. The one-heart-mode flag changes MCLK path selection and must match the compatible data.

## Test Signals

Build all MT2701 objects and boot both `"mediatek,mt2701-audio"` and `"mediatek,mt7622-audio"` compatibles. Confirm DAI IDs, I2S counts, and MCLK selection through logs/regmap traces.
