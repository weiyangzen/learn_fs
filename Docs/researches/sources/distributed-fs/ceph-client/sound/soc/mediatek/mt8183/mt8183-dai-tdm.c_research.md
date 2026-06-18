# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-dai-tdm.c

Purpose: implements the MT8183 TDM playback DAI used primarily for HDMI output, including HDMI channel mux controls, TDM/MCLK/BCK DAPM supplies, format/sysclk handling, channel layout programming, and trigger-time enable.

Important APIs/types/functions: `struct mtk_afe_tdm_priv` stores BCK/MCLK ids/rates, output mode, inversion flags, MCLK multiple, and selected APLL; helper functions derive HDMI word length, TDM word length, BCK cycles, LRCK width, channel grouping, and fixed channel counts; eight HDMI channel DAPM muxes map HDMI output slots to memory channels; TDM clock events call `mt8183_mck_enable/disable`; `mtk_dai_tdm_cal_mclk` validates APLL divisibility; `mtk_dai_tdm_hw_params` computes MCLK/BCK, writes TDM and HDMI output registers; trigger toggles HDMI output and TDM enable; set_sysclk and set_fmt store clock/format policy; register callback allocates private state and registers the DAI/routes/widgets.

Control flow: registration initializes default `mclk_multiple = 128`, BCK id `MT8183_I2S4_BCK`, and MCLK id `MT8183_I2S4_MCK`. Machine BE links set dai_fmt/sysclk as needed. hw_params calculates a default MCLK if not explicitly set, computes BCK from rate/channels/format, writes `AFE_TDM_CON1/2`, HDMI channel count, and bit width. DAPM turns on MCLK and BCK supplies through the clock layer. Trigger start/resume enables HDMI out and TDM; stop/suspend disables both.

State and persistence: per-TDM private state persists in `afe_priv->dai_priv[MT8183_DAI_TDM]`. MCLK rate may persist after explicit sysclk or be reset by DAPM MCK shutdown. TDM/HDMI registers are regcache-managed by the AFE core.

Dependencies and integration: depends on clock helpers, MT8183 register definitions, HDMI memif DAI from `mt8183-afe-pcm.c`, optional HDMI codec machine links, and ALSA DAPM. The Makefile includes it in the aggregate AFE module.

Risks: BCK/MCLK divisibility problems are warnings in hw_params, not hard failures, after default MCLK calculation. Unsupported DAI formats default to I2S instead of returning an error. Channel mapping defaults to zero for invalid channel counts, though the DAI advertises 2-8. Verbose `dev_info` in hot paths can be noisy.

Test signals: HDMI/TDM playback with 2/4/6/8 channels, S16/S24/S32 formats, I2S and DSP_A formats, explicit sysclk and default MCLK paths, APLL family selection, HDMI channel mux controls, and trigger start/stop register state.
