# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rv1126-cru.h

## Purpose
`rockchip,rv1126-cru.h` is the clock/reset binding header for RV1126. It includes PMUCRU and main CRU clock IDs plus PMU and main soft-reset IDs.

## Important APIs, types, and functions
The file exports PMU clock macros beginning at `PLL_GPLL`, RTC/Wi-Fi/PMU clocks, and UART/I2C/GPIO/PWM PMU-domain clocks. The main CRU section defines PLLs, many `SCLK_*`, `DCLK_*`, `ACLK_*`, `HCLK_*`, `PCLK_*`, `MCLK_*`, and `DBCLK_*` IDs for CPU, DDR, ISP, CIF, video, crypto, storage, USB, GMAC, and serial peripherals. Reset macros `SRST_*` cover PMU reset registers and CRU reset registers.

## Control flow
DTS clock/reset specifiers include the IDs; the RV1126 CRU/PMUCRU clock and reset providers interpret them at runtime. Reset control flows through the reset-controller API and clock control through the common clock framework.

## State and persistence
The header has no state. Numeric mappings are persistent ABI. Hardware register state is split between PMUCRU and CRU domains and may survive some low-power transitions.

## Dependencies and integration points
It integrates with RV1126 board DTS, Rockchip clock/reset drivers, PMU-domain devices, and drivers for camera/ISP, video encode/decode, display, crypto, GMAC, USB PHY, SD/eMMC, I2S/PDM, UART/I2C/SPI/PWM, TSADC/PVTM, OTP, and watchdog/timer blocks.

## Risks and test signals
Risks include using main CRU IDs in PMUCRU contexts, reset IDs that do not match register-bit positions, and camera/video clocks that require coordinated power domains. Test signals include clock and reset provider registration, `dtbs_check`, media pipeline probe, GMAC/USB/storage smoke tests, PMU-domain GPIO/RTC behavior, and reset assertion/deassertion during driver remove/probe cycles.
