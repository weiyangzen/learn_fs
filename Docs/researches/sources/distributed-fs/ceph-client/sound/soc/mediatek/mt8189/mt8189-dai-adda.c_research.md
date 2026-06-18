# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-dai-adda.c

## Purpose

`mt8189-dai-adda.c` implements MT8189 ADDA and AP DMIC backend DAIs. It programs DAC/ADC sample-rate conversion, gain, IIR filters, MTKAIF protocol and phase alignment, AP DMIC source configuration, and PMIC VS1 voting. It also publishes DAPM mixers/routes that connect memory interfaces and internal sources to ADDA playback/capture endpoints.

## Important APIs, Types, And Data

The exported hook is `mt8189_dai_adda_register()`, called from the AFE platform probe. It allocates one `mtk_base_afe_dai`, attaches `mtk_dai_adda_driver[]`, `mtk_adda_controls[]`, `mtk_dai_adda_widgets[]`, and `mtk_dai_adda_routes[]`, initializes private data, and adds the DAI to `afe->sub_dais`.

`struct mtk_afe_adda_priv` stores the last DL and UL rates per ADDA-like DAI. `init_adda_priv_data()` allocates private data for `MT8189_DAI_ADDA` and `MT8189_DAI_ADDA_CH34`; AP DMIC and AP DMIC_CH34 share those state blocks. Rate helpers map ALSA rates to register encodings: `adda_dl_rate_transform()` supports common DL rates through 192 kHz while `adda_ul_rate_transform()` supports 8/16/32/48/96/192 kHz capture.

The DAI array exposes `ADDA`, `ADDA_CH34`, `AP_DMIC`, and `AP_DMIC_CH34`. Controls include raw `ADDA_DL_GAIN`, `MTKAIF_DMIC Switch`, and `ADDA_DL_MAX_VOL Switch`. DAPM widgets include ADDA enable gates, DL/UL clocks, playback/capture source enables, AUD_PAD_TOP, MTKAIF config supplies, AP DMIC supplies, FIFO soft reset supplies, VS1 voter supplies, and muxes for `ADDA_UL_Mux` and `ADDA_CH34_UL_Mux`.

## Control Flow

Playback setup enters `mtk_dai_adda_hw_params()` and `set_playback_hw_params()`. The code builds `AFE_ADDA_DL_SRC_CON0` with DL rate, x8 output mode, unmuted channels, optional voice mode for 8/16 kHz, and gain enable. It builds `AFE_ADDA_DL_SRC_CON1` with the normal -0.3 dB gain value. For the main `ADDA` DAI it clears predistortion registers, writes DL SRC registers, sets SDM attenuation, selects second-order SDM, and enables SDM auto reset with `SDM_AUTO_RESET_THRESHOLD`.

Capture setup enters `set_capture_hw_params()`. It converts the sample rate into UL voice mode, enables IIR in software-selected mode, writes 35 Hz-at-48 kHz IIR coefficients, and programs one of the ADDA UL0, DMIC0, or DMIC1 SRC blocks. For analog MTKAIF capture it forces `AFE_MTKAIF0_RX_CFG0` data mode to AMIC. For AP DMIC capture, it calls `mtk_adda_ul_src_enable_dmic()`, which selects DMIC phases, 3.25 MHz mode, disables low-power mode, enables SDM 3-level and channel modes, and programs UL gain/gain mode.

DAPM events provide power sequencing. `mtk_adda_ul_event()` switches MTKAIF data mode to DMIC and configures the ADDA UL source when the user control has requested MTKAIF DMIC, then delays 120-130 us on power-down and resets the DMIC flags. `mtk_adda_pad_top_event()` writes AUD pad config based on `afe_priv->mtkaif_protocol`. `mtk_adda_mtkaif_cfg_event()` programs protocol 2 / protocol 2 clock phase mode, optionally inverts clocks for calibration, checks selected phase availability, computes MISO delay data/cycle pairs, and updates MTKAIF0/1 delay registers. `mtk_adda_dl_event()` adds the same 120-130 us post-power-down delay for DL.

PMIC VS1 voting is driven by `mt_vs1_voter_dl_event()`, `mt_vs1_voter_ul_event()`, `mt8189_adda_dl_max_vol_set()`, and `mt6363_vs1_vote()`. The vote is asserted when ADDA UL is on or when ADDA DL is on at max volume, and deasserted otherwise by writing the PMIC regmap set/clear registers.

## State And Persistence

State is held in `afe_priv->dai_priv[]`, `afe_priv->mtkaif_dmic`, `afe_priv->mtkaif_dmic_ch34`, `afe_priv->mtkaif_protocol`, MTKAIF phase arrays, and the VS1 voting booleans `is_adda_dl_on`, `is_adda_ul_on`, `is_adda_dl_max_vol`, and `is_mt6363_vote`. These values persist across DAPM events while the component remains bound. Register programming is not self-restoring in this file; platform-level regcache and runtime resume in `mt8189-afe-pcm.c` handle hardware power transitions.

## Dependencies And Integration Points

The file depends on the AFE clock/register headers and the interconnection constants used by mixer controls. It integrates with MTKAIF calibration state in `struct mt8189_afe_private`, PMIC access through `afe_priv->pmic_regmap`, and DAPM routes used by the memif file. It is registered as one of the sub-DAIs aggregated by the main AFE platform driver and selected by the machine driver's BE links and DAPM paths.

## Risks

`mt8189_adda_dmic_set()` sets both `mtkaif_dmic` and `mtkaif_dmic_ch34`, but only `mtkaif_dmic` is read in `mtk_adda_ul_event()` in this file; callers need to verify CH34 behavior through routes and DMIC source events. MTKAIF phase delay programming assumes phase arrays are initialized correctly; negative values skip delay setup. `mt6363_vs1_vote()` silently returns when `pmic_regmap` is absent, so audio may work without the power vote only if board power is otherwise sufficient. Some route controls connect many internal sources into ADDA DL/UL mixers and include duplicated or asymmetric channel options; route validation should match hardware diagrams.

## Test Signals

Test playback at 8/16/48 kHz and capture at 8/16/32/48 kHz on ADDA and AP DMIC, checking for rate transform warnings. Validate `MTKAIF_DMIC Switch`, `ADDA_DL_MAX_VOL Switch`, and VS1 PMIC set/clear writes with regmap tracing. Exercise MTKAIF protocol 2 and phase-delay paths with calibration data populated and absent. DAPM debug should show expected supplies for ADDA playback, analog capture, AP_DMIC, and AP_DMIC_CH34, plus the 120 us shutdown delay before AFE off.
