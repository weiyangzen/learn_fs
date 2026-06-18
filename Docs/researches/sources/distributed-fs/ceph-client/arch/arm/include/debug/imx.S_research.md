# sources/distributed-fs/ceph-client/arch/arm/include/debug/imx.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/imx.S` implements the i.MX DEBUG_LL UART
macro backend. It is part of the vendored Linux ARM code under the Ceph client source tree and has
49 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: addruart, senduart, waituartcts, waituarttxrdy, busyuart,
UART_VADDR, and IMX_IO_P2V.
Visible dependencies include: `asm/assembler.h`, `imx-uart.h`.
Important macros/constants include: `IMX_IO_P2V(x)`, `UART_VADDR`.

## Control Flow
addruart computes physical and virtual addresses, senduart writes TX data, and busyuart polls
transmit-complete state.

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
Primary risk: the virtual address formula and status bits must match the selected i.MX UART
generation. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.
