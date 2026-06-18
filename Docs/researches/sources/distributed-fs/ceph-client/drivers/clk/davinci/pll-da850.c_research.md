# sources/distributed-fs/ceph-client/drivers/clk/davinci/pll-da850.c

Purpose: provides DA850/OMAP-L138/AM18xx-specific PLL descriptors, SYSCLK definitions, OBSCLK parent tables, and init routines consumed by the generic DaVinci PLL driver.

Important APIs/types/functions: `da850_pll0_info` and `da850_pll1_info` describe PLL masks, unlock registers, multiplier limits, output ranges, and quirks. `SYSCLK()` definitions create `pll0_sysclk1..7` and `pll1_sysclk1..3`. `da850_pll0_init()`, `of_da850_pll0_init()`, `da850_pll1_init()`, and `of_da850_pll1_init()` register clocks and clkdev aliases.

Control flow: PLL0 registration creates the PLL tree from `ref_clk`, registers seven sysclks, AUXCLK, an `async2` fixed-factor alias, and OBSCLK. PLL1 registration uses `oscin` as parent and registers three sysclks plus OBSCLK. OF init uses `of_davinci_pll_init()` with sysclk arrays and max IDs; platform init manually installs clkdev aliases for PSCs and legacy devices.

State and persistence: no independent mutable state; it programs hardware through generic PLL helpers and persists clock topology through registered `clk` objects and providers.

Dependencies and integration points: uses CFGCHIP unlock masks, DT bindings, `clkdev`, syscon lookup for `ti,da830-cfgchip`, and the generic declarations in `pll.h`. PSC and CFGCHIP providers consume names such as `pll0_sysclk2`, `pll0_sysclk4`, `async2`, and `pll1_sysclk2`.

Risks: init routines ignore some returned errors after registration, so missing clock nodes may surface later as consumer probe failures. Fixed-ratio SYSCLKs are treated read-only even though hardware may allow coordinated ratio changes. Legacy aliases encode specific device names and can break if platform device names drift.

Test signals: boot DA850 with DT and non-DT paths, inspect `/sys/kernel/debug/clk/clk_summary`, verify PSC parent lookups, test CPU/ARM SYSCLK rate changes, and confirm CFGCHIP unlock bits allow PLL programming.
