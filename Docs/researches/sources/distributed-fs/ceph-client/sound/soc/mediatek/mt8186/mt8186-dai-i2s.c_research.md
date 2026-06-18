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
