# sources/distributed-fs/ceph-client/drivers/clk/eswin/clk-eic7700.c

Purpose: describes and registers the ESWIN EIC7700 clock tree, including fixed rates, programmable PLLs, fixed factors, dividers, gates, muxes, and CPU PLL rate-change protection.

Important APIs/types/functions: descriptor arrays are `eic7700_fixed_rate_clks`, `eic7700_pll_clks`, `eic7700_factor_clks`, `eic7700_div_clks`, `eic7700_gate_clks`, `eic7700_early_clks`, `eic7700_mux_clks`, and `eic7700_clks`. `eic7700_clk_pll_cpu_notifier_cb()` temporarily switches the CPU root mux to low-power fixed-factor input while `clk_pll_cpu` changes. `eic7700_clk_probe()` registers all descriptors and publishes an OF onecell provider.

Control flow: probe allocates `EIC7700_NR_CLKS`, registers fixed-rate roots, PLLs, the CPU PLL notifier, factors, simple dividers/gates, early composite descriptors needed as mux parents, muxes, then the remaining derived clocks. Consumers retrieve clocks by IDs from `dt-bindings/clock/eswin,eic7700-clock.h`.

State and persistence: register state lives in the SYS-CRG MMIO range. Runtime state includes `eswin_clock_data`, `clk_hw` arrays, and the saved CPU mux parent during PLL transitions.

Dependencies and integration points: depends on the shared ESWIN helpers in `clk.c`, common-clock APIs, OF platform probing, and DT binding IDs. Many gates use `CLK_IGNORE_UNUSED` where clocks must remain on for CPUs, UARTs, DDRT, and timer paths.

Risks: the file is table-heavy; ID/parent ordering mistakes can silently wire a clock to the wrong parent. Some fixed-rate entries are declared with rate 0 (`APLL_FOUT2`, `APLL_FOUT3`, `EXT_MCLK`), so consumers must not assume valid rates unless hardware/DT updates them elsewhere. The CPU notifier assumes `eic7700_mux_clks[0]` and `eic7700_early_clks[11]` remain specific clocks.

Test signals: probe with DT, enumerate all clock IDs, run CPU PLL rate changes under load, verify protected parent switch/restore, check critical/ignore-unused clocks survive late init, and compare clock summary rates with the SoC manual.
