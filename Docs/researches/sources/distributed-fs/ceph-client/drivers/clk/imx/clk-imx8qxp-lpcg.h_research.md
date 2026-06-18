# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8qxp-lpcg.h

## Purpose
Provides subsystem-local LPCG register offsets for i.MX8QXP LSIO, connectivity, and ADMA clock-gate blocks.

## Important APIs, Types, And Functions
This header defines offset macros such as `LSIO_PWM_0_LPCG`, `CONN_USDHC_0_LPCG`, `CONN_ENET_0_LPCG`, `ADMA_LPUART_0_LPCG`, `ADMA_LPI2C_0_LPCG`, and many ADMA audio/peripheral LPCG offsets. There are no functions or types.

## Control Flow
No executable control flow. `clk-imx8qxp-lpcg.c` uses these constants in static LPCG tables to calculate MMIO addresses relative to a subsystem base.

## State And Persistence Behavior
All definitions are compile-time constants. The values encode hardware register layout and must match the SoC reference manual and DT binding expectations.

## Dependencies And Integration Points
The header is private to the i.MX clock driver implementation. It integrates static LPCG registration with dt-binding clock IDs and with the SCU LPCG gate helper.

## Risks
Wrong offsets gate the wrong peripheral clock or touch an unrelated register. Because subsystem ranges can overlap child devices, offset mistakes can be difficult to distinguish from power-domain or SCU ownership issues.

## Test Signals
Compile coverage plus peripheral smoke tests for PWM, UART, I2C, USDHC, ENET, NAND, ADMA audio, and DMA channels behind the listed LPCGs.
