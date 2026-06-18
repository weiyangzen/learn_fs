# sources/distributed-fs/ceph-client/arch/arm/include/debug/renesas-scif.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/renesas-scif.S` implements Renesas SCIF
DEBUG_LL output for multiple register layouts. It is part of the vendored Linux ARM code under the
Ceph client source tree and has 56 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: SCIF_PHYS, SCIF_VIRT, FTDR, FSR, TDFE, TEND, addruart, senduart,
waituarttxrdy, and busyuart.
Important macros/constants include: `SCIF_PHYS`, `SCIF_VIRT`, `FTDR`, `FSR`, `TDFE`, `TEND`.

## Control Flow
compile-time CONFIG_DEBUG_R7S72100_SCIF2 and CONFIG_DEBUG_RCAR_GEN2_SCIF branches select the
transmit and status offsets.

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
Primary risk: using the wrong variant writes to the wrong register offset and can stall waiting on
non-status bits. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.
