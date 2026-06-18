# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-reg.h

Purpose: Provides the MT8365 AFE register map and bit-field definitions used by the MT8365 ASoC platform drivers. It is the hardware ABI for top clock gates, memifs, interconnect matrices, I2S/PCM/DMIC/TDM/SPDIF/ASRC blocks, IRQ counters, ADDA controls, secure masks, and gain/control-monitor blocks.

Important APIs and definitions: The header defines register offsets from `AUDIO_TOP_CON0` through `AFE_SECURE_MASK_CONN27`, with `MAX_REGISTER` set to the final secure mask register. Important bit groups include `AUD_TCON*_PDN_*` power-down controls, `AFE_I2S_CON*` format/rate/enable fields, `AFE_ASRC_2CH_CON*` coefficient SRAM and calibration controls, `AFE_ADDA_*` sample-rate and ADDA enable fields, `PCM_INTF_CON1_*` PCM mode fields, `DMIC_TOP_CON_*` capture filter and channel fields, `AFE_CONN_24BIT_*` output width controls, `AFE_GAIN1_*`, and CM1/CM2 channel-mixer fields.

Control flow: This header has no executable flow, but it drives every `regmap_update_bits()`, `FIELD_PREP()`, and register-write sequence in the MT8365 AFE implementation. Its masks determine which hardware bits are preserved or overwritten during DAI prepare/shutdown, memif setup, DMIC setup, ASRC programming, and clock-gate management.

State and persistence: All definitions represent hardware registers whose values persist in the AFE block until modified, powered down, or reset. The header also models 64-bit DMA address support with base/end/current MSB registers for multiple memifs. `MAX_REGISTER` bounds regmap access.

Dependencies and integration points: Includes `linux/bitfield.h` and is consumed by MT8365 AFE common code, DAI drivers, memory-interface code, clock code, and machine integration. It aligns with register offsets documented for the MT8365 audio block and must match device-tree reg ranges and regmap stride.

Risks: Incorrect offsets or masks cause silent hardware misprogramming. Several macros encode zero-valued modes such as `PCM_INTF_CON1_MASTER_MODE` or `AFE_I2S_CON1_TDMOUT_TO_PAD`; they are meaningful only when paired with masks. Wide masks such as `PCM_INTF_CON1_CONFIG_MASK` and `DMIC_TOP_CON_CONFIG_MASK` require careful review when new bits are added. `MAX_REGISTER` must remain synchronized with the largest valid offset.

Test signals: Compile coverage for all MT8365 sound drivers, regmap debugfs register dumps, successful I2S/PCM/DMIC/ADDA playback and capture, IRQ counter behavior, 24-bit route setup through `AFE_CONN_24BIT`, and ASRC coefficient writes to `AFE_ASRC_2CH_CON12/13`.
