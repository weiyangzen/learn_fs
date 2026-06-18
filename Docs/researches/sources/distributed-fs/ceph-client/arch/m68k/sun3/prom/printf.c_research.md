# sources/distributed-fs/ceph-client/arch/m68k/sun3/prom/printf.c

## Purpose

provides a small prom_printf() formatter for Sun-3 early firmware diagnostics

## Important APIs, Types, and Functions

Source read size: 55 lines, 975 bytes. Includes: `linux/kernel.h`, `asm/openprom.h`, `asm/oplib.h`.
Defined functions: `prom_printf`. Declared functions: `va_start`, `pr_info`. External symbols
referenced/declared: `kgdb_initialized`.

## Control Flow and Behavior

the function formats into a temporary buffer and writes through PROM console output while normal
printk may be unavailable

## State and Persistence

no durable state is kept beyond emitted firmware console output

## Dependencies and Integration Points

integrates with PROM console wrappers and early Sun-3 boot/debug code

## Risks and Test Signals

format buffer sizing and PROM output availability are the risks; early boot diagnostics are the
signal
