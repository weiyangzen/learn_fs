# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rv1103b-cru.h

## Purpose
`rockchip,rv1103b-cru.h` defines CRU clock IDs for Rockchip RV1103B, a compact video/AI-oriented SoC. It covers PLL/root clocks, UART and peripheral clocks, media interfaces, SRAM, USB PHY reference clocks, and audio codec clocks.

## Important APIs, types, and functions
The macro API starts with `PLL_GPLL`, `ARMCLK`, `PLL_DPLL`, and root divider clocks such as `XIN_OSC0_HALF` and `CLK_GPLL_DIV*`. Families include `CLK_*`, `ACLK_*`, `HCLK_*`, `PCLK_*`, `SCLK_*`, `LSCLK_*`, `MCLK_*`, `TCLK_*`, `DCLK_*`, `CCLK_*`, and `DBCLK_*`. Tail IDs include `SCLK_UART*_SRC`, `XIN_RC_SRC`, `CLK_UTMI_USBOTG`, and `CLK_REF_USBPHY`.

## Control flow
The header is included by DTS and driver code. Runtime control flows from clock phandle cells to the RV1103B CRU driver, which implements parent selection, rate division, gating, and enable sequencing.

## State and persistence
No state is maintained in the header. The numeric values are persistent ABI, while CRU registers and low-power domains carry actual clock state.

## Dependencies and integration points
It integrates with RV1103B board DTS files, Rockchip CRU support, audio codec and I2S/PDM users, video/camera blocks, USB PHY, UART/I2C/SPI/PWM/timer/GPIO drivers, SRAM/DMA paths, and PMU/RC oscillator users.

## Risks and test signals
Risks include selecting source clocks instead of effective leaf clocks, RC/USB reference misconfiguration, and wrong media-clock IDs causing camera or display probe failures. Test signals include serial console, USB PHY lock, audio codec clocking, camera pipeline bring-up, clk-summary rates, and clean DT validation.
