# sources/distributed-fs/ceph-client/arch/csky/include/asm/highmem.h

## Purpose

defines highmem kmap helpers and address limits

## Important APIs, Types, and Functions

Source read size: 44 lines, 1114 bytes. Includes: `linux/init.h`, `linux/interrupt.h`,
`linux/uaccess.h`, `asm/kmap_size.h`, `asm/cache.h`. Key macros/defines: `__ASM_CSKY_HIGHMEM_H`,
`HIGHMEM_DEBUG`, `LAST_PKMAP`, `LAST_PKMAP_MASK`, `PKMAP_NR(virt)`, `PKMAP_ADDR(nr)`,
`ARCH_HAS_KMAP_FLUSH_TLB`, `flush_cache_kmaps()`, `arch_kmap_local_post_map(vaddr, pteval)`,
`arch_kmap_local_post_unmap(vaddr)`.

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
