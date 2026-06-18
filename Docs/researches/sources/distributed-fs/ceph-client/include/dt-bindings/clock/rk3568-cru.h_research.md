# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3568-cru.h

## Purpose
`rk3568-cru.h` is the clock/reset binding ABI for RK3568 and closely related RK356x Rockchip SoCs. It describes PMUCRU clocks, main CRU clocks, SCMI-managed clocks, and a large reset namespace.

## Important APIs, types, and functions
The file exports macro IDs only. It separates PMUCRU PLLs and clocks (`PLL_PPLL`, `PLL_HPLL`, RTC, PMU, GPIO0, UART0, I2C0, PWM0) from main CRU PLLs and peripheral clocks (`PLL_APLL`, `PLL_GPLL`, `PLL_CPLL`, `PLL_NPLL`, `PLL_VPLL`, `PLL_HPLL`, `PLL_USB480M`). Families include `CLK_*`, `SCLK_*`, `ACLK_*`, `HCLK_*`, `PCLK_*`, `MCLK_*`, `DCLK_*`, and `DBCLK_*`. `SCMI_*` IDs expose firmware-mediated clock handles, and `SRST_*` IDs cover PMU and main CRU soft resets through high-numbered PHY and delay-line resets.

## Control flow
The header participates only in preprocessing. Runtime control flows from a DT clock or reset specifier to the RK3568 clock/reset provider; if the ID belongs to SCMI, firmware may be the effective clock manager. Reset consumers use the `SRST_*` values through reset-controller phandles.

## State and persistence
No mutable state exists here. The macro numbers are persistent DT ABI and must remain stable. Actual clock enable, mux, divider, and reset state is held in CRU/PMUCRU hardware registers or firmware-controlled SCMI state.

## Dependencies and integration points
The header is consumed by RK3568 DTS files, `drivers/clk/rockchip` RK3568 tables, SCMI clock users, reset-controller users, and peripheral drivers for GPU, NPU, VOP, VPU, RGA, crypto, USB, PCIe/SATA/pipe PHY, GMAC, MMC, I2S/PDM, CAN, UART, SPI, and I2C.

## Risks and test signals
Risks include confusing PMUCRU and main CRU ID spaces, adding DTS nodes with raw numbers instead of macros, unstable SCMI IDs, and missing resets for PHY-heavy blocks. Test signals include `dtbs_check`, complete clock summary registration, SCMI clock availability, reset deassertion during driver probe, and peripheral smoke tests across storage, display, network, USB, and audio.
