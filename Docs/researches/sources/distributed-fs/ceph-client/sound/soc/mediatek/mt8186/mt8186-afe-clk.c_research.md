# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-clk.c

## Purpose

`mt8186-afe-clk.c` is the MT8186 AFE clock consumer/orchestration layer. It obtains common clock framework handles, registers local audsys gate clocks, enables and disables audio infrastructure clocks, selects APLL parents, controls APLL tuner registers, and provides MCLK helpers for I2S and TDM users.

## Important APIs, Types, and Functions

The `aud_clks[CLK_NUM]` table maps clock IDs from `mt8186-afe-clk.h` to device-tree/clkdev names. `mt8186_init_clock()` registers audsys gate clocks, allocates `afe_priv->clk`, performs `devm_clk_get()` for every ID, and looks up `apmixedsys`, `topckgen`, and `infracfg` syscon regmaps. `mt8186_afe_enable_clock()` and `mt8186_afe_disable_clock()` manage the core clock sequence: infra audio, 26 MHz MTKAIF clock, top audio mux, audio internal bus mux, audio high-speed mux, and AFE gate. `mt8186_afe_enable_cgs()`/`disable_cgs()` enable the BCLK/ASRC/TDM clock gates from `CLK_I2S1_BCLK` through `CLK_ETDM_OUT1_BCLK`.

`mt8186_apll1_enable()` and `mt8186_apll2_enable()` set mux parents, enable 22.5792 MHz or 24.576 MHz paths, program `AFE_APLL*_TUNER_CFG`, and set `AFE_HD_ENGEN_ENABLE`. The matching disable functions clear those hardware bits and return muxes to `CLK_CLK26M`. `mt8186_get_apll_by_rate()` chooses APLL2 for rates divisible by 8000 and APLL1 otherwise. `mt8186_mck_enable()` selects the right APLL parent for an I2S/TDM master-clock mux, enables the divider, and sets the requested rate.

## Control Flow and State

Probe calls `mt8186_init_clock()` before regmap initialization. Runtime resume calls `mt8186_afe_enable_clock()` followed by `mt8186_afe_enable_cgs()`, and runtime suspend reverses that through `mt8186_afe_disable_cgs()` and `mt8186_afe_disable_clock()`. Clock handles and syscon regmaps persist in `struct mt8186_afe_private`. APLL and MCLK helpers are invoked by DAPM clock supplies and DAI hw_params code elsewhere.

## Dependencies and Integration Points

The file depends on Linux CCF, regmap/syscon, `mt8186-audsys-clk.c`, register macros from `mt8186-reg.h`, and the private state in `mt8186-afe-common.h`. Its clock-name strings must match both audsys registered gates and device-tree clock providers. ASoC DAPM clock supplies such as `aud_dac_clk` rely on these clocks being registered and discoverable.

## Risks

Several error paths return after enabling an earlier clock without fully unwinding muxes or prepared parents, especially inside APLL mux setup and MCLK setup. `mt8186_init_clock()` logs missing clocks and stores `NULL`; later helpers dereference clock slots without null checks, so missing DT/clkdev entries can become crashes rather than probe failures. `mt8186_get_apll_by_name()` defaults to APLL2 for every non-APLL1 name, so bad names are not rejected. MCLK IDs are not bounds checked before indexing `mck_div`.

## Test Signals

Useful signals include AFE probe with all `devm_clk_get()` entries present, runtime PM cycles without clock leak warnings, DAPM playback/capture paths enabling the expected audsys gates, 44.1 kHz paths selecting APLL1 and 48 kHz-family paths selecting APLL2, and I2S/TDM MCLK output rate measurements. Failure signatures are `clk_prepare_enable`/`clk_set_parent` errors, missing clock-provider names, or suspend/resume hangs around AFE enablement.
