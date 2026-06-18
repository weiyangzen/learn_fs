# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx7ulp.c

## Purpose
This file registers the i.MX7ULP clock domains exposed by separate SCG1, PCC2, PCC3, and SMC1 device tree nodes. It covers system PLL/PFD generation, system/core/NIC/DDR roots, peripheral clock controller gates and composites, and the SMC ARM core selector.

## Important APIs, Types, And Functions
Four early init functions are declared with `CLK_OF_DECLARE()`: `imx7ulp_clk_scg1_init()`, `imx7ulp_clk_pcc2_init()`, `imx7ulp_clk_pcc3_init()`, and `imx7ulp_clk_smc1_init()`. Each allocates `struct clk_hw_onecell_data` with `kzalloc_flex()`, maps its node with `of_iomap()`, fills `hws[]`, validates with `imx_check_clk_hws()`, and registers `of_clk_hw_onecell_get`. The SCG path uses `imx_clk_hw_pllv4()`, `imx_clk_hw_pfdv2()`, mux, divider, divider-gate, and `imx_clk_hw_cpu()` helpers. PCC paths use `imx7ulp_clk_hw_composite()` plus simple gates. `ulp_div_table` defines the 1/2/4/8/16/32/64 divider encoding used by SCG bus dividers.

## Control Flow
SCG1 initialization resolves root inputs `rosc`, `sosc`, `sirc`, `firc`, and `upll`; configures APLL/SPLL pre-selectors and pre-dividers; registers APLL/SPLL and their PFDs; registers PLL/PFD selectors; creates SPLL, system, high-speed-run system, DDR, NIC, GPU, SOSC bus, and FIRC bus clocks. PCC2 then publishes DMA, GPIO, CAAM, timers, LPSPI, LPI2C, LPUART, FlexIO, USB, USDHC, watchdog, and USB PHY clocks. PCC3 publishes additional timers, MMDC, LPI2C/LPUART, DSI/LCDIF, VIU, pin controllers, and GPU2D/3D clocks. SMC1 only exposes the ARM mux selecting normal or HSRUN core parents.

## State And Persistence
There is no remove path or explicit suspend state. Each node owns a separate onecell provider allocated for boot lifetime. Hardware programming is persistent in SCG/PCC/SMC MMIO. Critical flags protect DDR and NIC clocks, and MMDC is registered as a critical gate because memory controller access must remain clocked.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/imx7ulp-clock.h`, node compatibles `fsl,imx7ulp-scg1`, `fsl,imx7ulp-pcc2`, `fsl,imx7ulp-pcc3`, and `fsl,imx7ulp-smc1`, and firmware/device-tree supplied clock names. PCC composites depend on the i.MX7ULP-specific composite helper's interpretation of PCC register fields. UART aliases are registered after PCC2/PCC3 setup through `imx_register_uart_clocks()`.

## Risks And Test Signals
Risk centers on split-provider ordering: PCC consumers depend on SCG roots such as `nic1_clk`, `nic1_bus_clk`, and PLL/PFD outputs already being registered. PLL configuration is marked as not safely changeable while enabled, so reparent/rate operations must respect gate flags. Test signals include successful boot with all four providers, stable DDR/NIC operation, UART console on LPUART4-7, USB/USDHC/CAAM/timer devices probing, GPU/display clocks when present, no missing-clock warnings, and clk-summary rates matching SCG/PCC register values.
