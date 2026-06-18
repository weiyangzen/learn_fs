# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos-audss.c

## Purpose

`clk-exynos-audss.c` is a platform clock driver for the Exynos audio subsystem clock controller. It registers a onecell clock provider containing audio muxes, dividers, and gates for Exynos4210/5250/5410/5420-style AUDSS blocks, with variant flags for ADMA, MST, EPLL enablement, and clock count differences.

## Important APIs, types, and functions

- File-scope `lock`, `reg_base`, `clk_data`, and `epll` hold the register lock, mapped registers, onecell provider, and optional EPLL clock.
- `ASS_CLK_SRC`, `ASS_CLK_DIV`, and `ASS_CLK_GATE` are the three AUDSS registers.
- `reg_save` persists those three register values across PM.
- `struct exynos_audss_clk_drvdata` describes variant features. `has_adma_clk`, `enable_epll`, and `num_clks` are used; `has_mst_clk` is set for Exynos5410 but not otherwise consumed here.
- `exynos_audss_clk_probe()` maps registers, resolves optional parents, enables EPLL when required, registers mux/divider/gate clocks, adds the OF provider, and enables runtime PM.
- `exynos_audss_clk_teardown()` unregisters clocks by ID range and type.
- `exynos_audss_clk_suspend()` / `exynos_audss_clk_resume()` save and restore registers.
- `exynos_audss_clk_remove()` removes the provider, unregisters clocks, disables runtime PM, and disables EPLL if enabled.

## Control flow

Probe selects variant data from OF match, maps MMIO, initializes `epll` to `-ENODEV`, and allocates a `clk_hw_onecell_data` table. Optional `pll_ref` and `pll_in` clocks override default `mout_audss` parents; `pll_in` is prepared/enabled for variants with `enable_epll`.

Runtime PM is enabled while holding a noresume usage count to keep the device active during provider setup. The driver registers `mout_audss`, `mout_i2s`, `dout_srp`, `dout_aud_bus`, `dout_i2s`, gates for SRP/I2S/PCM, and optionally ADMA. Optional `cdclk`, `sclk_audio`, and `sclk_pcm_in` override parent names. After checking all exposed entries, it publishes the provider and drops the runtime PM usage count. Failure paths unregister clocks, disable PM, and unprepare EPLL.

## State and persistence behavior

State is file-global, so the implementation assumes a single AUDSS instance. Registered clock hardware is stored in devm-allocated onecell data but explicitly unregistered. The three hardware registers are saved/restored on runtime suspend/resume, and late system sleep delegates to runtime PM force suspend/resume. EPLL prepare/enable is balanced on remove and probe failure.

## Dependencies

The driver depends on `dt-bindings/clock/exynos-audss-clk.h`, platform-device probing, OF match data, MMIO resources, CCF mux/divider/gate registration helpers, runtime PM, and optional named parent clocks (`pll_ref`, `pll_in`, `cdclk`, `sclk_audio`, `sclk_pcm_in`).

## Risks and edge cases

- File-scope globals make multiple AUDSS instances unsafe.
- `has_mst_clk` is declared but unused.
- Teardown relies on clock ID ordering by type.
- Optional parent lookup failures silently leave default parent names.
- PM callbacks access registers through global `reg_base`; PM ordering must ensure register access is valid.
- Any new failure path after EPLL enablement must preserve disable/unprepare balance.

## Test signals

Runtime validation should probe each compatible, inspect `clk_summary` for expected clocks/parents, exercise I2S/PCM/SRP audio, verify ADMA clock presence on Exynos5420, and run runtime plus system suspend/resume while confirming `ASS_CLK_SRC`, `ASS_CLK_DIV`, and `ASS_CLK_GATE` restore correctly.
