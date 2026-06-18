<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-pericfg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-pericfg.c

Purpose: This driver registers MT8173 peripheral configuration clocks and resets for UART, I2C, PWM, SPI, MSDC, NFI, USB, and related peripheral buses.

Important APIs, types, and functions: `peri0_cg_regs` and `peri1_cg_regs` back `peri_gates`. `peri_clks` adds peripheral composites such as UART clock selection. `peri_desc` includes gates, composites, `mt8173_clk_lock`, and `clk_rst_desc`. It binds `mediatek,mt8173-pericfg`.

Control flow: `mtk_clk_simple_probe` registers gates, composites, and reset controller from the descriptor and publishes an OF provider. Consumers request clocks and resets using MT8173 binding IDs.

State and persistence behavior: Gate, mux, and reset states live in pericfg registers. Provider state is runtime-only. The spinlock protects shared composite register updates.

Dependencies and integration points: It depends on MediaTek gate/composite/reset helpers, DT bindings, and topckgen parents. It supports serial, I2C, SPI, PWM, MSDC, NAND, USB, and PMIC-related drivers.

Risks and edge cases: Peripheral boot dependencies make missing clocks obvious as deferred probes. Reset descriptor offsets must align with reset bindings. Composite parent order affects UART/peripheral baud generation.

Test signals: Probe serial/I2C/SPI/MSDC/USB devices, reset assertions through reset consumers, clk summary gate toggles, mux rate validation, and driver removal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-pericfg.c -->
