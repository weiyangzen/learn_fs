# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk3528-cru.h

## Purpose
`rockchip,rk3528-cru.h` provides the stable clock ID namespace for the RK3528 CRU, including normal CRU clocks and SCMI-visible secure/firmware clocks.

## Important APIs, types, and functions
The macro API starts with PLL and CPU/root clocks (`PLL_APLL`, `PLL_CPLL`, `PLL_GPLL`, `PLL_PPLL`, `PLL_DPLL`, `ARMCLK`) and continues through `CLK_*`, `ACLK_*`, `HCLK_*`, `PCLK_*`, `SCLK_*`, `MCLK_*`, `DCLK_*`, `CCLK_*`, `TCLK_*`, and `DBCLK_*`. The file also defines `SCMI_*` IDs for CPU, GPU, crypto, key ladder, TRNG, and related secure clock consumers.

## Control flow
No executable flow exists. DTS files use these names in clock specifiers; the RK3528 CRU driver or SCMI firmware backend interprets the numeric ID and applies the requested enable/rate/parent operation.

## State and persistence
The ABI state is the fixed integer mapping. Runtime state is maintained by CRU registers or by firmware for SCMI clocks. The header itself stores nothing and should not be reordered.

## Dependencies and integration points
Integration points include Rockchip RK3528 DTS, the CRU driver, SCMI clock bindings, reset/power-domain coordinated peripheral probes, and drivers for crypto, display, video, GMAC, USB, SDMMC/SDIO, eMMC, audio, UART, I2C, SPI, PWM, timers, and GPIO.

## Risks and test signals
Risks include misuse of SCMI IDs as direct CRU IDs, numeric ABI changes, and incorrect sample/drive clock IDs for MMC/SDIO interfaces. Test signals are clean schema checks, clock provider registration without gaps that drivers need, MMC tuning success, crypto secure clock access through SCMI, and working display/network/storage peripherals.
