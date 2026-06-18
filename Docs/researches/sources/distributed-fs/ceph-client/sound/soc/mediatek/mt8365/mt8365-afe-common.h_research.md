# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-afe-common.h

## Purpose
Shared private definitions for the MT8365 ASoC AFE driver family. It assigns platform-wide IDs for memory interfaces, backend DAIs, IRQs, clocks, top clock gates, sample-rate encodings, MCLKs, channel-merge blocks, ASRC blocks, and data structures used by the platform, clock, ADDA, DMIC, I2S, PCM, and TDM code.

## APIs, Types, and Functions
Important enums define `MT8365_AFE_MEMIF_*`, `MT8365_AFE_IO_*`, `MT8365_AFE_IRQ*`, `MT8365_TOP_CG_*`, `MT8365_CLK_*`, `MT8365_AFE_APLL*`, I2S sets/clocking, TDM output modes, PCM formats, `MT8365_FS_*`, raw `FS_*HZ` encodings, debugfs indices, IRQ directions, MCLK IDs, `enum mt8365_cm_num`, `enum mt8365_cm2_mux_in`, `enum cm2_mux_conn_in`, DMIC modes, IIR modes, and ASRC IDs. Key structures are `mt8365_fe_dai_data`, `mt8365_be_dai_data`, `mt8365_cm_ctrl_reg`, `mt8365_control_data`, `mt8365_gasrc_ctrl_reg`, `mt8365_gasrc_data`, and `mt8365_afe_private`. Inline helpers `rx_frequency_palette()`, `AutoRstThHi()`, and `AutoRstThLo()` map sample-rate codes to ASRC/auto-reset constants. The header also declares the cross-file registration and configuration functions for rate/channel validation, DAI private data, I2S out, ADDA, DMIC, PCM, and TDM.

## Control Flow, State, and Persistence
This header defines the persistent per-device state stored behind `mtk_base_afe.platform_priv`. `mt8365_afe_private` holds clock handles, SRAM mapping, FE SRAM/dma selection state, BE prepared flags, channel-merge controls, GASRC state, AFE-on and clock-gate refcounts, APLL tuner refcounts, selected TDM output mode, selected CM2 mux input, DAI-on flags, and per-DAI private pointers. These fields are mutated by probe, ALSA stream callbacks, DAPM mux controls, clock helpers, suspend/resume backup, and DAI registration paths.

## Dependencies and Integration
Depends on Linux clock/list/regmap headers, ALSA SoC/asound headers, the common MediaTek `mtk-base-afe.h`, and `mt8365-reg.h`. It is the integration boundary across all MT8365 source files: IDs in this header must match DAI driver IDs, memif tables, IRQ tables, top-CG mappings, `dai_priv[]` indexes, and machine-driver routing assumptions.

## Risks and Test Signals
Array-index correctness is the main risk: `be_data[dai->id - MT8365_AFE_BACKEND_BASE]`, `dai_priv[id]`, `top_cg_ref_cnt[cg]`, `clocks[clk]`, and IRQ/memif tables all rely on enum ordering staying synchronized. The `MT8365_AFE_BACKEND_END` and `MT8365_AFE_BACKEND_NUM` arithmetic makes insertions risky. Inline sample-rate tables return zero for unsupported values, which can look like a valid low constant if callers skip validation. Test signals are successful build of all MT8365 objects, probe without out-of-bounds KASAN reports, DAI registration for every ID, stream tests across FE and BE DAIs, DAPM route tests for CM1/CM2 and ASRC muxes, and suspend/resume with state restored.
