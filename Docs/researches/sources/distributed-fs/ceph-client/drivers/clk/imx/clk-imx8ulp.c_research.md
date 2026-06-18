# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8ulp.c

## Purpose
Registers clock providers and reset controllers for i.MX8ULP CGC1, CGC2, PCC3, PCC4, and PCC5 blocks. It covers PLLs, PFDs, oscillator dividers, bus/core roots, peripheral composite clocks, DMA gates, LPAV clocks, audio selectors, and PCC reset bits.

## Important APIs, Types, And Functions
The probe dispatcher `imx8ulp_clk_probe()` invokes match-data init functions: `imx8ulp_clk_cgc1_init()`, `imx8ulp_clk_cgc2_init()`, `imx8ulp_clk_pcc3_init()`, `imx8ulp_clk_pcc4_init()`, and `imx8ulp_clk_pcc5_init()`. Reset support uses `struct pcc_reset_dev`, `imx8ulp_pcc_assert()`, `imx8ulp_pcc_deassert()`, and `imx8ulp_pcc_reset_init()`. Clock creation uses i.MX helpers for PLLv4, PFDv2, disabled gates, muxes, dividers, composite PCC clocks, and fixed factors.

## Control Flow
Each init allocates onecell data sized for its binding, maps the platform resource, registers the block's clocks, calls `imx_check_clk_hws()`, and adds an OF provider. PCC blocks then register a reset controller using per-block offset arrays. PCC3 also registers UART clocks. The platform match table selects the init function by compatible string.

## State And Persistence Behavior
Hardware state is the CGC/PCC register set and PCC reset bits. Kernel state is devm-managed clock arrays plus reset-controller data. Reset RMW operations share `imx_ccm_lock` with clock control because reset bits live in the same PCC registers as clocks.

## Dependencies And Integration Points
Depends on `imx8ulp-clock.h`, reset-controller framework, OF clock providers, i.MX PLL/PFD/composite helpers, and platform compatibles for each block. Peripheral drivers consume clocks and resets from these providers.

## Risks
Clock and reset fields share registers, so missing locking can corrupt clock settings during reset toggles. Critical flags on A35/NIC/LPAV/DDR/MU/timer clocks affect boot and low-power reliability. PCC reset arrays must match binding reset IDs exactly.

## Test Signals
Boot all CGC/PCC nodes, inspect `clk_summary`, exercise UART, I2C, SPI, USDHC, USB, ENET, SAI, SPDIF, CSI/DSI, DMA, and GPU clocks, test reset controller users, and run suspend/resume with critical clocks retained.
