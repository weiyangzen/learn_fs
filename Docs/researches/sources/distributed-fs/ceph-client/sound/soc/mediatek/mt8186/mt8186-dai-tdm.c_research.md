# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-tdm.c

## Purpose

`mt8186-dai-tdm.c` registers and configures the MT8186 TDM input DAI. It supports 2 to 8 capture channels, I2S/left-justified/right-justified/DSP_A/DSP_B formats, one-pin and multi-pin data modes, master/slave clocking, low-jitter APLL routing, MCLK generation, GPIO pinmux request/release, and ETDM input register programming. The complete 643-line file was read.

## Important APIs, Types, and Functions

The private type is `struct mtk_afe_tdm_priv`, storing id, rate, clock inversion, LRCK width, MCLK id/multiple/rate/APLL, TDM format, data mode, slave mode, and low-jitter enable. Format enums encode hardware values for `TDM_IN_I2S`, `TDM_IN_LJ`, `TDM_IN_RJ`, `TDM_IN_DSP_A`, `TDM_IN_DSP_B`, one-pin/multi-pin data, and clock inversion.

Important helpers are `get_tdm_lrck_width()`, `get_tdm_ch_fixup()`, `get_tdm_ch_per_sdata()`, `mtk_tdm_en_event()`, `mtk_tdm_mck_en_event()`, `mtk_afe_tdm_mclk_connect()`, `mtk_afe_tdm_mclk_apll_connect()`, `mtk_afe_tdm_hd_connect()`, `mtk_afe_tdm_apll_connect()`, `mt8186_tdm_hd_get()`, `mt8186_tdm_hd_set()`, `mtk_dai_tdm_cal_mclk()`, `mtk_dai_tdm_hw_params()`, `mtk_dai_tdm_set_sysclk()`, `mtk_dai_tdm_set_fmt()`, `mtk_dai_tdm_set_tdm_slot()`, `init_tdm_priv_data()`, and public `mt8186_dai_tdm_register()`.

## Control Flow

Registration creates an AFE sub-DAI, attaches the single `TDM IN` DAI, controls, widgets, and routes, then initializes private state with MCLK multiple 512, MCLK id `MT8186_TDM_MCK`, and id `MT8186_DAI_TDM_IN`.

Format setup through `mtk_dai_tdm_set_fmt()` records the hardware format, data mode, bit/frame clock inversion, and master/slave state based on DAIFMT masks. `set_sysclk()` validates input-clock direction and delegates to `mtk_dai_tdm_cal_mclk()`, which selects an APLL by frequency and rejects frequencies that are zero, exceed the APLL rate, or do not divide the APLL rate. `set_tdm_slot()` records slot width in `lrck_width`, although the current `hw_params()` computes LRCK width from format and mode rather than using that field.

`mtk_dai_tdm_hw_params()` records the sample rate, channel count, format width, calculated channel-per-sdata count, LRCK width, transformed sample rates, and MCLK. If no MCLK was set explicitly, it computes `rate * mclk_multiple`. It then programs ETDM registers: `ETDM_IN1_CON0` for enable-independent mode/bit/word/channel settings, `ETDM_IN1_CON1` for LRCK width and MCLK output enable, `ETDM_IN1_CON3` for sample-rate timing, `ETDM_IN1_CON4` for relatch rate and inversion bits, `ETDM_IN1_CON2` for multi-pin mode, and `ETDM_IN1_CON8` for AFIFO use in slave mode.

DAPM power events request/release GPIOs and enable/disable MCLK through MediaTek clock helpers. Route predicates conditionally power low-jitter and MCLK supplies depending on private state.

## State and Persistence Behavior

Runtime state is held in `afe_priv->dai_priv[MT8186_DAI_TDM_IN]`. Low-jitter, format, inversion, slave mode, MCLK, and rate persist across ALSA callbacks until changed or cleared by DAPM MCLK power-down. Hardware state persists in ETDM registers and clock gates while the DAI is active. There is no nonvolatile persistence.

## Dependencies and Integration Points

The file depends on `linux/regmap.h`, `sound/pcm_params.h`, `mt8186-afe-clk.h`, `mt8186-afe-common.h`, `mt8186-afe-gpio.h`, and `mt8186-interconnection.h`. It integrates with AFE clock helpers for APLL/MCLK selection, DAPM supplies `aud_tdm_clk`, `TDM_EN`, `TDM_HD_EN`, and `TDM_MCLK_EN`, and the machine driver's `TDM IN` backend link. Register programming uses ETDM macros from `mt8186-reg.h`.

## Risks and Edge Cases

`get_tdm_id_by_name()` always returns `MT8186_DAI_TDM_IN`, which is fine for the single TDM instance but fragile if a second TDM is added. `mtk_dai_tdm_set_tdm_slot()` stores `lrck_width` but `hw_params()` ignores it, so slot-width requests may not behave as callers expect. In `set_sysclk()`, the error message says `dir != SND_SOC_CLOCK_OUT` while checking for `SND_SOC_CLOCK_IN`. If automatic MCLK calculation fails, `hw_params()` does not check the return from `mtk_dai_tdm_cal_mclk()`. Register writes ignore regmap errors.

## Test Signals

Exercise all DAIFMT formats and inversion combinations, master and slave mode, 2/4/8 channel capture, and both one-pin DSP and multi-pin I2S-like modes. Verify `TDM_HD_Mux` powers the correct APLL, explicit `set_sysclk()` rejects invalid MCLK rates, automatic MCLK is `rate * 512`, GPIO request/release occurs around DAPM power, and ETDM register fields match expected word length, channel count, inversion, AFIFO, and sample-rate transforms.
