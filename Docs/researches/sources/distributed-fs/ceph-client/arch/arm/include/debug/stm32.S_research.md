# sources/distributed-fs/ceph-client/arch/arm/include/debug/stm32.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/stm32.S` implements STM32 USART DEBUG_LL
output across old and newer register layouts. It is part of the vendored Linux ARM code under the
Ceph client source tree and has 43 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: STM32_USART_SR_OFF, STM32_USART_TDR_OFF, STM32_USART_TC,
STM32_USART_TXE, addruart, senduart, waituarttxrdy, and busyuart.
Important macros/constants include: `STM32_USART_SR_OFF`, `STM32_USART_TDR_OFF`, `STM32_USART_TC`,
`STM32_USART_TXE`.

## Control Flow
conditional CONFIG_STM32F4_DEBUG_UART selects SR/TDR offsets; the macros poll TXE/TC before and
after writes.

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
Primary risk: mixing STM32F4 offsets with later STM32 UARTs corrupts MMIO accesses during
decompressor or early printk output. Changes should preserve register layouts, numeric constants,
early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.
