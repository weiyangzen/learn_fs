# sources/distributed-fs/ceph-client/arch/m68k/mm/hwtest.c

## Purpose

implements early m68k RAM probing helpers that safely test physical memory ranges before the normal
page allocator trusts them

## Important APIs, Types, and Functions

Source read size: 96 lines, 2645 bytes. Includes: `linux/module.h`, `asm/hwtest.h`. Defined
functions: `hwreg_present`, `hwreg_write`. Declared functions: `local_irq_save`. Exported symbols:
`hwreg_present`, `hwreg_write`.

## Control Flow and Behavior

the routines write and verify test patterns while using exception-protected probing so board setup
can reject missing or aliased RAM without crashing the kernel

## State and Persistence

persistent effects are limited to the discovered usable memory map fed into m68k boot memory setup;
the probe deliberately restores or overwrites test locations during early boot

## Dependencies and Integration Points

depends on m68k exception handling, setup memory descriptors, low-level physical addressing, and
early boot ordering before paging and memblock are finalized

## Risks and Test Signals

unsafe probing can corrupt firmware data or fault recursively; booting on machines with sparse,
mirrored, or partially populated RAM is the strongest test signal
