# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-afe-clk.c

Purpose: centralizes MT8183 audio clock acquisition, top-level AFE clock gating, APLL1/APLL2 routing and tuner control, sample-rate-family APLL selection, and I2S/TDM MCLK divider programming.

Important APIs/types/functions: `aud_clks` maps private clock IDs to DT/CCF names; `mt8183_init_clock` obtains all clocks; `mt8183_afe_enable_clock` enables infrastructure/audio mux/AFE/I2S BCLK switch clocks and sets mux parents; `mt8183_afe_disable_clock` ungates in reverse; `apll1_mux_setting` and `apll2_mux_setting` select 22.5792 MHz or 24.576 MHz APLL-derived paths; `mt8183_apll1_enable/disable` and `mt8183_apll2_enable/disable` control tuner clocks/registers and HD engine bits; `mt8183_get_apll_rate`, `mt8183_get_apll_by_rate`, and `mt8183_get_apll_by_name` route 44.1k-family vs 48k-family clocks; `mt8183_mck_enable/disable` controls per-I2S master-clock selectors and dividers.

Control flow: AFE probe calls `mt8183_init_clock`; runtime resume calls `mt8183_afe_enable_clock` before touching registers, and suspend calls disable. DAPM APLL supplies in I2S/TDM call APLL enable/disable. I2S/TDM MCLK DAPM events call `mt8183_mck_enable`, which selects an APLL family from the requested rate, enables an optional top selector, parents it to the selected APLL mux, enables the divider, and sets divider rate.

State and persistence: all clock pointers are stored in `mt8183_afe_private->clk`. Clock enable counts and parent/rate choices persist in the CCF while active. Tuner and HD engine state persists in regmap registers until disabled or runtime-suspended.

Dependencies and integration: depends on Linux CCF, `mt8183-reg.h` tuner/HD engine bits, `mt8183-afe-common.h` private state and MCLK IDs, and DAPM supply events from I2S/TDM DAI files. DT must expose every clock name in `aud_clks`.

Risks: APLL enable functions call mux-setting helpers but ignore their return values, so a failed mux parent change can be hidden until later clock operations. `mt8183_get_apll_by_name` treats every non-APLL1 name as APLL2. `mt8183_mck_enable` assumes `mck_id` is valid and only special-cases I2S5 MCK. Error paths disable clocks but do not always restore mux parents after later failures.

Test signals: probe with all clocks present, runtime suspend/resume, playback/capture at 44.1k-family and 48k-family rates, DAPM low-jitter/MCLK routes, `clk_summary` parent/rate checks, and fault injection for clock get/enable/set_parent/set_rate failures.
