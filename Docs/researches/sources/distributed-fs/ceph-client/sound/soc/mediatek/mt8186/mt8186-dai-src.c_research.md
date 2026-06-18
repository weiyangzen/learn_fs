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
