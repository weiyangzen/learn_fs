# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx5.c

## Purpose
`clk-imx5.c` is the common clock framework provider for i.MX50, i.MX51, and i.MX53 CCM hardware. It builds a flat onecell clock table indexed by `dt-bindings/clock/imx5-clock.h`, maps DPLL and CCM register blocks, registers PLLs, muxes, dividers, fixed factors, gates, and CPU clocks, then exposes them to device tree consumers through `of_clk_add_provider()`. The file also applies boot-time parent/rate policy for SDHC, USB, CAN, TV/display, and low-power step clocks.

## Important APIs, Types, And Functions
The key state is `static struct clk *clk[IMX5_CLK_END]` and `static struct clk_onecell_data clk_data`. `mx5_clocks_common_init()` creates clocks shared by all supported i.MX5 variants: fixed inputs, bus roots, UART/ECSPI/USB/SSI/SPDIF roots, peripheral gates, critical AHB/AIPS/TMAX/SPBA/EMI/GPC clocks, and shared display/audio parent muxes. Variant entry points `mx50_clocks_init()`, `mx51_clocks_init()`, and `mx53_clocks_init()` map the correct PLL base addresses, call the common initializer, add SoC-specific muxes/gates, run `imx_check_clocks()`, register the provider, and tune initial parent/rate choices. Registration is via `CLK_OF_DECLARE()` compatible strings `fsl,imx50-ccm`, `fsl,imx51-ccm`, and `fsl,imx53-ccm`.

The implementation depends heavily on i.MX helper constructors from `drivers/clk/imx/clk.h`: `imx_clk_pllv2()`, `imx_clk_mux()`, `imx_clk_mux_flags()`, `imx_clk_divider()`, `imx_clk_gate2()`, `imx_clk_gate2_flags()`, `imx_clk_fixed_factor()`, and `imx_clk_cpu()`.

## Control Flow
Probe is early OF clock declaration driven. Each SoC init maps DPLL regions with fixed physical base addresses, maps the CCM node with `of_iomap()`, registers common clocks, registers SoC-only display/media/peripheral clocks, checks the table, publishes the onecell provider, then performs post-registration setup with normal clock framework calls. i.MX50 uses MX53-style DPLL addresses and a two-bit `main_bus` mux; i.MX51 applies MIPI power-saving register workarounds; i.MX53 adds PLL4, LDB, CAN, SATA, FIRI, CSI, IEEE1588, and an `imx_clk_cpu()` ARM clock model.

## State And Persistence
Persistent state is the global clock pointer table, `clk_data`, and hardware register state programmed through CCM/DPLL MMIO. No filesystem or NVRAM state is used. Parent/rate changes are persistent for the running kernel because they write live CCM register fields. Several gates are marked `CLK_IS_CRITICAL` to keep fabric, memory, and power-management clocks enabled regardless of consumer usage.

## Dependencies And Integration Points
The driver integrates with device tree clock consumers through numeric IDs from `imx5-clock.h`, with silicon revision helpers from `<soc/imx/revision.h>`, with Linux CCF APIs, and with downstream drivers through `clk_register_clkdev()` aliases for CPU and GPC DVFS plus `imx_register_uart_clocks()`. It also relies on board-provided fixed clocks named `ckil`, `osc`, `ckih1`, and `ckih2`.

## Risks
Risk is concentrated in register bit positions, parent arrays, and SoC differences. A wrong mux parent order breaks DT clock IDs silently. Failed `ioremap()`/`of_iomap()` only triggers `WARN_ON()` and execution continues, so a bad mapping can become a later NULL access. Clock names must remain stable because many in-file parents reference prior registrations by string. Critical-clock flags must be conservative: removing one from bus, memory, or power domains can hang boot.

## Test Signals
Useful signals are early boot without clock provider warnings, `imx_check_clocks()` absence of missing-clock diagnostics, working serial console after `imx_register_uart_clocks()`, correct SDHC enumeration at the configured 166.25 MHz or 200 MHz roots, USB PHY operation at 24 MHz/rounded 54 MHz OHCI/host roots, display/LDB paths on i.MX53, and debugfs `/sys/kernel/debug/clk/clk_summary` parent/rate/gate state matching the reference manual and board DT.
