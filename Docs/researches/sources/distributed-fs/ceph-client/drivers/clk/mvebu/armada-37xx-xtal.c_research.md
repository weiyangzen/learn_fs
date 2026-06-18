# sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-37xx-xtal.c

Purpose: Armada 37xx XTAL clock provider that chooses 25 MHz or 40 MHz from a latched strap bit.

Important APIs/functions: `armada_3700_xtal_clock_probe` reads `NB_GPIO1_LATCH` via parent syscon, registers a fixed-rate clock, and adds a simple OF provider. `armada_3700_xtal_clock_remove` deletes the provider.

Control flow: probe validates parent node, obtains regmap, reads latch bit `XTAL_MODE`, selects rate, optionally reads `clock-output-names`, registers fixed-rate `xtal`, and publishes it.

State and persistence: fixed rate is sampled once at probe from latch hardware; no software state beyond the `clk_hw` pointer is needed.

Dependencies and integration: syscon parent, platform driver matching `marvell,armada-3700-xtal-clock`, CCF fixed-rate provider, TBG parent linkage.

Risks: initial devm allocation of `clk_hw` is overwritten by `clk_hw_register_fixed_rate`, making the allocation unnecessary. Remove deletes provider but does not unregister the fixed-rate clock.

Test signals: strap variants for 25/40 MHz, TBG downstream rates, provider remove/reprobe checks, and DT `clock-output-names` handling.
