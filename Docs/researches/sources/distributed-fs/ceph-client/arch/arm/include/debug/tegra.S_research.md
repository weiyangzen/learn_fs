# sources/distributed-fs/ceph-client/arch/arm/include/debug/tegra.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/tegra.S` implements NVIDIA Tegra DEBUG_LL
UART selection and transmit support. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 218 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: TEGRA_UARTA-E bases, clock/reset and PMC scratch registers,
checkuart(), addruart, senduart, busyuart, and waituartcts.
Visible dependencies include: `linux/serial_reg.h`.
Important macros/constants include: `UART_SHIFT`, `TEGRA_CLK_RESET_BASE`, `TEGRA_APB_MISC_BASE`,
`TEGRA_UARTA_BASE`, `TEGRA_UARTB_BASE`, `TEGRA_UARTC_BASE`, `TEGRA_UARTD_BASE`, `TEGRA_UARTE_BASE`,
`TEGRA_PMC_BASE`, `TEGRA_CLK_RST_DEVICES_L`, `TEGRA_CLK_RST_DEVICES_H`, `TEGRA_CLK_RST_DEVICES_U`,
`TEGRA_CLK_OUT_ENB_L`, `TEGRA_CLK_OUT_ENB_H`, `TEGRA_CLK_OUT_ENB_U`, `TEGRA_PMC_SCRATCH20`,
`TEGRA_APB_MISC_GP_HIDREV`, `UART_VIRTUAL_BASE`, ... (19 total).

## Control Flow
addruart can inspect scratch registers and clock enables to infer the active UART, then 8250-style
TX/status polling emits bytes.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: the detection path reads reset, clock, and HIDREV state before normal mappings exist,
so unsupported chips or clock-gated UARTs can select no usable console. Changes should preserve
register layouts, numeric constants, early-boot calling conventions, and userspace/module ABI
boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.
