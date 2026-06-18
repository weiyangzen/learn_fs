# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-afe-clk.c

## Purpose
Clock and top clock-gate control layer for the MT8365 AFE platform driver. It centralizes devicetree clock lookup, common AFE-on sequencing, top clock-gate reference counting, and APLL tuner/engineering-clock setup used by MT8365 DAI implementations.

## APIs, Types, and Functions
Public functions include `mt8365_afe_init_audio_clk()`, `mt8365_afe_disable_clk()`, `mt8365_afe_set_clk_rate()`, `mt8365_afe_set_clk_parent()`, `mt8365_afe_enable_top_cg()`, `mt8365_afe_disable_top_cg()`, `mt8365_afe_enable_main_clk()`, `mt8365_afe_disable_main_clk()`, `mt8365_afe_emi_clk_on()`, `mt8365_afe_emi_clk_off()`, `mt8365_afe_enable_afe_on()`, `mt8365_afe_disable_afe_on()`, `mt8365_afe_enable_apll_tuner_cfg()`, `mt8365_afe_disable_apll_tuner_cfg()`, `mt8365_afe_enable_apll_associated_cfg()`, and `mt8365_afe_disable_apll_associated_cfg()`. Internal helpers map `MT8365_TOP_CG_*` IDs to `AUDIO_TOP_CON0/1` registers and masks, and set or clear HD engine bits in `AFE_HD_ENGEN_ENABLE`.

## Control Flow, State, and Persistence
Probe calls `mt8365_afe_init_audio_clk()` to fill `mt8365_afe_private.clocks[]` from named clocks. Runtime users call `mt8365_afe_enable_main_clk()`, which prepares `top_audio_sel`, ungates `MT8365_TOP_CG_AFE`, and asserts `AFE_DAC_CON0` bit 0 through `mt8365_afe_enable_afe_on()`. Matching disable paths decrement reference counters and only write hardware when the counter reaches zero. Top clock gates are protected by `afe_ctrl_lock`; APLL tuner counters are protected by `afe_clk_mutex`. APLL-associated enable turns on ENGEN1/2, 22M/24M gates, HD engine bits, tuner top gates, and tuner configuration registers; disable unwinds the sequence.

## Dependencies and Integration
Depends on Linux `clk`, regmap, `struct mtk_base_afe`, MT8365 register definitions, and `struct mt8365_afe_private` from `mt8365-afe-common.h`. All MT8365 sub-DAIs use this layer for startup/shutdown power windows. The platform probe also uses it to set the `top_audio_sel` parent to the 26 MHz clock and to keep AFE registers accessible for DAPM registration.

## Risks and Test Signals
Several clock and regmap operations ignore return codes, and underflow recovery only clamps counters after decrement, so mismatched enable/disable paths can hide sequencing bugs. `get_top_cg_reg()` and `get_top_cg_mask()` return zero for invalid IDs, which could accidentally target `AUDIO_TOP_CON0` with a zero mask. `mt8365_afe_emi_clk_on/off()` are stubs even though PCM DMA fallback calls them. The HD engine disable writes `~AFE_22M_PLL_EN` or `~AFE_24M_PLL_EN` as the value under a one-bit mask, which relies on masked update semantics. Test signals are balanced refcounts under concurrent streams, clean suspend/resume after active streams, clock-tree debugfs showing expected parents/rates, APLL1/APLL2 playback at 44.1k/48k families, and no register access faults when DAPM reads controls while runtime PM is active.
