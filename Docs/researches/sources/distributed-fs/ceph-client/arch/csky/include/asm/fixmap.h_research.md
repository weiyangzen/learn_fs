# sources/distributed-fs/ceph-client/arch/csky/include/asm/fixmap.h

## Purpose

defines fixed virtual mapping slots and address bounds

## Important APIs, Types, and Functions

Source read size: 33 lines, 747 bytes. Includes: `asm/page.h`, `asm/memory.h`, `linux/threads.h`,
`asm/kmap_size.h`, `asm-generic/fixmap.h`. Key macros/defines: `__ASM_CSKY_FIXMAP_H`,
`FIXADDR_SIZE`, `FIXADDR_START`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
