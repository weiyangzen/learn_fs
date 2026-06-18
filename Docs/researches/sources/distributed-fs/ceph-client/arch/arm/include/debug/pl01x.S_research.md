# sources/distributed-fs/ceph-client/arch/arm/include/debug/pl01x.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/pl01x.S` implements the ARM AMBA
PL010/PL011 DEBUG_LL UART backend. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 37 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: UART01x_DR, UART01x_FR, UART01x_FR_TXFF, UART01x_FR_BUSY, addruart,
senduart, waituarttxrdy, and busyuart.
Visible dependencies include: `linux/amba/serial.h`.

## Control Flow
addruart returns CONFIG_DEBUG_UART_PHYS/VIRT, transmit waits for TX FIFO room, sends a byte, then
polls BUSY.

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
Primary risk: PL010 versus PL011 differences are hidden by linux/amba/serial.h constants and must
stay compatible with both users. Changes should preserve register layouts, numeric constants, early-
boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.
