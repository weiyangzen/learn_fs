# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8mq.c

## Purpose
Registers the i.MX8MQ CCM clock tree. It exposes oscillator inputs, ANATOP PLLs, SSCG PLLs, fixed PLL derivatives, composite core/bus/IP roots, CCGR-style gates, monitor outputs, and the CPU clock to the common clock framework through the `fsl,imx8mq-ccm` provider.

## Important APIs, Types, And Functions
The main entry point is `imx8mq_clocks_probe()`. It allocates `struct clk_hw_onecell_data`, fills the global `hws` array indexed by `dt-bindings/clock/imx8mq-clock.h`, maps ANATOP and CCM register ranges, registers clocks through helpers from `clk.h`, calls `imx_check_clk_hws()`, and publishes `of_clk_hw_onecell_get`. The file is table-heavy: parent selector arrays describe mux inputs for PLLs, A53, M4, VPU, GPU, NOC, DRAM, display, PCIe, SAI, SPDIF, ENET, NAND, USDHC, I2C, UART, USB, CSI, DSI, CLKO, and PLL monitor outputs.

Key helpers used here include `imx_clk_hw_frac_pll()`, `imx_clk_hw_sscg_pll()`, `imx8m_clk_hw_composite*()`, `imx_clk_hw_mux*()`, `imx_clk_hw_gate*()`, `imx_clk_hw_fixed_factor()`, `imx8m_clk_hw_fw_managed_composite*()`, and `imx_clk_hw_cpu()`.

## Control Flow
Probe initializes dummy and external clocks from device tree names, maps `fsl,imx8mq-anatop`, builds PLL reference muxes/dividers/PLLs/bypass muxes/output gates, creates fixed SYS PLL outputs, and registers PLL monitor mux/dividers. It then maps the CCM resource, registers core, bus, AHB/IPG, DRAM, IP, peripheral, root-gate, and CPU clocks. On provider registration failure or mapping failure it jumps to `unregister_hws` and unregisters the array.

## State And Persistence Behavior
The persistent hardware state is CCM/ANATOP register content; kernel state is the allocated `clk_hw` graph and static shared-gate counters for SAI, display, and NAND gates sharing physical bits. DRAM clocks are flagged firmware-managed / no-cache because TF-A may alter their registers outside Linux.

## Dependencies And Integration Points
Depends on the common clock framework, OF platform probing, i.MX clock helpers, `imx8mq-clock.h`, ANATOP compatible lookup, CCM MMIO, and consumers that request clocks by DT index. It calls `imx_register_uart_clocks()` for serial clock integration.

## Risks
Risks are incorrect DT binding indexes, parent name drift, wrong register offsets or gate sharing, and critical-clock flag mistakes on NOC/AHB/GIC/DRAM paths. Reload is suppressed because clocks are not fully removable. Firmware-managed DRAM paths must remain uncached and must not assume Linux owns parent/divider state.

## Test Signals
Boot an i.MX8MQ DT and verify no missing-clock warnings, `clk_summary` topology/rates, UART console, CPU frequency clock, display/VPU/GPU/CSI/DSI/PCIe peripherals, suspend/resume with DRAM rates, and failure-path coverage for missing ANATOP/CCM resources.
