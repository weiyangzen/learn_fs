# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-common.h

## Purpose

`mt8186-afe-common.h` is the central MT8186 AFE contract shared by the platform driver, clock code, control helpers, and DAI implementations. It defines memif IDs, DAI IDs, IRQ IDs, APLL/MTKAIF enums, common stream aliases, private runtime state, and registration/control prototypes.

## Important APIs, Types, and Data

The first enum assigns `MT8186_MEMIF_*` IDs for playback and capture DMA engines and then continues into DAI IDs such as ADDA, AP DMIC, I2S, HW gain, SRC, PCM, TDM, and hostless paths. Aliases such as `MT8186_RECORD_MEMIF`, `MT8186_PRIMARY_MEMIF`, and `MT8186_BARGEIN_MEMIF` identify policy-level stream roles. `MT8186_IRQ_0` through `MT8186_IRQ_26` index IRQ metadata. MTKAIF protocol constants and ADDA gain constants are shared with ADDA setup code. MCLK IDs identify I2S/TDM master-clock outputs.

`struct mt8186_afe_private` stores clock handles, clkdev lookups, syscon regmaps, per-memif IRQ counter overrides, debug/control values, xrun assertions, DAI on/private data arrays, MTKAIF calibration/protocol fields, DMIC and loopback state, and MCLK rates.

Function prototypes expose DAI registration callbacks, misc-control registration, rate transforms, I2S sharing, and DAI-private allocation.

## Control Flow and State

The header defines no flow, but its IDs drive almost every runtime table in this directory. `mt8186_afe_pcm_dev_probe()` allocates `struct mt8186_afe_private`; DAI register functions attach per-DAI private blocks into `dai_priv`; ALSA controls mutate fields such as `irq_cnt`, `xrun_assert`, and `mtkaif_dmic`; runtime clock code populates `clk`, `lookup`, and syscon pointers.

## Dependencies and Integration Points

It includes ALSA SoC, Linux list/regmap, `mt8186-reg.h`, and the MediaTek base AFE API. Every MT8186 DAI implementation relies on these IDs being stable and matching the DAI-driver arrays, memif metadata, DAPM routes, GPIO selection switch, and IRQ usage table.

## Risks

The single combined enum means inserting a memif or DAI in the middle changes numeric IDs and breaks table indexes unless all arrays are updated. `dai_priv` is a `void *` array, so mismatched IDs or shared private blocks can cause type confusion. State fields are generally not protected by dedicated locks beyond the external ALSA/control paths, so changes should respect existing call contexts.

## Test Signals

Validation should include probing all DAI registration callbacks, checking `afe->num_dai_drivers`, opening each named FE/BE stream, exercising controls that mutate private state, and verifying DAPM routes resolve with the intended DAI IDs. Compiler warnings for missing enum cases in switch statements are useful after adding IDs.
