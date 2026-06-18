# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/cacheflush.h

## Purpose

declares cache controller operations and cache/TLB-facing flush helpers for pages, folios, and user
text updates

## Important APIs, Types, and Functions

Source read size: 103 lines, 3427 bytes. Includes: `linux/mm.h`, `linux/io.h`, `asm-
generic/cacheflush.h`. Defined functions: `flush_dcache_folio`, `copy_to_user_page`. Declared
functions: `microblaze_cache_init`, `flush_dcache_range`, `invalidate_icache_range`. Key
macros/defines: `_ASM_MICROBLAZE_CACHEFLUSH_H`, `enable_icache()`, `disable_icache()`,
`flush_icache()`, `flush_icache_range(start, end)`, `invalidate_icache()`,
`invalidate_icache_range(start, end)`, `enable_dcache()`, `disable_dcache()`, `invalidate_dcache()`,
`invalidate_dcache_range(start, end)`, `flush_dcache()`, `flush_dcache_range(start, end)`,
`ARCH_IMPLEMENTS_FLUSH_DCACHE_PAGE`, `flush_dcache_page(page)`, `flush_dcache_folio`,
`flush_cache_page(vma, vmaddr, pfn)`, `copy_to_user_page`. Types visible in this file: `scache`,
`page`. External symbols referenced/declared: `mbc`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
