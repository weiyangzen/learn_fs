# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk3506-cru.h

## Purpose
`rockchip,rk3506-cru.h` defines the RK3506 clock binding IDs for the CRU. It is a modern Rockchip binding header focused on clock IDs rather than reset IDs.

## Important APIs, types, and functions
The exported API is numeric macros from PLL IDs through peripheral clocks. Major identifiers include `PLL_GPLL`, `PLL_V0PLL`, `PLL_V1PLL`, `ARMCLK`, `CLK_DDR`, root/gated PLL outputs, `ACLK_*`, `HCLK_*`, `PCLK_*`, `SCLK_*`, `MCLK_*`, `LRCK_*`, `TCLK_*`, and `DBCLK_*`. The highest entries include 32 kHz/PMU/ref PHY/Wi-Fi and PLL reference helper clocks such as `CLK_WIFI_OUT`, `CLK_V0PLL_REF`, `CLK_V1PLL_REF`, and `CLK_32K_FRAC_MUX`.

## Control flow
Preprocessor inclusion is the only flow in the header. At runtime, device-tree clock cells referencing these constants are looked up by the RK3506 CRU driver, which performs the actual gate, mux, divider, and rate operations.

## State and persistence
The header has no runtime state. Its integer assignments are persistent ABI for RK3506 device trees and drivers. Hardware clock state lives in CRU registers and can persist across low-power transitions depending on the SoC domain.

## Dependencies and integration points
It integrates with RK3506 board DTS files, Rockchip CRU driver tables, and peripheral drivers for DDR, buses, DMA, crypto, audio, PWM, GPIO, UART, SPI, I2C, timers, touch key, PHY reference outputs, and Wi-Fi clock output.

## Risks and test signals
Risks are duplicate values, typoed identifiers in DTS, missing reset coverage if consumers expect reset macros here, and clock-output IDs that must match IO/PMU routing. Test signals include clean DT compilation, no unknown clock IDs in probe logs, correct rate reporting in `/sys/kernel/debug/clk/clk_summary`, and functional board bring-up for serial console, storage, network or wireless, and audio.
