# sources/distributed-fs/ceph-client/arch/arm/include/debug/msm.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/msm.S` implements the Qualcomm MSM UART
DEBUG_LL backend. It is part of the vendored Linux ARM code under the Ceph client source tree and
has 48 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: addruart, senduart, waituarttxrdy, waituartcts, and busyuart around
UARTDM or legacy register layouts.
No standalone symbols are declared beyond build-system or include-level directives.

## Control Flow
waituarttxrdy conditionally polls either UARTDM status or legacy flag registers before senduart
writes the byte.

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
Primary risk: the backend has SoC-specific register spacing and can spin forever if the selected
port does not expose the expected status. Changes should preserve register layouts, numeric
constants, early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.
