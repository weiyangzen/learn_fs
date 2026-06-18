# sources/distributed-fs/ceph-client/arch/arm/include/debug/sti.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/sti.S` implements STMicroelectronics STI
ASC DEBUG_LL output. It is part of the vendored Linux ARM code under the Ceph client source tree and
has 39 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: ASC_TX_BUF_OFF, ASC_CTRL_OFF, ASC_STA_OFF, ASC_STA_TX_FULL,
ASC_STA_TX_EMPTY, and the standard debug macros.
Important macros/constants include: `ASC_TX_BUF_OFF`, `ASC_CTRL_OFF`, `ASC_STA_OFF`,
`ASC_STA_TX_FULL`, `ASC_STA_TX_EMPTY`.

## Control Flow
transmit writes ASC_TX_BUF after waituarttxrdy sees space, and busyuart waits until the ASC reports
TX empty.

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
Primary risk: the hard-coded status bit definitions are a boot-critical ABI with the STI ASC
hardware block. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.
