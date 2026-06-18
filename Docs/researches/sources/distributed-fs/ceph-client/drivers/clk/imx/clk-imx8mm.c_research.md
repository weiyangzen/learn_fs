# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8mm.c

## Purpose
This platform driver registers the i.MX8M Mini CCM clock tree. It publishes external inputs, anatop PLLs, fixed PLL outputs, root composites for CPU/bus/peripheral domains, CCGR leaf gates, shared gates, DRAM firmware-managed roots, and an ARM CPU clock provider.

## Important APIs, Types, And Functions
`imx8mm_clocks_probe()` is the only probe function and is bound by the `fsl,imx8mm-ccm` match table. It uses global `clk_hw_data` and `hws`, allocates a onecell provider with `kzalloc_flex()`, maps the anatop node with `of_find_compatible_node()`/`of_iomap()`, maps the CCM resource with `devm_platform_ioremap_resource()`, and registers clocks with `imx_clk_hw_pll14xx()`, `imx8m_clk_hw_composite*()`, `imx_clk_hw_gate4()`, shared gate helpers, and `imx_clk_hw_cpu()`. Parent-name arrays define all mux choices for A53, M4, VPU, GPU, AXI/AHB/NOC, display, PCIe, CSI, SAI, SPDIF, ENET, storage, serial, USB, GIC, and PDM domains.

## Control Flow
Probe first registers dummy/external clocks and anatop PLL roots: audio/video/DRAM/GPU/VPU/ARM/sys_pll3, bypass muxes, output gates, fixed SYS PLL1 and SYS PLL2 derived rates, and CLKOUT mux/div/gates. It then switches to the CCM base and builds core composites, backwards-compatible aliases for old source/gate/div IDs, the A53 core mux, bus composites, IPG dividers, firmware-managed DRAM clocks, all peripheral root composites, CCGR gates, shared NAND/SAI/PDM/display gates, fixed GPT 3 MHz and DRAM alternate roots, DRAM core mux, and the CPU clock. It validates with `imx_check_clk_hws()`, registers the provider, then registers UART lookup clocks.

## State And Persistence
The driver has no remove path for clocks and suppresses bind attributes to prevent unbind/rebind crashes. Clock state is in hardware registers, with global `hws` used by helper and debug paths. Shared counters protect CCGR bits shared by SAI root/IPG pairs, PDM root/IPG, NAND root/bus, and display subclocks. DRAM alternate/APB clocks are marked firmware-managed because TF-A changes DRAM clocks outside the Linux clock framework.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/imx8mm-clock.h`, `fsl,imx8mm-anatop`, `fsl,imx8mm-ccm`, input clock names (`osc_24m`, `osc_32k`, `clk_ext1-4`), i.MX8M composite helpers, PLL14xx data, and the common clock framework. Consumers use DT clock IDs. `mcore_booted` is exposed as a module parameter shared by i.MX code paths.

## Risks And Test Signals
Risks include incorrect PLL parent/bypass setup, mismatched old alias IDs, missing critical flags for NOC/AHB/GIC/DRAM, unsafe Linux control of firmware-managed DRAM clocks, and shared-gate underflow disabling a block still in use. Test signals include successful i.MX8MM boot, no missing clocks in `imx_check_clk_hws()`, clk-summary coverage of all IMX8MM IDs, CPUfreq changes, DRAM stability with TF-A, display/CSI/VPU/GPU/PCIe/USB/ENET/USDHC/audio peripheral probes, and failed provider-registration paths unregistering already created hardware clocks.
