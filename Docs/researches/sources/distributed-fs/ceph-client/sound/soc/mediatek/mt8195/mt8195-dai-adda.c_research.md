# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-dai-adda.c

## Purpose
Implements MT8195 ADDA DAIs for analog playback and capture paths through MT6359/MTKAIF. It provides DL_SRC playback, UL_SRC1 capture, and UL_SRC2/ADDA6 capture DAIs, DAPM routing, MTKAIF setup, digital mic and ADDA6-only controls, high-resolution clock switching, and sample-rate programming for ADDA DL/UL source blocks.

## Important APIs, Types, and Functions
`mt8195_dai_adda_register()` registers the sub-DAI descriptor with the AFE core. Runtime DAI programming is handled by `mtk_dai_adda_hw_params()`, `mtk_dai_da_configure()`, and `mtk_dai_ad_configure()`. MTKAIF setup lives in `mt8195_adda_mtkaif_init()` and DAPM callbacks `mtk_adda_mtkaif_cfg_event()`, `mtk_adda_ul_event()`, and `mtk_adda6_ul_event()`. Playback power delay is handled by `mtk_adda_dl_event()`. Hires clock parent switching uses `mtk_audio_hires_event()` and conditional DAPM route callback `mtk_afe_adda_hires_connect()`.

Controls include `ADDA_DL_Gain`, `MTKAIF_DMIC`, and `MTKAIF_ADDA6_ONLY`. `struct mtk_dai_adda_priv` stores `hires_required` per ADDA DAI. The DAI table exposes `DL_SRC`, `UL_SRC1`, and `UL_SRC2` with S16/S24/S32 formats and rate masks up to 192 kHz.

## Control Flow
Registration allocates a `mtk_base_afe_dai`, attaches ADDA DAI drivers, widgets, routes, controls, and allocates private data for DL_SRC, UL_SRC1, and UL_SRC2. During `hw_params`, the driver validates the DAI id, marks `hires_required` when rate exceeds 48 kHz, then programs either playback or capture. Playback sets DL source input mode via common ADDA rate transform, disables saturation, unmutes channels, enables voice mode for 8/16 kHz, and enables new second SDM. Capture writes UL voice mode into either ADDA or ADDA6 UL source registers.

DAPM powers the graph through ordered supplies: ADDA enable, playback/capture enable, MTKAIF config, and optional hires clock. MTKAIF init sets protocol-2 and clock inversion bits on ADDA/ADDA6 and AUD_PAD_TOP, then if machine-driver calibration succeeded, writes delay data/cycle values for MISO channel alignment. Capture PRE_PMU chooses analog or digital mic mode and, for ADDA6-only, disables sync word 2 as needed. POST_PMD callbacks delay about 125 us before AFE off.

## State and Persistence
Per-DAI `hires_required` persists across params and is consumed by DAPM route connection checks. MTKAIF calibration fields, `mtkaif_dmic_on`, and `mtkaif_adda6_only` live in `afe_priv->mtkaif_params`, normally filled by the machine driver. Mixer route and gain state lives in ASoC DAPM/control state and AFE registers. Hires clock parent changes persist until DAPM power-down restores `top_audio_h_sel` to 26 MHz.

## Dependencies and Integration Points
Depends on MT8195 clock helpers, register definitions, common ADDA rate transform helpers, ALSA SoC DAI/DAPM/control APIs, and `struct mtkaif_param` in MT8195 private data. It integrates with the machine driver through `mt8195_mt6359_mtkaif_calibration()` and MT6359 codec setup. Its DAPM endpoints connect to memif I/O widgets (`I000`, `I020`, `I070`, etc.) and card routes for `ADDA_INPUT`/`ADDA_OUTPUT`.

## Risks
MTKAIF delay programming is skipped but not failed when calibration is unavailable, so systems may probe while capture timing is marginal. Many register writes ignore return status. `hires_required` is per-DAI state updated only at `hw_params`; route decisions during DAPM must see a current value. The 125 us shutdown delay is timing-sensitive. The ADDA6-only and DMIC controls directly mutate shared MTKAIF parameters and require userspace/board policy to avoid inconsistent capture setup.

## Test Signals
Signals include successful DL_SRC playback and UL_SRC1/UL_SRC2 capture, MTKAIF calibration logs and stable capture from all MISO paths, toggling `MTKAIF_DMIC` and `MTKAIF_ADDA6_ONLY`, route activation of hires clocks above 48 kHz, correct ADDA gain register behavior, no pops or truncation during POST_PMD delay, and capture/playback tests at 8/16/48/96/192 kHz.
