# sources/distributed-fs/ceph-client/drivers/clk/nxp/clk-lpc18xx-creg.c

Purpose: Provides LPC18xx/LPC43xx CREG-derived 32 kHz and 1 kHz clocks. The 32 kHz clock must be available early, while the 1 kHz divided clock is registered later by a platform driver.

Important APIs, types, and functions: `struct clk_creg_data` stores clock hardware, name, syscon regmap, enable mask, and ops. `clk_creg_32k_prepare()` powers up and releases reset for the 32 kHz oscillator, then sleeps 2500 ms. `clk_creg_1k_recalc_rate()` returns `parent / 32`. `clk_register_creg_clk()` registers a CREG clock.

Control flow: `CLK_OF_DECLARE_DRIVER()` runs `lpc18xx_creg_clk_init()` early, looks up the parent syscon, registers only the 32 kHz clock, and leaves the 1 kHz slot as `-EPROBE_DEFER`. `builtin_platform_driver()` later runs `lpc18xx_creg_clk_probe()`, reuses the early 32 kHz clock, registers the 1 kHz clock with 32 kHz as parent, and replaces the OF provider data.

State and persistence: Static arrays hold early and final clock pointers. Enable and prepare state persist in the parent syscon register `CREG0`.

Dependencies and integration points: Depends on a syscon parent node, a DT parent for the 32 kHz source, CCF, and regmap. Consumers may request the 32 kHz clock before platform driver probe.

Risks: Preparing the 32 kHz oscillator blocks for 2.5 seconds because there is no status bit. `lpc18xx_creg_clk_probe()` uses `clk_register_creg_clk(NULL, ...)` rather than devm despite being in a platform probe, so clocks persist globally. Provider replacement must not break early consumers.

Test signals: Early consumers should resolve the 32 kHz clock; 1 kHz consumers should defer until platform probe. Enable/disable should update `EN32KHZ` and `EN1KHZ`. Prepare should clear `PD32KHZ` and `RESET32KHZ`.
