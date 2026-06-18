# sources/distributed-fs/ceph-client/arch/m68k/sun3/prom/console.c

## Purpose

implements Sun-3 PROM console input/output wrappers used before the normal tty console is available

## Important APIs, Types, and Functions

Source read size: 170 lines, 4014 bytes. Includes: `linux/types.h`, `linux/kernel.h`,
`linux/sched.h`, `asm/openprom.h`, `asm/oplib.h`, `linux/string.h`. Defined functions: `Copyright`,
`prom_nbputchar`, `prom_getchar`, `prom_putchar`, `prom_query_input_device`,
`prom_query_output_device`. Declared functions: `local_irq_save`. Types visible in this file:
`prom_input_device`, `prom_output_device`.

## Control Flow and Behavior

PROM console routines translate kernel console calls into ROM vector operations for putchar,
getchar, nonblocking polling, and console write loops

## State and Persistence

persistent state is minimal; behavior depends on PROM vector state and early console registration

## Dependencies and Integration Points

integrates with asm/openprom.h, oplib, early printk, boot diagnostics, and Sun-3 PROM initialization

## Risks and Test Signals

PROM calling convention mistakes hang early boot; serial/framebuffer PROM console boot logs are the
key signal
