# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8mn.c

## Purpose
This platform driver registers the i.MX8M Nano CCM clock tree. It is structurally similar to the i.MX8MM provider but adjusted for Nano hardware: M7 instead of M4 naming, GPU core/shader clocks, a reduced/changed multimedia set, SAI2/3/5/6/7, six GPTs, camera/display pixel roots, and Nano-specific PLL names.

## Important APIs, Types, And Functions
`imx8mn_clocks_probe()` is bound to `fsl,imx8mn-ccm`. It allocates `struct clk_hw_onecell_data` with `devm_kzalloc()`, fills global `hws`, maps `fsl,imx8mn-anatop` with `devm_of_iomap()`, maps the CCM resource, and registers PLL14xx, fixed-factor, composite, gate, shared gate, and CPU clocks. It uses `imx8m_clk_hw_fw_managed_composite()` for DRAM paths, `imx8m_clk_hw_composite_bus_critical()` for key buses, and `imx_clk_hw_cpu()` for the ARM clock.

## Control Flow
Probe creates dummy/external clocks, registers audio/video/DRAM/GPU/M7_ALT/ARM/SYS_PLL3 PLLs and bypass/output gates, derives fixed SYS_PLL1/2 rates, and creates CLKOUT1/2. It then registers core composites for A53, M7, GPU core, and GPU shader, aliases GPU source/gate/div IDs to the composite hardware, creates the A53 core selector, bus and AHB/audio roots, IPG dividers, critical DRAM core mux, firmware-managed DRAM alt/APB clocks, peripheral composites, CCGR gates, shared NAND/SAI/PDM/display gates, fixed GPT 3 MHz and DRAM alternate roots, and the CPU clock. It validates, publishes the provider, and registers UART clocks.

## State And Persistence
Clock state persists in anatop/CCM registers. Global `clk_hw_data`/`hws` live for the module lifetime, and bind attributes are suppressed to avoid unbinding a provider whose clocks are in use. Shared counters guard SAI root/IPG pairs, SAI7, PDM, display/camera pixel group, and NAND. DRAM alt/APB clocks are firmware-managed because TF-A may alter them outside Linux.

## Dependencies And Integration Points
Dependencies are `dt-bindings/clock/imx8mn-clock.h`, compatibles `fsl,imx8mn-anatop` and `fsl,imx8mn-ccm`, external clock names, PLL14xx definitions, and the i.MX8M composite helper API. Device drivers consume the exported onecell clock IDs for display, camera, GPU, USB, ENET, USDHC, serial, timers, PDM, SAI, and watchdog clocks.

## Risks And Test Signals
Risks include accidental carryover from i.MX8MM where Nano lacks a block, wrong shared display gate semantics because camera and display pixel roots share one CCGR bit, missing critical handling for NOC/AHB/GIC/DRAM, and firmware-managed DRAM rate caching errors. Test signals include i.MX8MN boot with clean clock warnings, working CPUfreq, GPU/display/camera/USB/ENET/USDHC/audio probing, six GPT roots visible, shared SAI/PDM gates surviving simultaneous audio users, suspend/resume smoke tests, and clk-summary rates matching hardware.
