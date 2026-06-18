# sources/distributed-fs/ceph-client/drivers/clk/meson/sclk-div.c

Purpose: This is the Meson sample-clock divider implementation. It models hardware where divider register value zero gates the clock, nonzero values encode `divider = value + 1`, and some LR-clock variants have a programmable high-time field for duty cycle.

Important APIs, types, and functions: The exported API is `meson_sclk_div_ops`. Internal helpers include `sclk_div_maxval`, `sclk_div_maxdiv`, `sclk_div_getdiv`, `sclk_div_bestdiv`, `sclk_div_determine_rate`, `sclk_apply_ratio`, `sclk_div_set_duty_cycle`, `sclk_div_get_duty_cycle`, `sclk_apply_divider`, `sclk_div_set_rate`, `sclk_div_recalc_rate`, `sclk_div_enable`, `sclk_div_disable`, `sclk_div_is_enabled`, and `sclk_div_init`.

Control flow: CCF rate requests enter `determine_rate`, which finds the closest divider and may ask the parent to round to a better rate when `CLK_SET_RATE_PARENT` is set. `set_rate` caches the chosen divider and only writes hardware immediately if the clock is enabled. `enable` writes the cached divider and duty ratio; `disable` writes zero to the divider field. Init calls `clk_regmap_init`, reads the current hardware divider, chooses max divider if disabled, and caches the duty cycle.

State and persistence behavior: `struct meson_sclk_div_data` stores `cached_div` and `cached_duty` in memory. Hardware persistence is limited to the divider and optional high-time fields. Disabled clocks preserve desired rate in memory so enable can restore it rather than writing while gated.

Dependencies and integration points: It depends on `clk-regmap`, `parm`, common divider helpers, and CCF duty-cycle callbacks. Meson audio/sample clock definitions use this ops table through `clk_regmap` data.

Risks and edge cases: Divider zero means disabled, so rate recalculation uses cached state instead of raw hardware when disabled. Duty-cycle math depends on `cached_div`; unset or invalid duty denominators can produce unexpected high-time values. Parent-rate search clamps divider to at least 2. Test signals include rate round/set with and without parent propagation, enable-after-set behavior, disabled-state recalc, duty-cycle get/set on variants with and without `hi`, and register traces confirming zero gates the clock.
