# sources/distributed-fs/ceph-client/drivers/clk/davinci/pll.c

Purpose: implements the generic DaVinci PLL common-clock provider, including PLLOUT, optional pre/post dividers, PLLEN bypass control, AUXCLK, SYSCLKBP, OBSCLK, SYSCLKn, OF registration, platform probing, and debugfs register exposure.

Important APIs/types/functions: main types are `davinci_pll_clk` and `davinci_pllen_clk`. PLL ops include recalc, determine, and set-rate; DM365 has a 2x multiplier recalc variant. `davinci_pll_div_register()` builds gate+divider composites. Public registration functions include `davinci_pll_clk_register()`, `davinci_pll_auxclk_register()`, `davinci_pll_sysclkbp_clk_register()`, `davinci_pll_obsclk_register()`, `davinci_pll_sysclk_register()`, and `of_davinci_pll_init()`.

Control flow: `davinci_pll_clk_register()` optionally creates `oscin`, prediv, PLLOUT, postdiv, and PLLEN. A PLLEN notifier switches to bypass before parent/PLL rate changes, resets and relocks the PLL, then re-enables PLL mode. SYSCLK notifiers wait for pending GO operations and trigger `PLLCMD_GOSET` after divider changes. OF init registers child providers for `pllout`, `sysclk`, `auxclk`, and `obsclk`. The platform driver maps registers and dispatches DA850 init callbacks.

State and persistence: hardware register state lives in PLL MMIO; software state is allocated `clk_hw` wrappers and notifier blocks. There is no suspend persistence layer.

Dependencies and integration points: depends on clk composite/gate/divider/mux helpers, OF providers, regmap/syscon for CFGCHIP unlock, platform IDs, `postcore_initcall()`, and DA850 callbacks from `pll-da850.c`.

Risks: busy waits use unbounded `regmap_read_poll_timeout(..., 0, 0)` for SYSCLK/PSC-style waits in related paths, so stuck hardware can hang. Some allocations are not devm-managed and unregister paths are only partial error unwind. Rate setting writes PLLM directly and relies on notifier ordering for safe bypass. Debugfs regset allocation is not explicitly freed.

Test signals: exercise PLL rate changes, prediv/postdiv read-only flags, SYSCLK divider updates with GO synchronization, OF child providers, error unwinds on failed clock registration, and debugfs register visibility.
