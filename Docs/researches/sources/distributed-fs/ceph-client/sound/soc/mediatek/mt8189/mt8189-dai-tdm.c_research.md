# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-dai-tdm.c

## Purpose

`mt8189-dai-tdm.c` implements MT8189 TDM and DisplayPort transmitter (`TDM_DPTX`) playback backend DAIs. It configures TDM word/channel timing, HDMI output channel mapping, DPTX channel format, MCLK/BCK clocks, and DAPM routes that select between normal TDM output and DPTX output.

## Important APIs, Types, And Data

The exported registration hook is `mt8189_dai_tdm_register()`. It registers two playback-only DAIs, `TDM` and `TDM_DPTX`, both supporting 2-8 channels, S16/S24/S32 formats, and rates from 8 kHz through 192 kHz including 88.2/96/176.4 kHz. DAI ops are `mtk_dai_tdm_ops`, with hw_params, trigger, and set_sysclk.

`struct mtk_afe_tdm_priv` stores BCK ID/rate, MCLK ID/multiple/rate/APLL. Normal TDM defaults to 128fs MCLK; DPTX defaults to 256fs. Both use `MT8189_TDMOUT_BCK` and `MT8189_TDMOUT_MCK`. Helper functions translate ALSA params into register encodings: `get_tdm_wlen()`, `get_tdm_channel_bck()`, `get_tdm_lrck_width()`, `get_tdm_ch()`, `get_dptx_ch_enable_mask()`, `get_dptx_ch()`, and `get_dptx_wlen()`.

Controls include eight HDMI channel mux controls backed by `AFE_HDMI_CONN0`, letting each HDMI output slot select CH0-CH7. DAPM widgets include a `TDM Playback Route` demux with `NONE`, `TDMOUT`, and `DPTXOUT`, BCK/MCK supplies for normal and DPTX paths, and the TDM clock gate.

## Control Flow

Registration allocates one DAI descriptor and two private state blocks, installs controls/widgets/routes, adds the DAI to `afe->sub_dais`, and stores the private blocks in `afe_priv->dai_priv[MT8189_DAI_TDM]` and `[MT8189_DAI_TDM_DPTX]`.

`mtk_dai_tdm_hw_params()` validates the DAI ID, obtains private state, calculates MCLK if not explicitly set, then calculates BCK as `rate * channels * physical_width`. It rejects BCK rates above MCLK or MCLK rates not divisible by BCK. It writes `AFE_TDM_CON1` for left alignment, word length, channel count group, channel BCK cycles, and LRCK width. For DPTX it also programs `AFE_DPTX_CON` channel enable mask, channel number mode, and 16/24-bit format. It then maps channel pairs into `AFE_TDM_CON2`: 2 channels use O30/O31 only, 4 channels add O32/O33, 6 add O34/O35, and 8 add O36/O37. Finally it updates `AFE_HDMI_OUT_CON0` with channel count.

`mtk_dai_tdm_trigger()` enables HDMI output, optional DPTX, and TDM on start/resume, then disables them in reverse on stop/suspend. `mtk_dai_tdm_set_sysclk()` validates output-clock direction and delegates to `mtk_dai_tdm_cal_mclk()`, which selects an APLL by requested frequency and requires exact divisibility. DAPM events `mtk_tdm_bck_en_event()` and `mtk_tdm_mck_en_event()` enable/disable MCK gates at the stored rates, and `mtk_afe_tdm_apll_connect()` routes MCLK supplies to the chosen APLL.

## State And Persistence

Per-DAI private state stores the calculated or requested MCLK, selected APLL, and BCK rate. `mtk_tdm_mck_en_event()` resets `mclk_rate` to zero on power down, causing a later hw_params to recalculate default MCLK unless set_sysclk is called again. Hardware register state is restored through the parent AFE regmap/runtime PM flow.

## Dependencies And Integration Points

The file depends on MT8189 clock helpers for APLL selection/rates and MCK enable/disable, AFE register macros for TDM/HDMI/DPTX fields, and ASoC DAPM route predicates. The main AFE file assigns HDMI memif to custom IRQ31 and defines HDMI memif registers; the machine driver's `TDM_DPTX_BE` sets 256fs sysclk and forces backend format to S32_LE before reaching this DAI.

## Risks

Default MCLK calculation ignores the return value from `mtk_dai_tdm_cal_mclk()`; a non-divisible default might leave stale or invalid `mclk_apll` state before later BCK checks. `get_tdm_lrck_width()` subtracts one from physical width and assumes nonzero format width. `get_dptx_ch()` treats any channel count except exactly two as 8-channel mode; 4- and 6-channel DPTX rely on the enable mask to limit active channels. Trigger enables HDMI output before TDM/DPTX and disables HDMI last; hardware sequencing should be validated against the HDMI/DPTX block requirements.

## Test Signals

Test 2/4/6/8-channel playback at S16/S24/S32 and common HDMI/DP rates, including explicit set_sysclk and default MCLK paths. Negative tests should request non-divisible sysclk or BCK/MCLK combinations and expect `-EINVAL`. Regmap traces should show `AFE_TDM_CON1`, `AFE_TDM_CON2`, `AFE_HDMI_OUT_CON0`, and `AFE_DPTX_CON` values matching channel/format selection. DAPM should route either `TDMOUT` or `DPTXOUT`, select the correct APLL, and enable BCK/MCK supplies in order.
