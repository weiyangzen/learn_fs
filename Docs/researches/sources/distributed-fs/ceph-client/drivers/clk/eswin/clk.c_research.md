# sources/distributed-fs/ceph-client/drivers/clk/eswin/clk.c

Purpose: provides shared ESWIN common-clock helper registration plus custom PLL and divider implementations.

Important APIs/types/functions: `eswin_clk_init()` allocates `eswin_clock_data` and maps the MMIO resource. PLL ops implement `clk_pll_set_rate()`, `clk_pll_recalc_rate()`, and `clk_pll_determine_rate()`. Helper exports register fixed-rate, PLL, fixed-factor, mux, divider, gate, and mixed `eswin_clk_info` descriptors. `eswin_register_clkdiv()` registers the custom private divider used when `ESWIN_PRIV_DIV_MIN_2` is required.

Control flow: PLL set-rate computes fbdiv/frac from requested rate and parent, disables the PLL, writes refdiv/fbdiv/frac/postdiv fields, re-enables it, and polls lock. Registration functions iterate descriptor arrays, create devm-managed `clk_hw` objects, and store them in the onecell `hws` array.

State and persistence: runtime state is devm-managed provider data and MMIO-backed register contents. A spinlock in `eswin_clock_data` serializes mux/divider/gate read-modify-write cycles.

Dependencies and integration points: uses `bitfield.h`, `iopoll.h`, common-clock devm helpers, platform resource mapping, and descriptor types from `common.h`. Exports GPL symbols used by the EIC7700 provider.

Risks: `eswin_clk_init()` converts any ioremap error to `-EINVAL`, losing the original reason. Custom divider math has a potential divide-by-zero path in `eswin_clk_bestdiv()` when `down` becomes zero for rates above parent. PLL set-rate hardcodes refdiv/postdiv values and polls only 100 microseconds total, so marginal hardware could fail. `eswin_clk_register_fixed_factor()` assumes `parent_data->index` rather than full parent data.

Test signals: unit-style rate tests for PLL and private divider math, lock-timeout error injection, concurrent gate/mux/divider operations, probe failure with missing resource, and module build/export checks.
