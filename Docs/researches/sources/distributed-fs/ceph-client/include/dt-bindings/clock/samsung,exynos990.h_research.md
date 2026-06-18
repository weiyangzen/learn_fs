# sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynos990.h

## Purpose
`samsung,exynos990.h` defines Exynos990 clock-controller binding IDs for TOP, HSI0, PERIC0, PERIC1, and PERIS CMU domains.

## Important APIs, types, and functions
The exported `CLK_*` constants include shared and G3D/MMC PLL outputs, top-level muxes/dividers/gates, high-speed interface clocks in `CMU_HSI0`, many USI/UART/SPI/I2C-style peripheral clocks in `CMU_PERIC0` and `CMU_PERIC1`, and PERIS infrastructure clocks for GIC, MCT, OTP, TZPC, and TMU.

## Control flow
There are no functions. Consumers use the macros in device-tree clock cells; Exynos990 CMU provider drivers interpret them by domain and expose operations through the common clock framework.

## State and persistence
The file is stateless but ABI-sensitive. Hardware CMU registers store runtime state; always-on/peris clocks may interact with suspend and security policy.

## Dependencies and integration points
It integrates with Exynos990 DTS, Samsung CMU driver data, high-speed interface drivers, PERIC serial drivers, PERIS system blocks, thermal/timer/security-related devices, and power domains.

## Risks and test signals
Risks include domain-local numbering mistakes, missing parent gates from TOP to child CMUs, and breaking boot-critical PERIS clocks. Test signals include DT schema checks, all CMU nodes probing, serial console and USI peripherals working, high-speed interface bring-up, timer/thermal initialization, and clk-summary parent/rate verification.
