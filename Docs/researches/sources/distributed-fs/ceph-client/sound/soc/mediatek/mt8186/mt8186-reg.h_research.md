# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-reg.h

## Purpose

`mt8186-reg.h` is the central MT8186 AFE register definition header. It defines bit shifts, masks, composite helper macros, register offsets, maximum register address, and interrupt status/count masks used by the MT8186 platform, DAI, clock, memory-interface, interrupt, ADDA, ASRC, I2S, PCM, TDM/ETDM, sine-generator, secure, and debug code. The complete 2913-line header was read.

## Important APIs, Types, and Functions

The only type is an enum for memory-interface playback buffer size values: `MT8186_MEMIF_PBUF_SIZE_32_BYTES`, `64_BYTES`, `128_BYTES`, `256_BYTES`, and `MT8186_MEMIF_PBUF_SIZE_NUM`.

There are no functions. Macro groups include power and top control fields (`AUDIO_TOP_CON*`, `PDN_*`), global AFE enable and memory-interface enables (`AFE_DAC_CON0`, `DL*_ON`, `VUL*_ON`, `AUDIO_AFE_ON`), I2S fields (`AFE_I2S_CON*`, `AFE_CONNSYS_I2S_CON`), PCM fields (`PCM_INTF_CON1`, `PCM_INTF_CON2`, `PCM2_INTF_CON`), gain fields (`AFE_GAIN*_CON*`, `GAIN*_TARGET`, `AFE_GAIN*_CUR`), ADDA/MTKAIF fields, sine-generator fields, general ASRC fields (`AFE_GENERAL{1,2}_ASRC_2CH_CON*`, `GENERAL_ASRC_MODE`, `GENERAL_ASRC_EN_ON`), IRQ fields (`AFE_IRQ_MCU_*`), ETDM input fields (`ETDM_IN1_CON0` through `CON8` plus helper macros such as `ETDM_IN_CON3_FS()`), and the full register offset map from `AUDIO_TOP_CON0` through `ETDM_0_3_COWORK_CON3`.

## Control Flow

There is no executable control flow. Other C files use these macros in `regmap_update_bits()`, `regmap_write()`, regmap ranges, interrupt configuration, and DAPM control definitions. Field macros encode hardware layout so runtime control flow in DAI and platform code can assemble register values safely.

## State and Persistence Behavior

The header owns no state. It defines how volatile hardware state is addressed and masked. Persistent behavior is indirect: any incorrect macro can cause driver state to be written to the wrong field or register, affecting audio hardware until reset or reprogramming.

## Dependencies and Integration Points

The header relies on Linux `BIT()` and `GENMASK()` macros being available before use through including headers. It is included via `mt8186-afe-common.h` by the MT8186 DAI files in this work item and by broader MT8186 AFE platform code. It is tightly coupled to the SoC hardware manual and to regmap configuration, DAPM routes, IRQ handling, DMA memory-interface setup, clock gating, ADDA codec interface setup, ASRC coefficient loading, PCM/I2S/TDM programming, and debug/test controls.

## Risks and Edge Cases

This file is hardware ABI. A wrong offset, shift, or mask can corrupt unrelated AFE state, break audio routing, or cause subtle format/rate/clocking failures. Several symbolic names are reused across register contexts, such as generic `I2S_*` fields and `G_SRC_*` fields, so callers must pair them with the correct register. Some masks include both raw masks and shifted masks; using `_MASK` where `_MASK_SFT` is required, or vice versa, would produce wrong regmap operations. Register offset additions must update `AFE_MAX_REGISTER` and regmap access tables elsewhere. Because the header is macro-only, errors are usually caught by runtime audio behavior rather than compiler diagnostics.

## Test Signals

Build coverage catches missing names but not semantic mistakes. Stronger signals include regmap trace comparison against the hardware programming guide, runtime playback/capture across all memory interfaces, I2S/PCM/TDM/SRC/HW gain path tests, interrupt cadence tests using `AFE_IRQ_MCU_*`, sine-generator loopback tests, ASRC coefficient programming tests, and debugfs/regmap dumps confirming expected offsets and field values. Static review should compare changed macro groups against known-good vendor or upstream MT8186 definitions.
