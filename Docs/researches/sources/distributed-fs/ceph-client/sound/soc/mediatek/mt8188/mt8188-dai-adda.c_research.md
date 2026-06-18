# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-dai-adda.c

Purpose: Implements the MT8188 analog/digital audio front-end backend DAIs for ADDA playback (`DL_SRC`) and capture (`UL_SRC`). It handles MTKAIF receive setup, analog uplink DMIC mode, ADDA sample-rate programming, hi-res clock routing, DAPM widgets/routes, and user controls for DL gain and MTKAIF DMIC selection.

Important APIs and functions: `mt8188_dai_adda_register()` adds the ADDA DAI group to `afe->sub_dais`. `mt8188_adda_mtkaif_init()` configures MTKAIF protocol2 and optional calibrated MISO delay. `mtk_adda_dl_event()` and `mtk_adda_ul_event()` handle DAPM power timing and mic type setup. `mtk_afe_adda_hires_connect()` conditionally connects hires clock supplies based on per-DAI `hires_required`. `mtk_dai_adda_hw_params()` records whether the stream is above 48 kHz and calls DA or AD register configuration. `mt8188_adda_dmic_get/set()` exposes MTKAIF DMIC mode.

Control flow: Register allocates two `mtk_dai_adda_priv` objects into `dai_priv[DL_SRC]` and `dai_priv[UL_SRC]`, then exposes widgets/routes/controls. During hw_params, playback configures DL input mode, disables saturation, unmutes channels, handles voice mode for 8/16 kHz, and enables new second SDM. Capture configures UL voice mode. During DAPM capture power-up, MTKAIF configuration and mic-type bits are programmed. Power-down delays 125 us before AFE off.

State and persistence: Per-DAI state is `hires_required`. Shared MTKAIF state in `mt8188_afe_private->mtkaif_params` tracks calibration success, selected phases, phase cycles, and `mtkaif_dmic_on`. Hardware state is in ADDA and pad registers.

Dependencies and integration: Uses MediaTek ADDA common transform helpers, regmap, bitfield helpers, ASoC DAPM/control APIs, and clocks registered as DAPM supplies (`aud_dac`, `aud_adc`, hires variants). Its I/O connects to AFE memif routing through I/O widgets such as `I168/I169`, `O176/O177`, and ADDA input/output endpoints.

Risks: If MTKAIF calibration is not marked OK, the driver silently continues with protocol setup but no delay compensation. `mtk_afe_adda_hires_connect()` relies on widget-name substring matching. DMIC mode is cached and applied only on DAPM UL power-up, so changing the control during an active path may not immediately reprogram hardware. Rate transforms must stay aligned with supported rates.

Test signals: Playback and capture at 48 kHz and 96/192 kHz should toggle normal and hires clock supplies appropriately. Capture tests should cover analog mic and MTKAIF DMIC switch before stream start. Mixer tests should validate `ADDA_DL_GAIN` and route controls. Logs should show no calibration-related errors unless expected.
