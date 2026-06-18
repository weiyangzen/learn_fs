# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779.c

## Purpose

This is the main MT6779 clock driver. It registers topckgen clocks, apmixed PLLs, apmixed 26 MHz gates, and infracfg always-on gates for a mobile SoC. The top side exposes a large rate tree made from fixed factors, muxes with update bits, and audio mux/divider composites. The infracfg side exposes peripheral and system bus gates for PMIC, GCE, I2C, PWM, UART, MSDC, UFS, USB, security, modem, audio, and ADSP paths.

## Important APIs, types, and functions

Important local objects are `top_fixed_clks`, `top_divs`, many `*_parents` arrays, `top_muxes`, `top_aud_muxes`, `top_aud_divs`, `infra_clks`, `apmixed_clks`, and `plls`. The registration entry points are `clk_mt6779_apmixed_probe()`, `clk_mt6779_top_probe()`, `clk_mt6779_probe()`, and the `clk_mt6779_init()` `arch_initcall`. The driver uses `struct mtk_pll_data`, `struct mtk_mux`, `struct mtk_composite`, `struct mtk_gate`, `struct mtk_gate_regs`, and `struct mtk_clk_desc`.

## Control flow, state, and persistence

`clk_mt6779_init()` registers two platform drivers: the match-data dispatcher for `"mediatek,mt6779-apmixed"` and `"mediatek,mt6779-topckgen"`, plus a separate simple infracfg driver for `"mediatek,mt6779-infracfg_ao"`. Topckgen maps the MMIO resource, allocates `CLK_TOP_NR_CLK` onecell data, registers fixed clocks, factors, muxes under `mt6779_clk_lock`, and audio composites before adding the OF provider. APMIXED allocates `CLK_APMIXED_NR_CLK`, registers PLLs and apmixed gates, then publishes the provider. Infra uses `mtk_clk_simple_probe()` with `infra_desc`. Runtime state is hardware register state and common-clock registrations; the driver does not persist state across reboot.

## Dependencies and integration points

The file depends on `clk-mtk.h`, `clk-gate.h`, `clk-mux.h`, `clk-pll.h`, and `dt-bindings/clock/mt6779-clk.h`. It integrates with device-tree compatible strings, Linux CCF provider lookup, and consumers in display, camera, audio, storage, USB, UFS, modem, ADSP, and security blocks. Critical clocks include `axi_sel`, `spm_sel`, `sspm_sel`, and `apmixed_appll26m`, which are marked to avoid disabling bus/co-processor/PLL-root paths.

## Risks and test signals

The biggest risks are parent-name mismatches, wrong mux update offsets, gate polarity mistakes, and accidentally losing `CLK_IS_CRITICAL` on bus or always-on clocks. Probe error paths are sparse and do not unregister all prior allocations on every later failure. Test by booting MT6779 device trees, checking `/sys/kernel/debug/clk/clk_summary`, probing display/camera/audio/UFS/USB paths, and verifying no clk disable warning or hang occurs when unused clocks are disabled.
