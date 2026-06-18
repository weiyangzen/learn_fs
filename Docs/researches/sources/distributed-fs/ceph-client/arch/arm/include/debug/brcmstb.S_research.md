# sources/distributed-fs/ceph-client/arch/arm/include/debug/brcmstb.S

## Purpose
Defines low-level early-printk/debug macro support for the Broadcom STB UART family auto-detection. It supplies the standard addruart, senduart, busyuart, waituarttxrdy, and waituartcts macro contract consumed by ARM head/decompressor/debug assembly.

## Important APIs, Types, And Functions
Important macros/constants include REG_PHYS_BASE, REG_PHYS_BASE_V7, REG_VIRT_BASE, REG_PHYS_ADDR(x), REG_PHYS_ADDR_V7(x), SUN_TOP_CTRL_BASE, SUN_TOP_CTRL_BASE_V7, UARTA_3390, UARTA_72116, UARTA_7250. Assembly macros include .macro  addruart, rp, rv, tmp, .macro store, rd, rx:vararg, .macro load, rd, rx:vararg, .macro senduart,rd,rx, .macro busyuart,rd,rx, .macro waituarttxrdy,rd,rx, .macro waituartcts,rd,rx. It depends directly on #include <linux/serial_reg.h>, #include <asm/cputype.h>.

## Control Flow
Early boot or decompressor code expands addruart to derive physical/virtual debug addresses, senduart to write one byte/word, and busyuart or wait macros to poll transmitter state before continuing. The macros run before normal drivers or clocks may be available.

## State And Persistence
No normal kernel persistence. Some macros poll hardware registers; brcmstb additionally caches detected UART physical/virtual addresses in shared early-boot storage when built for zImage.

## Dependencies And Integration Points
Integrated by ARM decompressor/head/debug assembly through the standard debug macro names. Dependencies are #include <linux/serial_reg.h>, #include <asm/cputype.h> plus CONFIG_DEBUG_UART_* or platform register layout constants.

## Risks And Edge Cases
Register offsets, endian handling, physical/virtual address assumptions, and polling bits must match the SoC before the serial driver exists; a wrong value can hang very early boot or lose panic/decompressor output.

## Test Signals
Test signals are successful decompressor/earlycon output on the target SoC, build coverage for the selected CONFIG_DEBUG_* option, and boot logs that continue past early MMU enablement.
