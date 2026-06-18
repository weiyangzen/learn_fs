# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-dai-adda.c

Purpose: implements the MT8183 ADDA DAI for analog playback/capture through the audio codec interface, including DL/UL interconnect mixers, MTKAIF protocol/DMIC setup, ADDA DAPM supplies, and ADDA hw_params register programming.

Important APIs/types/functions: DAPM mixer controls connect DL1/DL2/DL3, ADDA UL, and PCM capture sources to ADDA DL channels; `mtk_adda_ul_event` applies DMIC-specific MTKAIF and UL source settings and delays after power-down; `MTKAIF_DMIC` kcontrol stores `afe_priv->mtkaif_dmic`; ADDA widgets include playback/capture supplies and clocks; `set_mtkaif_rx` programs MTKAIF protocol 1/2/2 clock phase settings; `mtk_dai_adda_hw_params` configures playback SRC/up-sampling/gain/SDM or capture MTKAIF/IIR/voice mode; `mt8183_dai_adda_register` contributes DAI driver, controls, widgets, and routes to the AFE sub-DAI list.

Control flow: registration appends one ADDA DAI to `afe->sub_dais`. During DAPM power-up for capture, DMIC mode may rewrite MTKAIF RX and UL source bits. Playback hw_params clears predistortion, maps rate through common ADDA helpers, chooses upsampling, applies gain, enables DL gain, and sets SDM attenuation. Capture hw_params configures MTKAIF protocol, selects internal ADC, maps UL rate, enables IIR, loads fixed high-pass coefficients, writes UL source config, and defaults to AMIC data mode unless the DAPM DMIC event overrides it.

State and persistence: `mtkaif_dmic`, MTKAIF protocol/calibration fields, and phase-cycle data live in `mt8183_afe_private`. ADDA register state is cached by the AFE regmap and controlled by DAPM supplies. The kcontrol changes persistent per-device capture behavior until changed again.

Dependencies and integration: depends on `mtk-dai-adda-common.h` rate transform helpers, MT8183 register definitions, interconnection indices, regmap, AFE private state, and DAPM routes from memif/I2S/PCM/hostless components.

Risks: some `regmap_update_bits` calls in the DMIC event use a zero mask with nonzero values, which is suspicious and may be no-ops depending on macro expansion. MTKAIF protocol defaults must be initialized elsewhere or the default branch does nothing. Playback gain constants are hardcoded. DMIC mode is user-controlled and can conflict with analog mic expectations.

Test signals: ADDA playback at 8k-192k, ADDA capture at 8/16/32/48k, `MTKAIF_DMIC` toggling, AMIC vs DMIC capture, MTKAIF protocol variants including calibrated phase data, DAPM supply sequencing, and register traces for SRC/IIR/SDM settings.
