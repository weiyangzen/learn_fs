<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8135.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8135.c

Purpose: This is the main MT8135 clock controller driver for topckgen, infracfg, and pericfg. It describes fixed PLL factors, top-level mux composites, infrastructure gates, peripheral gates, a UART peripheral composite, and reset controllers.

Important APIs, types, and functions: `top_divs` derives divided clocks from apmixedsys PLLs; many parent arrays feed `top_muxes`; `infra_clks` and `peri_gates` use `mtk_gate` definitions; `peri_clks` adds a UART selector. `infra_desc`, `peri_desc`, and `topck_desc` are selected by OF compatibles `mediatek,mt8135-infracfg`, `mediatek,mt8135-pericfg`, and `mediatek,mt8135-topckgen`. Reset descriptors cover infra and peri reset banks.

Control flow: `mtk_clk_simple_probe` matches a compatible string, selects the descriptor, registers factors/composites/gates/resets under the shared `mt8135_clk_lock` where needed, and exposes an OF clock provider. Consumers access clock IDs from `dt-bindings/clock/mt8135-clk.h`.

State and persistence behavior: Clock state is hardware MMIO state in topckgen/infracfg/pericfg registers plus volatile provider registrations. Reset-controller state is also register-backed. No persistent configuration is stored by the driver.

Dependencies and integration points: The file depends on MediaTek common clock/gate helpers, `clk-pll.h` parents provided by `clk-mt8135-apmixedsys.c`, syscon/reset infrastructure, and DT bindings. It integrates with CPU/bus, display, camera, VDEC/VENC, storage, USB, UART/SPI, PMIC wrapper, and memory-subsystem consumers.

Risks and edge cases: The file is table-dense; parent array order, mux field width, gate polarity, and reset bank offsets must match the SoC manual. Several muxes select display/video PLLs, making bad parents visible as display or codec instability. Shared registers require the lock to avoid read-modify-write races.

Test signals: Check all three compatibles bind, reset controls appear, clock summary shows expected parent trees, UART/SPI/MSDC/USB/display/video consumers probe, mux switching works under load, and remove unregisters providers without leaked clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8135.c -->
