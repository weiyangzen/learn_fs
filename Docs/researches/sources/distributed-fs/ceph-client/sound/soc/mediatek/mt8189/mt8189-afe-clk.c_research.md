# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-afe-clk.c

## Purpose

`mt8189-afe-clk.c` implements MT8189 AFE clock acquisition, gating, parent selection, APLL setup, MCLK setup, and always-on peripheral clock enablement. It is the clock-control layer used by MT8189 platform and DAI drivers to make register access, main AFE operation, audio PLLs, and serial-port master clocks available.

## Important APIs, Types, and Data

`struct mt8189_mck_div` maps each logical MCLK ID to an optional mux clock and a divider clock. `mck_div[]` covers I2S input/output MCLKs, FMI2S, TDM output MCLK, and TDM output BCK. `aud_clks[]` maps the `MT8189_CLK_*` enum values from `mt8189-afe-clk.h` to device-tree clock names such as `top_aud_intbus`, `apll1`, `apll12_div_i2sin0`, `top_i2sout0`, and `aud_mst_ck_peri`.

Exported or externally declared functions include `mt8189_init_clock()`, `mt8189_afe_enable_clk()`, `mt8189_afe_disable_clk()`, `mt8189_afe_enable_reg_rw_clk()`, `mt8189_afe_disable_reg_rw_clk()`, `mt8189_afe_enable_main_clock()`, `mt8189_afe_disable_main_clock()`, `mt8189_apll1_enable()`, `mt8189_apll1_disable()`, `mt8189_apll2_enable()`, `mt8189_apll2_disable()`, `mt8189_get_apll_rate()`, `mt8189_get_apll_by_rate()`, `mt8189_get_apll_by_name()`, `mt8189_mck_enable()`, and `mt8189_mck_disable()`.

Static helpers convert clock-gate IDs to registers, masks, and on/off values. This matters because some top fields are positive enables in `AUDIO_ENGEN_CON0`, while others are power-down bits in `AUDIO_TOP_CON4`.

## Control Flow

Clock initialization starts with `mt8189_init_clock()`. It allocates `afe_priv->clk`, fetches every clock named in `aud_clks[]`, calls `mt8189_afe_disable_apll()` to put APLL-related muxes back under `clk26m`, and then enables always-on peripheral clocks for intbus, slave, and master audio peripheral domains. Failure in clock fetching aborts initialization; failure in AO enable unwinds only the clocks enabled by that helper.

APLL enable first calls either `apll1_mux_setting(true)` or `apll2_mux_setting(true)`. These helpers enable the top APLL mux, set it to the APLL clock, enable the corresponding engineering mux, set it to APLL divided by four, enable the audio high mux, and set it to the full APLL. Errors unwind previously enabled muxes and parents. The public APLL enable function then clears top power-down gates, programs `AFE_APLL1_TUNER_CFG` or `AFE_APLL2_TUNER_CFG`, enables the frequency tuner, and asserts the positive APLL enable bit. Disable reverses the positive enable, disables tuner, applies PDN gates, and returns muxes to 26 MHz.

MCLK enable validates `mck_id`, derives APLL1 for rates not divisible by 8000 and APLL2 for 8 kHz-family rates, optionally enables and reparents the MCLK mux, enables the divider clock, and sets the divider to the requested rate. MCLK disable disables the divider and optional mux. Register-read/write clock enable sets audio intbus and audio high mux parents to `clk26m` after enabling them. Main clock enable/disable writes the `MT8189_AUDIO_26M_EN_ON` top gate through regmap.

## State and Persistence

Runtime state is stored in `struct mt8189_afe_private`: `clk` is the devm-managed array of clock handles, and `mck_rate[]` is declared in the private struct although this file does not update it. Hardware state persists in the common clock framework's prepare/enable counts, mux parent selections, divider rates, and AFE regmap bits. APLL tuner register settings persist until disabled, reset, or overwritten.

No file-backed persistence exists. All state is per-device and tied to probe lifetime. Because this layer uses prepare/enable counts, callers must keep enable/disable calls balanced.

## Dependencies and Integration Points

The implementation depends on Linux CCF (`struct clk`, `devm_clk_get`, `clk_set_parent`, `clk_set_rate`, `clk_get_rate`, `clk_prepare_enable`), regmap, and MT8189 register macros from `mt8189-reg.h`. It assumes `afe->platform_priv` is a valid `struct mt8189_afe_private` and `afe->regmap` is initialized before gate/tuner operations.

Device tree must provide every clock name listed in `aud_clks[]`; one missing clock fails `mt8189_init_clock()`. Other MT8189 DAI files should call `mt8189_apll*` and `mt8189_mck_*` around stream setup, and platform code should call `mt8189_afe_enable_reg_rw_clk()` before register access when the domain may be off.

## Risks

`mt8189_mck_disable()` checks only `mck_id < 0`; it does not reject `mck_id >= MT8189_MCK_NUM` before indexing `mck_div[mck_id]`. Callers must pass valid IDs or this can read past the table. `mt8189_mck_enable()` can leak an enabled mux or divider on later parent/rate failures because not every error path disables earlier clocks. Similarly, APLL enable has multi-step regmap/clock side effects and does not fully unwind all top gates if a later gate write fails.

`mt8189_afe_enable_reg_rw_clk()` ignores return values from enable and parent-setting helpers, so callers receive success even if clocks failed. `mt8189_afe_enable_top_cg()` returns success when `afe->regmap` is null after logging an error, which can hide probe ordering mistakes. `mt8189_get_apll_by_name()` returns APLL2 for all non-`APLL1` names, so invalid names are not distinguishable from a valid APLL2 request.

Concurrent callers need external serialization or balanced reference patterns; this file does not maintain explicit users or locks. Parent selection of shared muxes can affect multiple active MCLK users if the clock tree is not designed for concurrent independent rates.

## Test Signals

Build coverage should include all MT8189 AFE objects. Runtime validation should inspect probe logs for successful `devm_clk_get` of every name, clock summary/debugfs parent and rate changes during 44.1 kHz and 48 kHz-family playback, balanced prepare counts after stream stop, and regmap traces for `AUDIO_ENGEN_CON0`, `AUDIO_TOP_CON4`, `AFE_APLL1_TUNER_CFG`, and `AFE_APLL2_TUNER_CFG`. Audio tests should cover I2S in/out, TDM MCLK/BCK, repeated stream start/stop, rate switching between APLL1 and APLL2 families, suspend/resume, and forced failure injection for missing clocks or failed `clk_set_parent`.
