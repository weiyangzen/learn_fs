<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-sdmmc-mux.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-sdmmc-mux.c

Purpose: implements the Tegra SDMMC mux/divider composite used by newer Tegra SD/MMC clocks that have two different hardware parent selector encodings depending on whether the fractional divider is zero. It wraps parent muxing, an 8-bit fractional divider, and a Tegra peripheral gate into one Common Clock Framework clock.

Important APIs, types, and functions: `tegra_clk_register_sdmmc_mux_div()` is the exported constructor declared in `clk.h` and used by Tegra210 for SDMMC instances. The implementation stores state in `struct tegra_sdmmc_mux`: `reg`, optional `lock`, `div_flags`, embedded `tegra_clk_periph_gate`, and delegated `gate_ops`. Core callbacks are `clk_sdmmc_mux_get_parent()`, `set_parent()`, `determine_rate()`, `recalc_rate()`, `set_rate()`, gate passthrough callbacks, and `restore_context()`.

Control flow: parent lookup reads `reg`, extracts bits 31:29, and maps the raw selector through `mux_lj_idx` when divider bits are zero or `mux_non_lj_idx` when nonzero. Rate calculation uses `rate = parent_rate * 2 / (div + 2)` with rounding behavior selected by `TEGRA_DIVIDER_ROUND_UP`. `set_rate()` computes the fractional divider with `div_frac_get()`, locks if provided, translates the current logical parent to the matching raw low-jitter or non-low-jitter selector, writes selector plus divider as one register value, and fences with `fence_udelay(2, reg)`. Gate operations call the normal Tegra peripheral gate ops after binding the embedded gate hw to the composite clock.

State and persistence: persistent state is hardware register contents plus the global `periph_clk_enb_refcnt` array. The C object is allocated for the lifetime of the clock and freed only on registration failure. Suspend/resume context is restored by replaying parent and rate from CCF state, which is important because raw parent encoding changes with divider mode.

Dependencies and integration: depends on `clk.h` helpers, `get_reg_bank()`, `tegra_clk_periph_gate_ops`, `periph_clk_enb_refcnt`, and `div_frac_get()`. The fixed parent list is `"pll_p", "pll_c4_out2", "pll_c4_out0", "pll_c4_out1", "clk_m"` and must match hardware selector tables.

Risks and test signals: risks are off-by-one selector table errors, changing divider without translating selector encoding, missing locking with shared CAR registers, and invalid `clk_num` bank lookup. Test by switching all parents with divider zero and nonzero, verifying SDMMC rates against register values, checking gate enable/disable/reset behavior, and running suspend/resume while an SDMMC clock uses both low-jitter and divided modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-sdmmc-mux.c -->
