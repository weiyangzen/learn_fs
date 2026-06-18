# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rv1126b.c

Purpose: RV1126B clock controller description and init code. It declares PLL rate tables, CPU clock rate/divider tables, parent-name arrays, and a large `rv1126b_clk_branches[]` topology for top, bus, peri, core, PMU, PMU1, DDR, VI, VEPU, NPU, VDO, and VCP CRU islands.

Important APIs/types/functions: uses Rockchip CCF macros from `clk.h`: `PLL`, `COMPOSITE`, `COMPOSITE_FRAC`, `COMPOSITE_FRACMUX_NOGATE`, `COMPOSITE_NODIV`, `GATE`, `DIV`, `FACTOR`, `MUX`, and `PNAME`. `rv1126b_clk_init()` is the central entry point. `clk_rv1126b_probe()` dispatches platform-device probing through `device_get_match_data()`. `CLK_OF_DECLARE()` and `builtin_platform_driver_probe()` provide early DT and platform-driver registration.

Control flow: init computes the onecell size with `rockchip_clk_find_max_clk_id()`, maps the CRU registers with `of_iomap()`, creates a provider with `rockchip_clk_init()`, registers PLLs, branches, the multi-PLL ARM clock, reset lookup table, restart handler, and OF clock provider, then writes five PVTPLL source-select registers.

State and persistence: state is hardware-backed CRU register state plus the in-memory onecell clock lookup table. PLLs and gates marked `CLK_IS_CRITICAL` are expected to stay enabled. No runtime persistence exists beyond programmed registers.

Dependencies and integration: depends on `dt-bindings/clock/rockchip,rv1126b-cru.h`, `rv1126b_rst_init()`, Rockchip common clock helpers, Linux CCF, OF, platform-device, and restart notifier integration. Consumers bind through compatible `rockchip,rv1126b-cru`.

Risks: the branch table is dense and register-bit oriented; a wrong parent array, divider width, gate bit, or `CLK_IS_CRITICAL` flag can break boot, display, storage, DDR, NPU/video, or PMU operation. The final direct `writel_relaxed()` PVTPLL selects bypass normal CCF registration and need hardware validation.

Test signals: boot on RV1126B with clock provider present, `/sys/kernel/debug/clk/clk_summary` parent/rate checks, reset-controller phandle use, restart path, UART/storage/display/audio operation, and exercising rate changes on CPU, fractional UART/audio clocks, and PVTPLL-rooted domains.
