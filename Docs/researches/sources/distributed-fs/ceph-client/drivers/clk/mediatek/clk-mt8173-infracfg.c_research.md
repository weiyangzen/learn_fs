<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-infracfg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-infracfg.c

Purpose: This driver handles MT8173 infracfg clocks, including early fixed factors, CPU muxes, infrastructure gates, and the infracfg reset controller.

Important APIs, types, and functions: `infra_early_divs` creates `clk13m`; `cpu_muxes` expose CA53 and CA72 CPU selectors; `infra_gates` covers debug, SMI, audio, GCE, M4U, CPUM, keypad, CEC, PMIC SPI, and PMIC wrapper gates. `clk_rst_desc` registers simple reset banks. The early `CLK_OF_DECLARE_DRIVER` path runs `mt8173_infracfg_init` before the platform driver.

Control flow: Early init allocates shared `infra_clk_data`, registers early factors, and publishes an OF provider so early consumers can resolve clocks. Later platform probe reuses or allocates the same data, registers gates and CPU muxes, refreshes the provider, and registers resets. Remove unregisters CPU muxes and gates.

State and persistence behavior: A global `infra_clk_data` pointer bridges early and platform phases. Hardware gate/mux/reset bits are volatile. Provider data persists for the device lifetime.

Dependencies and integration points: It depends on `of_clk_hw_onecell_get`, MediaTek factor/gate/cpumux/reset helpers, MT8173 bindings, and early boot clock users. It feeds CPU cluster, SMI/M4U, audio, GCE, PMIC wrapper, and reset consumers.

Risks and edge cases: The two-phase init must not double-allocate or leak clock data. Provider replacement/removal ordering matters. CPU mux registration is sensitive to parent order and may affect live CPU frequency paths.

Test signals: Early boot without deferred clock failures, CPU frequency/cluster mux operation, reset-controller consumers, infracfg gate toggling, and remove cleanup after early provider registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-infracfg.c -->
