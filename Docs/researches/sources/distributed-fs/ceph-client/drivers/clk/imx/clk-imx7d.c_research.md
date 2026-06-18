# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx7d.c

## Purpose
This file is the early boot clock provider for the i.MX7D CCM. It describes the SoC clock tree from external inputs through anatop PLLs, PFDs, root muxes, pre/post dividers, and CCGR-style gates, then publishes the clocks through a `clk_hw_onecell_data` provider for device tree consumers.

## Important APIs, Types, And Functions
The only function is `imx7d_clocks_init()`, registered with `CLK_OF_DECLARE(imx7d, "fsl,imx7d-ccm", ...)`. It allocates the onecell hardware array with `kzalloc_flex()`, resolves input clocks with `imx_get_clk_hw_by_name()`, maps anatop and CCM registers with `of_iomap()`, and registers clocks with i.MX helpers from `clk.h`: `imx_clk_hw_pllv3()`, `imx_clk_hw_pfd()`, `imx_clk_hw_mux2[_flags]()`, `imx_clk_hw_gate[2/3/4]()`, `imx_clk_hw_divider2()`, `imx_clk_hw_cpu()`, and shared/exclusive gate helpers. Static parent-name arrays define every root source selector. `test_div_table` and `post_div_table` model non-linear PLL divider encodings.

## Control Flow
Initialization first publishes dummy, oscillator, and CKIL entries, then maps `fsl,imx7d-anatop` and builds PLL bypass sources, PLL cores, bypass muxes, output gates, audio/video/DRAM post dividers, system PFDs, fixed-factor system/DRAM/ENET derived outputs, and the LVDS output selector. It then maps the CCM node and builds root source muxes, root gates, pre-dividers, post-dividers, and leaf gates for CPU, bus, DRAM, display, MIPI, PCIe, ENET, SAI/SPDIF, storage, I2C, UART, SPI, PWM, timers, watchdogs, USB, and ADC. After `imx_check_clk_hws()`, it registers the provider, forces PLL bypass parents to their PLLs, selects specific MIPI CSI and GPT parents, registers fixed USB PLL factors late, and calls `imx_register_uart_clocks()`.

## State And Persistence
The persistent state is the global `clk_hw_data`, `hws`, and shared gate counters for SAI1-3, NAND, and ENET1/2. Hardware register state lives in CCM/anatop MMIO and is not saved/restored here; this is an early init provider, not a removable platform driver. Several clocks are marked `CLK_IS_CRITICAL`, notably core system, IPG, AXI, and DRAM paths, so common clock framework disable paths should not shut them off.

## Dependencies And Integration Points
The file depends on `dt-bindings/clock/imx7d-clock.h` IDs matching the `hws[]` indexes, device tree nodes `fsl,imx7d-ccm` and `fsl,imx7d-anatop`, external input names such as `osc`, `ckil`, and `ext_clk_*`, and the i.MX clock helper library. Consumers bind through the OF clock provider and numeric DT clock specifiers. CPU frequency integration uses `imx_clk_hw_cpu()` with ARM root, ARM PLL, and system PLL clocks.

## Risks And Test Signals
Risks are mostly register-map drift and parent/index mismatch: a wrong offset or selector string can silently feed devices from the wrong PLL, while missing critical flags can stop DRAM, AXI, or IPG. Shared gates for SAI, NAND, and ENET must keep shared CCGR bits enabled until all users release them. Late USB fixed factors mean USB PHY consumers depend on correct naming. Test signals include boot on i.MX7D with no `imx_check_clk_hws()` warnings, populated `/sys/kernel/debug/clk/clk_summary`, working CPU frequency changes, UART console, USDHC/NAND/QSPI, ENET PTP/reference clocks, audio SAI clocks, display/MIPI paths, suspend/resume smoke tests, and absence of unexpected critical clock disables.
