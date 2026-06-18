# sources/distributed-fs/ceph-client/drivers/clk/clk-gpio.c

Purpose: GPIO-controlled clock provider for three variants: GPIO gate clocks, GPIO mux clocks, and gated fixed-rate clocks optionally backed by a regulator.

Important APIs, types, and functions: `struct clk_gpio` holds a GPIO descriptor and clock hardware. Gate ops are split between non-sleeping GPIO `.enable/.disable` and sleeping GPIO `.prepare/.unprepare`. Mux ops use `gpiod_get_value_cansleep()` and `gpiod_set_value_cansleep()`. `struct clk_gated_fixed` adds `supply` and `rate`; its ops combine regulator prepare state, GPIO output state, and fixed-rate recalc.

Control flow: `gpio_clk_driver_probe()` distinguishes `"gpio-mux-clock"` from `"gpio-gate-clock"`, validates mux parent count, gets the `select` or `enable` GPIO, registers a clock with parent data indexes, and publishes an OF provider. `clk_gated_fixed_probe()` reads `clock-frequency`, optional `clock-output-names`, optional `vdd` regulator, optional enable GPIO, selects sleeping or non-sleeping ops, registers the fixed clock, and publishes it.

State and persistence: clock state is GPIO output level and optional regulator enable state. Rate is stored in memory from firmware properties. There is no persistent software state across probe removal except hardware pin/regulator state managed by devres and providers.

Dependencies and integration points: depends on GPIO descriptor APIs, regulator framework, device properties, OF clock provider helpers, and common clock parent-data support. Built-in platform drivers bind DT-compatible nodes.

Risks and test signals: sleeping GPIOs must only be toggled in prepare paths; non-sleeping gates use enable paths. `clk_sleeping_gated_fixed_unprepare()` disables regulator before lowering GPIO, which may matter electrically. Mux requires exactly two parents. Test signals are DT probe, GPIO polarity behavior from descriptors, regulator enable/disable balance, and child clock parent/rate observations.
