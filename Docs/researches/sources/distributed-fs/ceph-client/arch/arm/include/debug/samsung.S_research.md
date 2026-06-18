# sources/distributed-fs/ceph-client/arch/arm/include/debug/samsung.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/samsung.S` provides shared Samsung
S3C/S5P DEBUG_LL transmit and FIFO polling logic. It is part of the vendored Linux ARM code under
the Ceph client source tree and has 94 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: fifo_level_s5pv210, fifo_full_s5pv210, fifo_level_s3c2440,
fifo_full_s3c2440, senduart, busyuart, and waituarttxrdy.
Visible dependencies include: `linux/serial_s3c.h`.
Important macros/constants include: `fifo_level`, `fifo_full`.

## Control Flow
SoC wrapper files define address and FIFO helper aliases; this file writes UTXH and loops on
UFSTAT/UTRSTAT until space or completion.

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
Primary risk: the macro alias contract with s3c24xx.S and s5pv210.S is tight and mistakes can leave
early boot spinning in FIFO waits. Changes should preserve register layouts, numeric constants,
early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.
