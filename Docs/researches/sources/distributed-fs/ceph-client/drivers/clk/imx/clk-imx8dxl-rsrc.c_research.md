# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8dxl-rsrc.c

## Purpose
This file provides the i.MX8DXL SCU clock resource allowlist used by the SCU-backed i.MX clock driver. It enumerates the SCFW resource IDs for peripherals whose clocks may be exposed through the SCU clock framework on i.MX8DXL.

## Important APIs, Types, And Functions
The only exported object is `const struct imx_clk_scu_rsrc_table imx_clk_scu_rsrc_imx8dxl`, which points to `imx8dxl_clk_scu_rsrc_table` and its `ARRAY_SIZE()`. The resource IDs come from `dt-bindings/firmware/imx/rsrc.h`, while `struct imx_clk_scu_rsrc_table` is declared by `clk-scu.h`.

## Control Flow
There is no executable control flow in this file. At link/runtime, the SCU clock driver selects this table for i.MX8DXL and uses it to decide which SCU resources to register or query. The comment requires the table to stay sorted in ascending order, which matters if consumers perform ordered lookups.

## State And Persistence
The table is static read-only data after initialization. It does not cache SCU responses or own any hardware state. Persistent clock state remains in the system controller firmware and the broader SCU clock framework.

## Dependencies And Integration Points
This table integrates with the SCFW resource namespace and the i.MX SCU clock provider. It lists SPI, UART, I2C, ADC, FTM, CAN, LCD/PWM, GPT, FSPI, SDHC, ENET, USB, NAND, M4, display PLL, audio PLL, audio clock, and A35 resources available for i.MX8DXL clock handling.

## Risks And Test Signals
Risks are omission, stale resource IDs, or losing sorted order. Missing resources prevent downstream clocks from appearing; extra resources can cause SCU calls to unavailable hardware. Test signals include SCU clock probe on i.MX8DXL without invalid-resource errors, expected peripherals receiving clocks, and any table-search self-checks or debug logs confirming resource lookup coverage.
