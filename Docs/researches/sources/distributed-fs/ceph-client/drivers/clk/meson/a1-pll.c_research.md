# sources/distributed-fs/ceph-client/drivers/clk/meson/a1-pll.c

Purpose: `a1-pll.c` is the Amlogic A1 PLL clock-controller driver. It exposes fixed PLL, hifi PLL, and fixed-factor fclk divider outputs used as parents by the A1 peripheral clock controller.

Important APIs and types: the file uses Meson `struct clk_regmap` PLL and gate descriptors, `struct clk_fixed_factor` for fclk divisions, `struct meson_clk_pll_data`, and `struct meson_clkc_data`. It registers a platform driver named `a1-pll-clkc` and delegates probe to `meson_clkc_mmio_probe`.

Control flow: static descriptors define `fixed_pll_dco` as a read-only PLL from `fixpll_in`, gate it as `fixed_pll`, derive fclk div2/div3/div5/div7 fixed factors from it, and gate each output. `hifi_pll` is a programmable PLL from `hifipll_in` with init register sequences and an M range of 32 to 64. The OF match table for `"amlogic,a1-pll-clkc"` passes `a1_pll_clkc_data` to the common MMIO probe.

State and persistence: runtime state lives in ANACTRL PLL registers and CCF registration structures. `fclk_div2`, `fclk_div3`, and `fclk_div5` are marked `CLK_IS_CRITICAL` because boot firmware or platform buses depend on them. No storage persists beyond hardware state.

Dependencies and integration points: it depends on Meson `clk-pll`, `clk-regmap`, and `meson-clkc-utils`, plus binding IDs from `amlogic,a1-pll-clkc.h`. It supplies firmware-name parents such as `fclk_div2` and `hifi_pll` consumed by `a1-peripherals.c`.

Risks: PLL init sequences and bit fields must match the A1 analog controller. Critical flags keep important clocks enabled but can mask missing ownership handoff. `fixed_pll_dco` is read-only, so attempts to change derived rates must resolve through allowed dividers or hifi PLL paths.

Test signals: `clk_summary` should show fixed PLL DCO, fixed PLL, fclk dividers, and hifi PLL at expected rates. Rate-change tests should cover hifi PLL programming and lock status. Boot tests should confirm DDR/APB/AXI dependent fclk outputs remain enabled.
