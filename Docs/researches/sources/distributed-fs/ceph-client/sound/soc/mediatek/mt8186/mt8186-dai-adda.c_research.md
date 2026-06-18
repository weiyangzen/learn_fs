# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-adda.c

## Purpose

`mt8186-dai-adda.c` implements the MT8186 ADDA and AP-DMIC DAI block. It defines DAPM controls/routes for analog/digital playback and capture, handles MTKAIF and DMIC setup, programs ADDA sample-rate/filter/SDM registers in hw_params, and registers the ADDA/AP_DMIC DAI drivers.

## Important APIs, Types, and Functions

`struct mtk_afe_adda_priv` stores current playback and capture rates, used by hi-res DAPM route predicates. `mtk_adda_dl_ch1_mix[]` and `mtk_adda_dl_ch2_mix[]` route DL memifs, ADDA UL loopback, gain, PCM capture, and SRC outputs into ADDA playback channels. `mtk_adda_ul_src_dmic()` configures DMIC mode and channel enable bits. DAPM event handlers manage GPIOs, MTKAIF protocol selection, pad top settings, calibration-based delay programming, and ADDA playback/capture pin enable/disable.

Controls include `ADDA_DL_GAIN` and `MTKAIF_DMIC Switch`; the latter persists in `afe_priv->mtkaif_dmic`. DAPM widgets include ADDA playback/capture supplies, AUD_PAD_TOP, ADDA_MTKAIF_CFG, AP_DMIC_EN, ADDA_FIFO, ADDA_UL_Mux, AP_DMIC input, and ADC/DAC clock supplies. Hi-res route predicates enable `aud_dac_hires_clk` or `aud_adc_hires_clk` only above 48 kHz.

`mtk_dai_adda_hw_params()` programs downlink input mode, upsampling, mute/gain, voice mode, predistortion reset, SDM gain/dither/auto-reset, uplink voice mode, IIR coefficients, internal ADC selection, MTKAIF RX data mode, and AP-DMIC source config. `mt8186_dai_adda_register()` adds the DAI group, controls, widgets, and routes, allocates ADDA private data, and shares that private data with AP_DMIC.

## Control Flow and State

Registration runs during AFE probe via `dai_register_cbs[]`. At stream setup, ALSA calls `hw_params()` and updates ADDA registers according to stream direction and DAI ID. DAPM powers routes and invokes event handlers around playback/capture supplies. Persistent state includes ADDA rates, MTKAIF DMIC/protocol/calibration fields in `mt8186_afe_private`, and shared ADDA/AP_DMIC private data.

## Dependencies and Integration Points

The file depends on regmap, delays, clock helpers, GPIO helpers, MT8186 interconnection IDs, common AFE definitions, and MediaTek ADDA common rate-transform helpers. It integrates with DAPM routes from memif, I2S, PCM, SRC, gain, and hostless DAIs.

## Risks

MTKAIF protocol-2 clock-phase handling relies on calibration fields being populated; missing phases log errors and skip delay programming. ADDA and AP_DMIC share one private block, so rate state can reflect the most recent stream on either DAI. GPIO requests are not fatal in DAPM event handlers; pinctrl failures can leave routes powered without pins active. Register programming uses many literal values and SoC-specific bitfields, so hardware revisions need careful audit.

## Test Signals

Exercise ADDA playback and capture at 8/16/48/96/192 kHz, AP_DMIC capture, MTKAIF DMIC switch transitions, hi-res route activation above 48 kHz, suspend/resume around active ADDA paths, and hostless loopback routes feeding ADDA. Regmap traces should show expected ADDA/MTKAIF/SDM/IIR writes during hw_params and DAPM power-up.
