# subset-b-006520 Research

Grouped source research for MediaTek MT8186 ASoC DAI drivers, machine-card helpers, register and interconnection definitions, plus the MT8188 ASoC Makefile. Each listed source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-hw-gain.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-hw-gain.c

## Purpose

`mt8186-dai-hw-gain.c` registers the MT8186 hardware gain DAI endpoints with the MediaTek AFE core. It exposes two stereo gain blocks, routes their inputs and outputs through the AFE interconnection matrix, provides ALSA mixer controls for target gain, and programs gain rate/step registers during `hw_params`. The complete 236-line file was read for this report.

## Important APIs, Types, and Functions

The exported registration entry point is `mt8186_dai_hw_gain_register(struct mtk_base_afe *afe)`, which allocates an `mtk_base_afe_dai`, appends it to `afe->sub_dais`, and attaches the DAI driver array, kcontrols, DAPM widgets, and routes.

Important static objects are `mtk_dai_gain_driver[]`, `mtk_dai_gain_ops`, `mtk_hw_gain_controls[]`, `mtk_dai_hw_gain_widgets[]`, and `mtk_dai_hw_gain_routes[]`. The gain volume controls are `SOC_SINGLE("HW Gain 1 Volume", AFE_GAIN1_CON1, ...)` and `SOC_SINGLE("HW Gain 2 Volume", AFE_GAIN2_CON1, ...)`. The two runtime functions are `mtk_hw_gain_event()` and `mtk_dai_gain_hw_params()`.

## Control Flow

Probe-time flow enters through `mt8186_dai_hw_gain_register()`, which only registers metadata with the parent AFE component. Stream setup calls `mtk_dai_gain_hw_params()`: it reads `params_rate()`, converts the rate with `mt8186_rate_transform()`, and writes the appropriate gain mode to either `AFE_GAIN1_CON0` or `AFE_GAIN2_CON0`. It also sets `GAIN1_SAMPLE_PER_STEP` style timing, using `0x40` for gain block 1 and `0x0` for gain block 2.

DAPM power-up flow calls `mtk_hw_gain_event()` on `SND_SOC_DAPM_PRE_PMU`. The callback selects gain block 1 or 2 by comparing the widget name against `HW_GAIN_1_EN_W_NAME`, clears the current gain register, and clears the target gain field so hardware ramps from zero when enabled.

## State and Persistence Behavior

There is no file-backed persistence. The only lasting state is hardware register state in the AFE regmap and ALSA control values stored by the component framework. DAPM supply state gates `GAIN1_ON_SFT` or `GAIN2_ON_SFT`, and `hw_params` persists rate/step configuration until the DAI is reconfigured or powered down by a later path.

## Dependencies and Integration Points

This file depends on `linux/regmap.h`, `mt8186-afe-common.h`, and `mt8186-interconnection.h`. It integrates with the ASoC DAPM graph through `SOC_DAPM_SINGLE_AUTODISABLE`, `SND_SOC_DAPM_MIXER`, `SND_SOC_DAPM_SUPPLY`, and the DAI driver table. Route input selectors use interconnection IDs such as `I_CONNSYS_I2S_CH1`, `I_ADDA_UL_CH1`, and `I_GAIN*` outputs. Register and bit macros come from `mt8186-reg.h` through the AFE common header.

## Risks and Edge Cases

The event callback assumes any non-HW Gain 1 widget is HW Gain 2; a mismatched widget name would write gain2 registers. The `GAIN1_*` mask and shift names are reused for gain2 sample-per-step writes, which relies on identical field layout. Unsupported rates depend on `mt8186_rate_transform()` behavior; this file does not reject a zero or invalid transformed mode. Register writes are not checked for regmap errors.

## Test Signals

Useful signals are successful kernel build with `CONFIG_SND_SOC_MT8186`, ASoC card probe logs showing `HW Gain 1` and `HW Gain 2` DAIs, `amixer` visibility and update behavior for both volume controls, DAPM route activation from CONNSYS/ADDA inputs to gain outputs, and regmap traces confirming `AFE_GAIN*_CON0`, `AFE_GAIN*_CON1`, and `AFE_GAIN*_CUR` writes during stream startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-hw-gain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-i2s.c

## Purpose

`mt8186-dai-i2s.c` implements the MT8186 I2S and CONNSYS I2S ASoC DAI registration and runtime configuration. It provides four main I2S CPU DAIs, a capture-only CONNSYS I2S path with ASRC calibration, low-jitter and MCLK controls, DAPM route predicates for APLL and shared-clock dependencies, GPIO request hooks, and the exported helper used by the machine driver to share one I2S clock with another. The complete 1231-line file was read.

## Important APIs, Types, and Functions

The central private state is `struct mtk_afe_i2s_priv`, holding DAI id, active sample rate, low-jitter flag, master flag, shared I2S id, MCLK id/rate, and selected APLL. Public entry points are `mt8186_dai_i2s_register(struct mtk_base_afe *afe)` and exported `mt8186_dai_i2s_set_share(struct mtk_base_afe *afe, const char *main_i2s_name, const char *secondary_i2s_name)`.

Important helpers include `get_i2s_wlen()`, `get_i2s_id_by_name()`, `get_i2s_priv_by_name()`, `mt8186_i2s_hd_get()`, `mt8186_i2s_hd_set()`, `mtk_i2s_en_event()`, `mtk_apll_event()`, `mtk_mclk_en_event()`, `mtk_afe_i2s_share_connect()`, `mtk_afe_i2s_hd_connect()`, `mtk_afe_i2s_apll_connect()`, `mtk_afe_i2s_mclk_connect()`, `mtk_afe_mclk_apll_connect()`, `mtk_dai_connsys_i2s_hw_params()`, `mtk_dai_connsys_i2s_trigger()`, `mtk_dai_i2s_config()`, `mtk_dai_i2s_hw_params()`, `mtk_dai_i2s_set_sysclk()`, and `mt8186_dai_i2s_set_priv()`.

## Control Flow

Registration allocates an AFE sub-DAI container, attaches `mtk_dai_i2s_driver[]`, controls, widgets, and routes, then initializes per-I2S private data by copying `mt8186_i2s_priv[]` into `afe_priv->dai_priv` via `mt8186_dai_set_priv()`.

Normal I2S stream setup calls `mtk_dai_i2s_hw_params()`, which delegates to `mtk_dai_i2s_config()`. That function stores the selected sample rate in private state, derives the hardware rate mode with `mt8186_rate_transform()`, maps PCM format to 16-bit or 32-bit word length, and updates the correct I2S register: `AFE_I2S_CON` for I2S0, `AFE_I2S_CON1` for I2S1, `AFE_I2S_CON2` for I2S2, or `AFE_I2S_CON3` for I2S3. If `share_i2s_id` is set, it recursively configures the source I2S with the same parameters.

CONNSYS I2S has separate ops. `mtk_dai_connsys_i2s_hw_params()` programs `AFE_CONNSYS_I2S_CON`, enables ASRC use, writes mode-dependent ASRC frequency settings, and programs fixed calibration registers. `mtk_dai_connsys_i2s_trigger()` enables or disables I2S, ASRC, and calibration on PCM trigger start/resume or stop/suspend and updates `afe_priv->dai_on[dai->id]`.

DAPM power sequencing uses supplies for I2S enable, low-jitter enable, MCLK enable, and APLL enable. Route predicates decide whether a supply should connect based on current low-jitter state, shared-clock state, MCLK rate, and the APLL selected from the stream or MCLK frequency.

## State and Persistence Behavior

State is held in `afe_priv->dai_priv[MT8186_DAI_I2S_*]` and `afe_priv->dai_on[MT8186_DAI_CONNSYS_I2S]`. Low-jitter control changes `low_jitter_en`; `set_sysclk()` records `mclk_rate` and `mclk_apll`; `hw_params()` records `rate`; `mt8186_dai_i2s_set_share()` records `share_i2s_id`. DAPM power-down of MCLK clears `mclk_rate`. All hardware state is volatile regmap state and clock/GPIO state; no persistent storage exists.

## Dependencies and Integration Points

The file depends on `linux/bitops.h`, `linux/regmap.h`, `sound/pcm_params.h`, `mt8186-afe-clk.h`, `mt8186-afe-common.h`, `mt8186-afe-gpio.h`, and `mt8186-interconnection.h`. It integrates with AFE clock helpers (`mt8186_apll*_enable()`, `mt8186_get_apll_by_rate()`, `mt8186_get_apll_rate()`, `mt8186_mck_enable()`), GPIO pinmux requests (`mt8186_afe_gpio_request()`), machine drivers through exported `mt8186_dai_i2s_set_share()`, and ASoC DAPM through many route predicates. DAI stream names are consumed by machine links such as `I2S0`, `I2S1`, `I2S2`, `I2S3`, and `CONNSYS_I2S`.

## Risks and Edge Cases

Name-based lookup is fragile: route predicates and controls infer ids from the first four characters of widget/control names. Recursive shared-I2S configuration can re-enter another DAI's config path; the current code only supports one-level share semantics and does not guard cycles. `mtk_dai_i2s_set_sysclk()` rejects non-output clocks and frequencies not dividing the selected APLL, but it only propagates MCLK settings when `share_i2s_id > 0`, so sharing with I2S0 as id 0 is not propagated by that condition. CONNSYS ASRC uses fixed magic calibration constants and only special-cases 44.1 kHz and 32 kHz before defaulting to 48 kHz. Regmap update errors are ignored.

## Test Signals

Test by probing an MT8186 sound card and confirming all five DAIs register. Exercise I2S0/I2S2 capture and I2S1/I2S3 playback at 16/24/32-bit physical formats and rates from 8 kHz through 192 kHz. Toggle `I2S*_HD_Mux` controls and verify APLL routes only power for low-jitter paths. Set MCLK from a machine driver and confirm `mt8186_mck_enable()` receives the expected MCLK id and rate. For shared clocks, validate headset and HDMI machine init paths using `mt8186_dai_i2s_set_share()` and inspect DAPM route activation. For CONNSYS I2S, trigger start/stop and check ASRC, calibration, and bypass bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-pcm.c

## Purpose

`mt8186-dai-pcm.c` registers and configures the MT8186 PCM 1 DAI, used primarily for Bluetooth SCO style PCM/I2S connectivity. It defines the PCM format/private-state model, DAPM mixers and loopback muxes, GPIO power events, register programming for `PCM_INTF_CON1`, and the single `PCM 1` DAI driver. The complete 419-line file was read.

## Important APIs, Types, and Functions

The private type is `struct mtk_afe_pcm_priv`, containing id, PCM format, bit-clock inversion, and frame-clock inversion. Configuration enums encode register values for TX channel repeat, VBT 16 kHz mode, external modem select, sync type, BT mode, AFIFO source, clock master/slave, word length, 24-bit mode, PCM mode, format, and clock inversion.

Key functions are `mtk_pcm_en_event()`, `mtk_dai_pcm_hw_params()`, `mtk_dai_pcm_set_fmt()`, `init_pcm_priv_data()`, and public `mt8186_dai_pcm_register(struct mtk_base_afe *afe)`. Important data objects include `mtk_dai_pcm_widgets[]`, `mtk_dai_pcm_routes[]`, `mtk_dai_pcm_driver[]`, and `mtk_dai_pcm_ops`.

## Control Flow

During registration, the driver allocates an AFE sub-DAI record, adds it to `afe->sub_dais`, attaches the PCM DAI driver and DAPM topology, allocates private state, initializes it to I2S format with non-inverted clocks, and stores it at `afe_priv->dai_priv[MT8186_DAI_PCM]`.

`mtk_dai_pcm_set_fmt()` is called by the ASoC core from machine-link format settings. It maps `SND_SOC_DAIFMT_I2S`, `LEFT_J`, `DSP_A`, and `DSP_B` onto internal PCM format values, then maps the inversion mask onto bit-clock and frame-clock inversion flags.

`mtk_dai_pcm_hw_params()` checks the playback and capture DAPM widgets; if either is already active it returns without reprogramming the shared PCM interface. Otherwise it builds `pcm_con`, sets external modem and master mode defaults, inserts rate mode from `mt8186_rate_transform()`, inserts previously selected format and inversion flags, derives 16/24-bit and 32/64-BCK-cycle word settings from the requested PCM format, and writes all non-enable bits to `PCM_INTF_CON1` using mask `0xfffffffe`.

DAPM supply event `mtk_pcm_en_event()` requests or releases PCM GPIO configuration on power up/down.

## State and Persistence Behavior

Runtime state lives in `struct mtk_afe_pcm_priv` under `afe_priv->dai_priv`. It persists between `set_fmt()` and `hw_params()` so machine-link format choices can be applied when hardware params arrive. Hardware register state is volatile in `PCM_INTF_CON1`, plus DAPM power state for `PCM_EN_SFT`. No filesystem or firmware persistence is used.

## Dependencies and Integration Points

The file depends on `linux/regmap.h`, `sound/pcm_params.h`, `mt8186-afe-common.h`, `mt8186-afe-gpio.h`, and `mt8186-interconnection.h`. Its DAPM routes connect `DL2`, `DL4`, I2S loopback paths, `I2S0`, and `I2S3`. Machine-card integration appears in the MT6366 card where the `PCM 1` backend is connected to the `bt-sco` codec with I2S/NB_IF format.

## Risks and Edge Cases

The shared interface is not reprogrammed if either playback or capture widget is active, so late format/rate changes while the opposite direction is active are ignored. Unsupported DAIFMT values silently default to I2S or non-inverted clocks rather than returning an error. `mt8186_rate_transform()` output is not validated locally. The register mask intentionally avoids bit 0 so DAPM controls enable state, but accidental field additions in `PCM_INTF_CON1` could be missed if the hard-coded mask is not updated.

## Test Signals

Build coverage should include `CONFIG_SND_SOC_MT8186`. Runtime tests should confirm `PCM 1` playback/capture appears, GPIO requests occur on DAPM power changes, BT SCO backend opens at 8/16/32/48 kHz as advertised, DAIFMT changes alter `PCM_FMT`, `PCM_SYNC_OUT_INV`, and `PCM_BCLK_OUT_INV`, and loopback muxes route PCM in/out to I2S widgets as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-src.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-src.c

## Purpose

`mt8186-dai-src.c` implements two MT8186 hardware sample-rate-converter DAIs, `HW_SRC_1` and `HW_SRC_2`. It manages downlink/uplink rate state, programs general ASRC frequency registers, loads IIR coefficient SRAM for downsampling cases, gates ASRC blocks through DAPM, and exposes DAI routes between DL/I2S/gain sources and SRC outputs. The complete 695-line file was read.

## Important APIs, Types, and Functions

The private type is `struct mtk_afe_src_priv` with `dl_rate` and `ul_rate`. Coefficient tables include `src_iir_coeff_32_to_16`, `src_iir_coeff_44_to_16`, `src_iir_coeff_44_to_32`, `src_iir_coeff_48_to_16`, `src_iir_coeff_48_to_32`, `src_iir_coeff_48_to_44`, `src_iir_coeff_96_to_16`, and `src_iir_coeff_96_to_44`.

Important functions are `mtk_get_src_freq_mode()`, `get_iir_coeff()`, `mtk_set_src_1_param()`, `mtk_set_src_2_param()`, `mtk_hw_src_event()`, `mtk_afe_src_en_connect()`, `mtk_dai_src_hw_params()`, `mtk_dai_src_hw_free()`, and public `mt8186_dai_src_register(struct mtk_base_afe *afe)`.

## Control Flow

Registration attaches two DAI drivers, shared DAPM widgets and routes, then allocates private state for `MT8186_DAI_SRC_1` and `MT8186_DAI_SRC_2` via `mt8186_dai_set_priv()`.

`mtk_dai_src_hw_params()` records the playback rate as `dl_rate` or capture rate as `ul_rate`, selects the correct input or output mode field in `GENERAL_ASRC_MODE`, and writes the transformed mode. `mtk_dai_src_hw_free()` clears the matching rate field when a stream is freed.

DAPM routes to the ASRC supply are conditional. `mtk_afe_src_en_connect()` only allows the enable route when both downlink and uplink rates are greater than zero, preventing a converter from powering before both stream directions have configured rates.

On `SND_SOC_DAPM_PRE_PMU`, `mtk_hw_src_event()` programs the selected converter through `mtk_set_src_1_param()` or `mtk_set_src_2_param()`. Those helpers write output and input frequency modes, initialize calibration/control registers, clear control register 2, and if `rate_in > rate_out`, fetch a matching IIR coefficient table, enable coefficient SRAM access, reset the coefficient address, write every coefficient to the coefficient data register, disable SRAM access, set IIR stage count, and enable IIR filtering. On `POST_PMU` it turns on ASM and CHSET and pulses/sets stream clear; on `PRE_PMD` it turns ASM and CHSET off and clears the stream-clear bit.

## State and Persistence Behavior

State persists only in `afe_priv->dai_priv[id]` and volatile ASRC registers. `dl_rate` and `ul_rate` are the gate for DAPM connection and parameter programming. Coefficients are stored in hardware coefficient SRAM until rewritten or the hardware block is reset. There is no file-backed persistence.

## Dependencies and Integration Points

The file depends on `linux/regmap.h`, `mt8186-afe-common.h`, and `mt8186-interconnection.h`. It uses register macros for `AFE_GENERAL{1,2}_ASRC_2CH_CON*`, `GENERAL_ASRC_MODE`, and `GENERAL_ASRC_EN_ON`. DAPM inputs include DL1/DL2/DL3/DL4/DL5/DL6, I2S0, and HW Gain 2 outputs; routes export `HW_SRC_1_Out` and `HW_SRC_2_Out` endpoints. Machine links in `mt8186-mt6366.c` expose `HW_SRC_1`, `HW_SRC_2`, and hostless SRC links.

## Risks and Edge Cases

Only explicit coefficient combinations are supported for downsampling. A valid hardware conversion rate without a table returns `-EINVAL` from the PRE_PMU path, but `mtk_hw_src_event()` ignores that return and still returns 0, so DAPM may proceed after a failed parameter setup. `mtk_get_src_freq_mode()` returns 0 on invalid rates after logging, which can program an invalid frequency mode if callers do not reject it. Coefficient writes must not be read during write, as noted by the code; debug or regmap instrumentation that reads during this sequence could be unsafe. Register writes ignore regmap errors.

## Test Signals

Test same-rate, upsampling, and downsampling cases for both SRC blocks. For downsampling, verify the expected coefficient table length and IIR stage are programmed; for unsupported conversions, verify error logs. DAPM tests should show SRC routes remain disconnected until both playback and capture sides have rates. Regmap traces should show `GENERAL_ASRC_MODE`, frequency registers, coefficient SRAM control, coefficient data writes, `G_SRC_CHSET_IIR_EN`, `G_SRC_ASM_ON`, and `G_SRC_CHSET_ON`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-src.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-tdm.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-tdm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-interconnection.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-interconnection.h

## Purpose

`mt8186-interconnection.h` defines MT8186 AFE input-port indices used by DAPM interconnection controls. The definitions map logical sources such as I2S channels, ADDA uplink channels, DL memory interfaces, gain outputs, SRC outputs, and TDM input channels to bit positions in `AFE_CONN*` registers. The complete 69-line header was read.

## Important APIs, Types, and Functions

There are no functions or types. Important macro families are low input indices `I_I2S0_CH*`, `I_ADDA_UL_CH*`, `I_DL*_CH*`, `I_PCM_*`, `I_GAIN*_OUT_CH*`, and high input indices represented as offsets from `I_32_OFFSET`, including `I_CONNSYS_I2S_CH*`, `I_SRC_*_OUT_CH*`, `I_DL4` through `I_DL8`, and `I_TDM_IN_CH1` through `I_TDM_IN_CH8`.

## Control Flow

The header has no runtime control flow. ASoC DAI files compile these macros into `SOC_DAPM_SINGLE_AUTODISABLE()` controls. At runtime, those controls set or clear the corresponding AFE connection bit when DAPM routes are activated.

## State and Persistence Behavior

No state is stored in this file. The macro values become register bit positions in DAPM controls; the resulting connection state is held by the AFE regmap and ALSA control/DAPM state.

## Dependencies and Integration Points

The header is included by MT8186 DAI files including hardware gain, I2S, PCM, SRC, and TDM paths. It depends only on its include guard. Its values must match `AFE_CONN*` and `AFE_CONN*_1` register layouts from `mt8186-reg.h` and the SoC hardware interconnect matrix.

## Risks and Edge Cases

Incorrect bit values silently route audio to the wrong source or no source. Some aliases intentionally overlap, such as `I_DL12_CH3` using the same bit as `I_DL1_CH1`, so consumers must understand the associated connection register context. High-port definitions subtract `I_32_OFFSET`; using them with a non-`*_1` register or using low-port values with a high register would address the wrong bit.

## Test Signals

Route-level tests should toggle each mixer switch and inspect the expected `AFE_CONN*` bit. Audio loopback tests can verify DL, ADDA, gain, SRC, CONNSYS, and TDM paths. Static review should compare this file with MT8186 hardware register documentation and with every `SOC_DAPM_SINGLE_AUTODISABLE()` use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-interconnection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-misc-control.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-misc-control.c

## Purpose

`mt8186-misc-control.c` adds miscellaneous ALSA controls for the MT8186 AFE sine generator. These controls select loopback target, sample rate, amplitude, mute state, and frequency dividers by programming `AFE_SINEGEN_CON0` and `AFE_SINEGEN_CON2`. The complete 252-line file was read.

## Important APIs, Types, and Functions

The public entry point is `mt8186_add_misc_control(struct snd_soc_component *component)`, which calls `snd_soc_add_component_controls()` for `mt8186_afe_sgen_controls[]`.

Static data maps user-facing enum strings to register values: `mt8186_sgen_mode_str[]`, `mt8186_sgen_mode_idx[]`, `mt8186_sgen_rate_str[]`, `mt8186_sgen_rate_idx[]`, and `mt8186_sgen_amp_str[]`. Control callbacks are `mt8186_sgen_get()`, `mt8186_sgen_set()`, `mt8186_sgen_rate_get()`, `mt8186_sgen_rate_set()`, `mt8186_sgen_amplitude_get()`, and `mt8186_sgen_amplitude_set()`.

## Control Flow

When the AFE component registers miscellaneous controls, ALSA exposes `Audio_SineGen_Switch`, `Audio_SineGen_SampleRate`, `Audio_SineGen_Amplitude`, channel mute switches, and frequency divider controls. Mode changes validate the enum index, translate it through `mt8186_sgen_mode_idx[]`, and either enable DAC sine generation with a selected loopback mode or disable sine generation and set the loopback field to `0x3f`. Rate changes translate through `mt8186_sgen_rate_idx[]` and program both channel sine mode fields. Amplitude changes validate against `AMP_DIV_CH1_MASK` and write both channel amplitude fields.

## State and Persistence Behavior

The current mode, rate, and amplitude are cached in `afe_priv->sgen_mode`, `afe_priv->sgen_rate`, and `afe_priv->sgen_amplitude`. Register state is volatile. ALSA controls return 1 when a cached value changed and 0 for no-op updates.

## Dependencies and Integration Points

The file includes Linux delay/DMA/io/regmap headers, ASoC headers, common MediaTek AFE platform headers, and `mt8186-afe-common.h`. The sine generator controls are component-level controls rather than DAI-specific controls. They are useful for hardware bring-up, loopback testing, and path validation across the interconnection matrix.

## Risks and Edge Cases

Some mode table entries map to `-1`, which disables sine generation; user-visible enum labels therefore include values that are not active loopback targets. The code validates enum bounds but does not validate that `mt8186_sgen_rate_idx[rate]` is hardware-valid beyond the table. The amplitude callback compares the enum value against `AMP_DIV_CH1_MASK`, relying on enum ordering matching register encoding. Regmap write errors are ignored.

## Test Signals

After card probe, `amixer` should show all sine-generator controls. Changing `Audio_SineGen_Switch` should update `INNER_LOOP_BACK_MODE` and `DAC_EN`; selecting `OFF` or invalid-mapped entries should disable generation. Rate and amplitude controls should update both channel fields. Audio bring-up can verify audible or captured sine on selected loopback paths and mute/frequency divider controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-misc-control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-mt6366-common.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-mt6366-common.c

## Purpose

`mt8186-mt6366-common.c` provides shared helpers for MT8186 machine drivers that use the MT6366/MT6358 codec path. It initializes the MTKAIF protocol for the primary codec runtime and offers a helper to replace backend link codecs from device-tree nodes. The complete 57-line file was read.

## Important APIs, Types, and Functions

Public exported functions are `mt8186_mt6366_init(struct snd_soc_pcm_runtime *rtd)` and `mt8186_mt6366_card_set_be_link(struct snd_soc_card *card, struct snd_soc_dai_link *link, struct device_node *node, char *link_name)`. Both are exported with `EXPORT_SYMBOL_GPL`.

## Control Flow

`mt8186_mt6366_init()` looks up the AFE component by `AFE_PCM_NAME`, obtains the codec component from the runtime, retrieves `mt8186_afe_private`, calls `mt6358_set_mtkaif_protocol()` with `MT6358_MTKAIF_PROTOCOL_1`, stores the selected protocol in `afe_priv->mtkaif_protocol`, and synchronizes DAPM. If `snd_soc_dapm_sync()` fails, it logs and returns the error.

`mt8186_mt6366_card_set_be_link()` checks whether a device-tree node is present and whether the current link name matches the requested backend link name. For matching links it calls `snd_soc_of_get_dai_link_codecs()` to populate the link codec array from the node and returns a probed error on failure.

## State and Persistence Behavior

The only cached state is `afe_priv->mtkaif_protocol`, which persists for the lifetime of the AFE device. Codec link replacement mutates the in-memory `snd_soc_dai_link` before card registration. There is no persistent storage.

## Dependencies and Integration Points

The file includes ASoC headers, codec header `mt6358.h`, common MediaTek platform headers, `mt8186-afe-common.h`, and its companion header. It is used by `mt8186-mt6366.c` for primary codec init and legacy device-tree backend codec assignment.

## Risks and Edge Cases

`snd_soc_rtd_to_codec(rtd, 0)` assumes at least one codec component exists. The helper only updates codecs for exact link-name matches, so renamed backend links in the machine driver or device tree would silently skip replacement. `char *link_name` could be `const char *`; current API permits modification even though no modification is intended.

## Test Signals

Probe logs should show successful primary codec init without DAPM sync errors. Regmap/codec traces should confirm MTKAIF protocol 1 is set. Legacy device-tree cards should bind playback and headset codecs into the intended I2S backend links; missing child nodes should produce probe errors in the caller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-mt6366-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-mt6366-common.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-mt6366-common.h

## Purpose

`mt8186-mt6366-common.h` declares the shared MT8186/MT6366 machine-driver helpers implemented in `mt8186-mt6366-common.c`. The complete 17-line header was read.

## Important APIs, Types, and Functions

It declares `mt8186_mt6366_init(struct snd_soc_pcm_runtime *rtd)` and `mt8186_mt6366_card_set_be_link(struct snd_soc_card *card, struct snd_soc_dai_link *link, struct device_node *node, char *link_name)`. It defines only the include guard `_MT8186_MT6366_COMMON_H_`.

## Control Flow

There is no executable control flow. Including machine drivers compile against these prototypes and call the helpers during card initialization or legacy probe setup.

## State and Persistence Behavior

The header owns no storage. State effects are in the implementation: MTKAIF protocol caching in AFE private data and in-memory DAI-link codec assignment.

## Dependencies and Integration Points

The declarations reference ASoC types `struct snd_soc_pcm_runtime`, `struct snd_soc_card`, and `struct snd_soc_dai_link`, plus `struct device_node`. It is included by `mt8186-mt6366.c` and should remain synchronized with exported function signatures in the implementation.

## Risks and Edge Cases

No direct runtime risk exists, but signature drift between this header and `mt8186-mt6366-common.c` would break builds. The non-const `char *link_name` is more permissive than necessary and can propagate const-correctness warnings if callers use string constants in stricter contexts.

## Test Signals

Build coverage for MT8186 machine drivers is the main signal. Include-order testing should confirm the referenced ASoC structs are declared by included source files before use or accepted as incomplete struct declarations by the compiler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-mt6366-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-mt6366.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-mt6366.c

## Purpose

`mt8186-mt6366.c` is the MT8186 ASoC machine driver for boards combining the MT8186 AFE with MT6366/MT6358 primary codec support and several external codec combinations such as RT1019/RT5682S, RT5682S/MAX98360, RT5650, and DA7219/MAX98357. It defines the card-level DAI links, DAPM widgets/routes, headset and HDMI jack setup, codec clock programming, SOF integration, legacy device-tree codec replacement, PCM constraints, and platform-driver binding. The complete 1377-line file was read.

## Important APIs, Types, and Functions

The machine private state is `struct mt8186_mt6366_rt1019_rt5682s_priv`, holding optional DMIC select GPIO and cached DMIC switch value. `enum mt8186_jacks` indexes headset and HDMI jack objects.

Important init and callback functions include `dmic_get()`, `dmic_set()`, `primary_codec_init()`, `mt8186_headset_codec_init()`, `mt8186_da7219_i2s_hw_params()`, `mt8186_da7219_i2s_hw_free()`, `mt8186_rt5682s_i2s_hw_params()`, `mt8186_mt6366_rt1019_rt5682s_hdmi_init()`, `mt8186_hw_params_fixup()`, `mt8186_i2s_hw_params_24le_fixup()`, `mt8186_i2s_hw_params_32le_fixup()`, `mt8186_sof_dai_link_fixup()`, `mt8186_mt6366_legacy_probe()`, and `mt8186_mt6366_soc_card_probe()`.

Important static data includes many `SND_SOC_DAILINK_DEFS()` definitions for frontends, backends, hostless links, and SOF links; `g_sof_conn_streams[]`; the main `mt8186_mt6366_rt1019_rt5682s_dai_links[]`; card variants `mt8186_mt6366_da7219_max98357_soc_card`, `mt8186_mt6366_rt1019_rt5682s_soc_card`, `mt8186_mt6366_rt5682s_max98360_soc_card`, and `mt8186_mt6366_rt5650_soc_card`; `mt8186_pcm_constraints[]`; `mt8186_sof_priv`; variant `mtk_soundcard_pdata` blocks; and the OF match table.

## Control Flow

The platform driver uses `mtk_soundcard_common_probe` as its probe. The selected OF compatible provides a `mtk_soundcard_pdata` instance, which points to the card, PCM constraints, optional SOF data, and `mt8186_mt6366_soc_card_probe()` as SoC-specific setup.

`mt8186_mt6366_soc_card_probe()` allocates machine-private state, obtains optional `dmic` GPIO, rewrites I2S backend fixups/ops based on whether the DA7219 variant is present, optionally runs legacy codec-node replacement, and initializes AFE GPIOs. Legacy probing loads `playback-codecs` and `headset-codec` child nodes and applies them to `I2S3`, `I2S0`, and `I2S1` links through `mt8186_mt6366_card_set_be_link()`.

Primary codec runtime init calls `mt8186_mt6366_init()` to set MTKAIF protocol, then optionally adds DMIC DAPM widgets and routes when a DMIC GPIO exists. Headset init shares I2S1 clock to I2S0, creates the headset jack with headphone/mic pins and four buttons, assigns key codes based on the codec variant, and registers the jack with the codec. HDMI init shares I2S2 clock to I2S3, creates an HDMI jack, and registers it with the HDMI codec.

Codec `hw_params` callbacks program external codec clocks. DA7219 setup requests CPU MCLK at `rate * 256`, configures DA7219 MCLK, and selects a PLL output based on 8 kHz-family versus 44.1 kHz-family rates; `hw_free()` stops the PLL. RT5682S setup configures TDM slot bit width, codec PLL from BCLK to 512fs, codec sysclk from PLL1, and CPU MCLK at `rate * 128`.

SOF fixup first delegates to `mtk_sof_dai_link_fixup()` and then applies MT8186-specific BE format fixups for I2S links, choosing S24_LE or S32_LE differently depending on DA7219 presence and I2S link id.

## State and Persistence Behavior

Card state is static data plus runtime `mtk_soc_card_data` and `mach_priv`. DMIC selection persists in `priv->dmic_switch` and in the optional GPIO output. Jack state lives in the ASoC jack subsystem. DAI-link arrays are mutated before registration for variant-specific ops/fixups and legacy codecs. Codec PLL and sysclk settings persist only while streams are active. PCM constraints force playback/capture rates to 48 kHz and channels to the listed sets through in-memory ALSA constraints.

## Dependencies and Integration Points

The driver depends on GPIO, input, module, OF, ASoC jack/PCM APIs, codec-specific headers for DA7219, MT6358, and RT5682, MediaTek common sound-card helpers, SOF common helpers, AFE clock/GPIO/common headers, and `mt8186-mt6366-common.h`. It integrates with CPU DAIs registered by MT8186 AFE files, codec drivers named `mt6358-sound`, `dmic-codec`, `bt-sco`, `hdmi-audio-codec`, RT5682S, DA7219, and speaker codecs, plus OF compatibles under `mt8186_mt6366_dt_match[]`.

## Risks and Edge Cases

The single DAI-link array is reused by all card variants and mutated at probe time, so care is needed if multiple variant devices could coexist in one kernel instance. Legacy probe requires both `playback-codecs` and `headset-codec` child nodes and fails probe if either is missing. Several operations compare codec/component/link names as strings, which is fragile across device naming changes. `dmic_set()` does not validate enum bounds directly, relying on ASoC enum handling. The DA7219 and RT5682S clock formulas assume fixed MCLK ratios; unsupported rates or codec PLL constraints surface only through codec callbacks. `mt8186_sof_dai_link_fixup()` returns the result of common SOF fixup even if a local format fixup failed, though local helpers currently return success.

## Test Signals

Build as a module or built-in with all referenced codec options. Probe each compatible string and confirm the expected card name, DAI links, controls, DAPM routes, and PCM constraints. Test headset insertion, microphone detect, and button key mapping for RT5682S and DA7219 variants. Test HDMI jack creation and I2S2-to-I2S3 clock sharing. Exercise DA7219 and RT5682S streams while tracing codec PLL/sysclk and CPU MCLK calls. Validate SOF topology paths through `g_sof_conn_streams[]`, and legacy device-tree boards with codec child-node replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-mt6366.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-reg.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-reg.h

## Purpose

`mt8186-reg.h` is the central MT8186 AFE register definition header. It defines bit shifts, masks, composite helper macros, register offsets, maximum register address, and interrupt status/count masks used by the MT8186 platform, DAI, clock, memory-interface, interrupt, ADDA, ASRC, I2S, PCM, TDM/ETDM, sine-generator, secure, and debug code. The complete 2913-line header was read.

## Important APIs, Types, and Functions

The only type is an enum for memory-interface playback buffer size values: `MT8186_MEMIF_PBUF_SIZE_32_BYTES`, `64_BYTES`, `128_BYTES`, `256_BYTES`, and `MT8186_MEMIF_PBUF_SIZE_NUM`.

There are no functions. Macro groups include power and top control fields (`AUDIO_TOP_CON*`, `PDN_*`), global AFE enable and memory-interface enables (`AFE_DAC_CON0`, `DL*_ON`, `VUL*_ON`, `AUDIO_AFE_ON`), I2S fields (`AFE_I2S_CON*`, `AFE_CONNSYS_I2S_CON`), PCM fields (`PCM_INTF_CON1`, `PCM_INTF_CON2`, `PCM2_INTF_CON`), gain fields (`AFE_GAIN*_CON*`, `GAIN*_TARGET`, `AFE_GAIN*_CUR`), ADDA/MTKAIF fields, sine-generator fields, general ASRC fields (`AFE_GENERAL{1,2}_ASRC_2CH_CON*`, `GENERAL_ASRC_MODE`, `GENERAL_ASRC_EN_ON`), IRQ fields (`AFE_IRQ_MCU_*`), ETDM input fields (`ETDM_IN1_CON0` through `CON8` plus helper macros such as `ETDM_IN_CON3_FS()`), and the full register offset map from `AUDIO_TOP_CON0` through `ETDM_0_3_COWORK_CON3`.

## Control Flow

There is no executable control flow. Other C files use these macros in `regmap_update_bits()`, `regmap_write()`, regmap ranges, interrupt configuration, and DAPM control definitions. Field macros encode hardware layout so runtime control flow in DAI and platform code can assemble register values safely.

## State and Persistence Behavior

The header owns no state. It defines how volatile hardware state is addressed and masked. Persistent behavior is indirect: any incorrect macro can cause driver state to be written to the wrong field or register, affecting audio hardware until reset or reprogramming.

## Dependencies and Integration Points

The header relies on Linux `BIT()` and `GENMASK()` macros being available before use through including headers. It is included via `mt8186-afe-common.h` by the MT8186 DAI files in this work item and by broader MT8186 AFE platform code. It is tightly coupled to the SoC hardware manual and to regmap configuration, DAPM routes, IRQ handling, DMA memory-interface setup, clock gating, ADDA codec interface setup, ASRC coefficient loading, PCM/I2S/TDM programming, and debug/test controls.

## Risks and Edge Cases

This file is hardware ABI. A wrong offset, shift, or mask can corrupt unrelated AFE state, break audio routing, or cause subtle format/rate/clocking failures. Several symbolic names are reused across register contexts, such as generic `I2S_*` fields and `G_SRC_*` fields, so callers must pair them with the correct register. Some masks include both raw masks and shifted masks; using `_MASK` where `_MASK_SFT` is required, or vice versa, would produce wrong regmap operations. Register offset additions must update `AFE_MAX_REGISTER` and regmap access tables elsewhere. Because the header is macro-only, errors are usually caught by runtime audio behavior rather than compiler diagnostics.

## Test Signals

Build coverage catches missing names but not semantic mistakes. Stronger signals include regmap trace comparison against the hardware programming guide, runtime playback/capture across all memory interfaces, I2S/PCM/TDM/SRC/HW gain path tests, interrupt cadence tests using `AFE_IRQ_MCU_*`, sine-generator loopback tests, ASRC coefficient programming tests, and debugfs/regmap dumps confirming expected offsets and field values. Static review should compare changed macro groups against known-good vendor or upstream MT8186 definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/Makefile

## Purpose

`sound/soc/mediatek/mt8188/Makefile` defines the object composition for the MT8188 ASoC platform driver and machine driver under Kbuild. It selects which `.o` files are linked into `snd-soc-mt8188-afe.o` and which machine-card object is built for the MT8188/MT6359 configuration. The complete 16-line file was read.

## Important APIs, Types, and Functions

There are no C APIs, types, or functions. Kbuild variables are `snd-soc-mt8188-afe-y`, `obj-$(CONFIG_SND_SOC_MT8188)`, and `obj-$(CONFIG_SND_SOC_MT8188_MT6359)`. The platform aggregate includes `mt8188-afe-clk.o`, `mt8188-afe-pcm.o`, `mt8188-audsys-clk.o`, `mt8188-dai-adda.o`, `mt8188-dai-dmic.o`, `mt8188-dai-etdm.o`, and `mt8188-dai-pcm.o`; the machine driver builds `mt8188-mt6359.o`.

## Control Flow

Kbuild evaluates this file during kernel build. If `CONFIG_SND_SOC_MT8188` is enabled, it builds and links the listed platform objects into `snd-soc-mt8188-afe.o`. If `CONFIG_SND_SOC_MT8188_MT6359` is enabled, it builds the machine driver object. There is no runtime control flow in the Makefile itself.

## State and Persistence Behavior

The file has no runtime state. Its build-time state is the selected kernel configuration and the object list generated from `*-y` variables.

## Dependencies and Integration Points

It integrates with the Linux Kbuild system and the parent MediaTek ASoC Makefile. Object names must match source files in the same directory and Kconfig symbols must match the MediaTek sound Kconfig definitions. The platform aggregate is the link boundary for the MT8188 AFE driver.

## Risks and Edge Cases

Missing an object from `snd-soc-mt8188-afe-y` can produce unresolved symbols or silently omit a DAI from the platform driver. Adding an object without the matching source file breaks builds. Kconfig symbol drift between Makefile and Kconfig prevents expected drivers from building. Object order can matter if initcall or linker-section assumptions exist, though this file mostly uses ordinary driver objects.

## Test Signals

Run kernel build or at least `make M=sound/soc/mediatek/mt8188` with `CONFIG_SND_SOC_MT8188` and `CONFIG_SND_SOC_MT8188_MT6359` enabled. Check that `snd-soc-mt8188-afe.o` contains all intended platform objects and that disabling each Kconfig symbol removes the corresponding object from the build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/Makefile -->
