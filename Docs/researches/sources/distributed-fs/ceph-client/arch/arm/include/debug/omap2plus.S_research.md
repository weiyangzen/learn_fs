# sources/distributed-fs/ceph-client/arch/arm/include/debug/omap2plus.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/omap2plus.S` implements OMAP2+ and Zoom
board DEBUG_LL address selection. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 82 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: OMAP/Zoom physical and virtual mapping constants, UART_OFFSET(),
addruart, senduart, and FIFO polling macros.
Visible dependencies include: `linux/serial_reg.h`.
Important macros/constants include: `ZOOM_UART_BASE`, `ZOOM_UART_VIRT`, `OMAP_PORT_SHIFT`,
`ZOOM_PORT_SHIFT`, `UART_OFFSET(addr)`.

## Control Flow
addruart chooses between special Zoom mapping and generic OMAP mapping, then TX writes use
serial_reg offsets with the configured port shift.

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
Primary risk: board-specific offset handling is fragile during very early boot because no driver or
device tree mapping can correct it. Changes should preserve register layouts, numeric constants,
early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.
