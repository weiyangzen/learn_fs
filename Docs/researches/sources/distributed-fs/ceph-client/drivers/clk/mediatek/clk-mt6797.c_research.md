# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6797.c

## Purpose

This is the main MT6797 clock driver for topckgen, infracfg, and apmixedsys. It registers fixed PLL-derived factors, top muxes, infrastructure gates/factors, and PLLs for the SoC. It also has an early infracfg provider path so early boot consumers can defer safely until the full platform driver registers gates.

## Important APIs, types, and functions

Important data includes `top_fixed_divs[]`, many parent arrays, `top_muxes[]`, `infra_clks[]`, `infra_fixed_divs[]`, global `infra_clk_data`, and `plls[]`. Entry points are `mtk_topckgen_init()`, `mtk_infrasys_init_early()`, `mtk_infrasys_init()`, `mtk_apmixedsys_init()`, `clk_mt6797_probe()`, and `clk_mt6797_init()`. The early hook uses `CLK_OF_DECLARE_DRIVER()` for `"mediatek,mt6797-infracfg"`.

## Control flow, state, and persistence

The `arch_initcall` registers one platform driver whose match data selects the init routine for topckgen, infracfg, or apmixedsys. Topckgen maps MMIO, allocates `CLK_TOP_NR`, registers factors and composites, then publishes a provider. Early infracfg allocates global onecell data, fills entries with `ERR_PTR(-EPROBE_DEFER)`, registers `clk13m`, and publishes the provider. Full infracfg replaces defers with `-ENOENT`, registers gates/factors, and adds the provider. APMIXED registers PLLs. State is global CCF provider data and hardware register state.

## Dependencies and integration points

Dependencies include `clk-gate.h`, `clk-mtk.h`, `clk-pll.h`, OF platform support, and `dt-bindings/clock/mt6797-clk.h`. Critical infrastructure gates `infra_dramc_f26m` and `infra_dramc_b_f26m` protect DRAM clocks, and `ddrphycfg_sel` is critical to avoid boot hangs. Consumers include core buses, storage, USB, display, media, audio, PMIC, security, and modem interfaces.

## Risks and test signals

Risks include early-provider lifetime issues, duplicate `of_clk_add_hw_provider()` for infracfg, missing critical flags, and lack of unregister/error cleanup. Test early boot without probe deferrals, DRAM stability, full clock summary, media/storage/USB/audio devices, and suspend/resume.
