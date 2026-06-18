# sources/distributed-fs/ceph-client/arch/arm/include/debug/imx-uart.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/imx-uart.h` centralizes physical UART
base address selection for many NXP/Freescale i.MX SoCs. It is part of the vendored Linux ARM code
under the Ceph client source tree and has 142 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: IMX*_UART*_BASE_ADDR constants, IMX*_UART_BASE token-pasting
helpers, IMX_DEBUG_UART_BASE(), and the CONFIG_DEBUG_* switch that defines UART_PADDR.
Important macros/constants include: `__DEBUG_IMX_UART_H`, `IMX1_UART1_BASE_ADDR`,
`IMX1_UART2_BASE_ADDR`, `IMX1_UART_BASE_ADDR(n)`, `IMX1_UART_BASE(n)`, `IMX25_UART1_BASE_ADDR`,
`IMX25_UART2_BASE_ADDR`, `IMX25_UART3_BASE_ADDR`, `IMX25_UART4_BASE_ADDR`, `IMX25_UART5_BASE_ADDR`,
`IMX25_UART_BASE_ADDR(n)`, `IMX25_UART_BASE(n)`, `IMX27_UART1_BASE_ADDR`, `IMX27_UART2_BASE_ADDR`,
`IMX27_UART3_BASE_ADDR`, `IMX27_UART4_BASE_ADDR`, `IMX27_UART_BASE_ADDR(n)`, `IMX27_UART_BASE(n)`,
... (92 total).

## Control Flow
preprocessor selection chooses a single UART physical address before any assembly debug backend
runs.

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
Primary risk: wrong SoC or CONFIG_DEBUG_IMX_UART_PORT values route early printk to unmapped MMIO or
a different serial port. Changes should preserve register layouts, numeric constants, early-boot
calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.
