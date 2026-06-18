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
