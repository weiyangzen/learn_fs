# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rv1108-cru.h

## Purpose
`rv1108-cru.h` is the Rockchip RV1108 clock/reset binding header. It exposes PLLs, bus/peripheral clocks, and reset IDs for this older Rockchip SoC.

## Important APIs, types, and functions
The clock API includes `PLL_APLL`, `PLL_DPLL`, `PLL_GPLL`, `ARMCLK`, many `SCLK_*` special clocks, `ACLK_*`, `PCLK_*`, and `HCLK_*` gate IDs, plus display/media IDs. Reset macros use several prefixes: `SRST_*`, `PRST_*`, `HRST_*`, `ARST_*`, `MRST_*`, and `NRST_*`, reflecting soft, peripheral, HCLK, ACLK, media, and other reset domains.

## Control flow
The header is consumed by DTS and drivers. Runtime clock/reset operations go through the RV1108 CRU driver and reset-controller implementation.

## State and persistence
No state is stored here. The numeric ID mapping is a stable ABI; hardware registers hold clock and reset state.

## Dependencies and integration points
It integrates with RV1108 device trees, Rockchip CRU support, reset consumers, and drivers for NAND, SDMMC/SDIO/eMMC, UART, I2C, SPI, PWM, GPIO, USB OTG, CIF, VPU, display, DSP, PMU, PVTM, and audio.

## Risks and test signals
Risks include mixing the many reset prefixes, assuming gaps can be reused, and using wrong clock IDs for storage sample/drive paths. Test signals include DT validation, reset-controller coverage, boot console, storage tuning, USB and camera/video operation, and clk-summary checks for expected gates.
