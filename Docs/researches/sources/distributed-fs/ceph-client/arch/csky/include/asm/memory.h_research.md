# sources/distributed-fs/ceph-client/arch/csky/include/asm/memory.h

## Purpose

defines kernel/user virtual memory layout constants

## Important APIs, Types, and Functions

Source read size: 25 lines, 657 bytes. Includes: `linux/compiler.h`, `linux/const.h`,
`linux/types.h`, `linux/sizes.h`. Key macros/defines: `__ASM_CSKY_MEMORY_H`, `FIXADDR_TOP`,
`PKMAP_BASE`, `VMALLOC_START`, `VMALLOC_END`, `TCM_NR_PAGES`, `FIXADDR_TCM`.

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
