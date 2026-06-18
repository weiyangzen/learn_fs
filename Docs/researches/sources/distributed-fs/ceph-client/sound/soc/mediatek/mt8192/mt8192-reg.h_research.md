# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-reg.h

## Purpose
This header is the MT8192 AFE register map and bitfield definition layer. It provides symbolic register offsets, shifts, masks, shifted masks, and small register-value enums used by the MT8192 platform, DAI, clock, memory-interface, IRQ, ASRC, MTKAIF, TDM, HDMI, and security code.

## Important APIs, Types, and Definitions
The only C type is the anonymous enum defining `MT8192_MEMIF_PBUF_SIZE_*` values. The rest of the file is preprocessor definitions. Important groups include top-level enable and monitor bits for `AFE_DAC_CON0` and `AFE_DAC_MON`; I2S control fields for `AFE_I2S_CON`, `AFE_I2S_CON1` through `AFE_I2S_CON9`, and `AFE_CONNSYS_I2S_CON`; PCM fields for `PCM_INTF_CON1`, `PCM_INTF_CON2`, and `PCM2_INTF_CON`; ADDA and MTKAIF fields for `AFE_ADDA_*`, `AFE_AUD_PAD_TOP`, `AFE_ADDA_MTKAIF_*`, and `AFE_ADDA6_MTKAIF_*`; memif control fields for DL, VUL, AWB, DAI, MOD_DAI, HDMI, and pbuf format registers; IRQ control/count/status fields for `AFE_IRQ_MCU_*`; ASRC and sinegen fields; and security mask register offsets.

The register-offset section maps symbolic names such as `AFE_DAC_CON0`, `AFE_CONN*`, `AFE_DL*_BASE`, `AFE_VUL*_CUR`, `AFE_IRQ_MCU_CON*`, `AFE_APLL*_TUNER_CFG`, `AFE_TDM_CON*`, `GENERAL_ASRC_*`, and `AFE_SECURE_MASK_*` to byte offsets. `AFE_MAX_REGISTER` is set to `AFE_SECURE_MASK_TINY_CONN7`, and `AFE_IRQ_STATUS_BITS`, `AFE_IRQ_CNT_SHIFT`, and `AFE_IRQ_CNT_MASK` summarize IRQ status/count handling.

## Control Flow
There is no executable control flow. Consumers use these definitions in `regmap_update_bits()`, `regmap_read()`, regmap range/default tables, DAI configuration helpers, interrupt handlers, and PCM/memif setup paths. The naming convention usually provides a raw shift, unshifted mask, and pre-shifted mask, letting callers either compose values manually or use update helpers with explicit masks.

## State and Persistence
This file owns no runtime state. It defines the layout of hardware state in the AFE register block. Runtime state persists only in the hardware registers accessed by other driver files, for example enable bits in `AFE_DAC_CON0`, buffer addresses/cursors for memifs, IRQ counters and clears, MTKAIF protocol/delay/fifo controls, and secure-domain masks.

## Dependencies and Integration Points
The header is included by MT8192 AFE implementation files that need stable names for hardware registers. It must agree with the SoC datasheet, the regmap maximum register, and any debugfs/regcache/default-register tables. It also underpins machine-driver calibration code that touches `AFE_AUD_PAD_TOP` and MTKAIF registers, and PCM/DAI code that configures I2S, PCM, TDM, HDMI, ASRC, and memif paths.

## Risks
The main risks are silent hardware misconfiguration from incorrect offsets, shifts, or masks. Because many names are repeated across similar I2S or memif blocks, copy/paste mistakes can be hard to detect at compile time. Some generic macro names, such as `INV_LRCK_SFT`, appear in multiple register sections and could collide semantically if used without register context. A wrong `AFE_MAX_REGISTER` may make regmap reject valid accesses or allow invalid ones. IRQ masks and clear bits are especially sensitive because stale interrupts can cause underruns or missed period notifications.

## Test Signals
Compile coverage catches missing macro names but not most numeric mistakes. Runtime signals include successful probe with no regmap range errors, working playback and capture on every memif/DAI using these offsets, stable interrupt delivery and period elapsed callbacks, correct I2S/PCM/TDM clock and format behavior across sample rates, successful MTKAIF calibration, no unexpected secure access faults, and register dumps matching expected bit transitions during stream start/stop.
