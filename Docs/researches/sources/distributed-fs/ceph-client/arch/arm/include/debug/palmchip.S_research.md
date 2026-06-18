# sources/distributed-fs/ceph-client/arch/arm/include/debug/palmchip.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/palmchip.S` adapts the generic 8250
DEBUG_LL backend to Palmchip UART register numbering. It is part of the vendored Linux ARM code
under the Ceph client source tree and has 12 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: UART_TX, UART_LSR, UART_MSR overrides followed by include of
debug/8250.S.
Visible dependencies include: `linux/serial_reg.h`, `debug/8250.S`.
Important macros/constants include: `UART_TX`, `UART_LSR`, `UART_MSR`.

## Control Flow
the file has no own control flow; the included 8250 macros inherit the Palmchip register indexes.

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
Primary risk: changing these offsets breaks all inherited 8250 polling and transmit logic for
Palmchip platforms. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.
