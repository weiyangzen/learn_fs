# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-dai-i2s.c

## Purpose

`mt8189-dai-i2s.c` implements MT8189 I2S-style backend DAIs using the ETDM input/output hardware blocks. It configures ETDM IN0/IN1 and OUT0/OUT1/OUT4, manages APLL and MCLK DAPM supplies, supports optional I2S sharing from device tree, and exposes DAPM mixers/routes so memory interfaces and internal sources can feed external I2S outputs or capture I2S inputs.

## Important APIs, Types, And Data

The exported function is `mt8189_dai_i2s_register()`. It registers five DAIs: `I2SIN0`, `I2SIN1`, `I2SOUT0`, `I2SOUT1`, and `I2SOUT4`. `I2SOUT4` supports up to 8 playback channels; the others are 2-channel. The DAI ops are `mtk_dai_i2s_ops` with `.hw_params = mtk_dai_i2s_hw_params` and `.set_sysclk = mtk_dai_i2s_set_sysclk`.

`struct mtk_afe_i2s_priv` persists per-DAI rate, MCLK ID/rate/APLL, share-property name, share target, channel count, sync/IP/slave/loopback fields, and low-jitter metadata. The static `mt8189_i2s_priv[]` seeds default IDs, MCLK IDs, and default share mappings: I2SIN0 defaults to sharing I2SOUT0, I2SIN1 defaults to sharing I2SOUT1, outputs default to no share, and I2SOUT4 uses the I2SIN1 MCK ID. `mt8189_dai_i2s_get_share()` can override these from device tree string properties such as `i2sin0-share` and `i2sout4-share`.

Rate and format helpers translate ALSA parameters to ETDM encodings: `get_etdm_rate()`, `get_etdm_inconn_rate()`, `get_etdm_wlen()`, and `get_etdm_lrck_width()`. User controls include `I2SIN0 Loopback` and `I2SIN1 Loopback`. Dummy muxes allow an I2S interface to be powered without a real codec path.

## Control Flow

During registration, `init_i2s_priv_data()` allocates and copies the template private data into `afe_priv->dai_priv[]`, then `mt8189_dai_i2s_get_share()` parses any share properties. At hw_params time, `mtk_dai_i2s_config()` records the stream rate and writes the relevant ETDM register block. IN0/IN1 configure initial count/point, LRCK reset, APLL clock source, auto clock enable, FS timing, relatch rate, AFIFO mode, almost-end counters, output-to-latch time, I2S format, APLL relatch domain, bit length, word length, and cowork master/slave selection. OUT0/OUT1/OUT4 similarly configure initial timing, FS timing, APLL clock source, relatch selection, I2S format, APLL relatch domain, bit length, word length, and cowork selection for OUT0/OUT1. If a DAI has `share_i2s_id >= 0`, the same configuration recursively applies to the shared DAI.

`mtk_dai_i2s_set_sysclk()` validates that the requested output MCLK divides the selected APLL rate, then records `mclk_rate` and `mclk_apll`. If the current DAI has a share target, it propagates the same MCLK values to the shared private data. DAPM supply events use that state: `mtk_apll_event()` enables/disables APLL1 or APLL2 based on widget name, and `mtk_mclk_en_event()` enables/disables the specific MCK gate only while a nonzero MCLK rate is routed. DAPM route predicates `mtk_afe_i2s_share_connect()`, `mtk_afe_i2s_apll_connect()`, `mtk_afe_i2s_mclk_connect()`, and `mtk_afe_mclk_apll_connect()` dynamically decide whether shared I2S, APLL, and MCLK routes are active.

The route table is substantial. I2SOUT0 and I2SOUT1 mix DL0-DL8 and DL_24CH stereo pairs plus gain/ADDA/PCM inputs. I2SOUT4 mixes DL0-DL8, DL24, DL_24CH channels 1-8, gain, ADDA, PCM, and SRC2. I2SIN0/I2SIN1 are capture widgets with DAPM supplies and optional dummy input muxes.

## State And Persistence

State lives in per-DAI `struct mtk_afe_i2s_priv` objects under `afe_priv->dai_priv[]`. The important persistent fields are `rate`, `mclk_rate`, `mclk_apll`, and `share_i2s_id`, which DAPM route predicates read after hw_params/set_sysclk. MCLK rate is reset to zero on MCLK supply power-down. ETDM registers are programmed during hw_params and rely on the platform regcache/runtime PM to preserve or restore values across power transitions.

## Dependencies And Integration Points

This file depends on clock helpers such as `mt8189_apll1_enable()`, `mt8189_apll2_enable()`, `mt8189_get_apll_by_rate()`, `mt8189_get_apll_rate()`, and `mt8189_mck_enable()`. It uses register definitions from `mt8189-afe-common.h`, interconnect bit indexes from `mt8189-interconnection.h`, and common AFE DAI data structures. The machine driver sets I2S BE sysclk through `snd_soc_dai_set_sysclk()`; that call is required before DAPM can enable the correct MCLK path.

## Risks

`get_etdm_rate()` and `get_etdm_inconn_rate()` return zero for unsupported rates instead of erroring, so an unexpected rate could silently program the 8 kHz encoding. `get_etdm_lrck_width()` returns zero only for physical width <= 1; normal S8 becomes 7, S16 becomes 15, and S32 becomes 31. Share recursion lacks cycle detection, so invalid device tree share properties could cause repeated configuration or recursion. `mtk_dai_i2s_set_sysclk()` checks `share_i2s_id > 0`, not `>= 0`, which is fine for current positive DAI IDs but should be kept in mind if IDs change. Route predicates depend on widget name prefixes, so DAPM widget renames can break behavior.

## Test Signals

Validate 48 kHz and higher-rate I2S playback/capture with I2SOUT0/1/4 and I2SIN0/1. Confirm set_sysclk failures for non-divisible MCLKs and success for expected 128fs or codec-driven rates. Device tree share-property tests should show only intended shared enable routes in DAPM. Regmap traces should show ETDM IN/OUT timing, word length, FS timing, cowork, APLL, and MCLK bits programmed before DAPM enables the interface.
