# sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/cacheflush.h

## Purpose

defines ABI-specific cache flush primitives and aliases used by generic C-SKY cache maintenance code
for C-SKY ABI v1

## Important APIs, Types, and Functions

Source read size: 64 lines, 1980 bytes. Includes: `linux/mm.h`, `asm/string.h`, `asm/cache.h`.
Functions: `flush_kernel_vmap_range`, `invalidate_kernel_vmap_range`, `flush_anon_page`. Key
macros/defines: `__ABI_CSKY_CACHEFLUSH_H`, `ARCH_IMPLEMENTS_FLUSH_DCACHE_PAGE`,
`flush_dcache_folio`, `flush_cache_mm(mm)`, `flush_cache_page(vma, page, pfn)`,
`flush_cache_dup_mm(mm)`, `flush_dcache_mmap_lock(mapping)`, `flush_dcache_mmap_unlock(mapping)`,
`ARCH_IMPLEMENTS_FLUSH_KERNEL_VMAP_RANGE`, `ARCH_HAS_FLUSH_ANON_PAGE`, `flush_cache_vmap(start,
end)`, `flush_cache_vmap_early(start, end)`, `flush_cache_vunmap(start, end)`,
`flush_icache_range(start, end)`, `flush_icache_mm_range(mm, start, end)`,
`flush_icache_deferred(mm)`, `copy_from_user_page(vma, page, vaddr, dst, src, len)`,
`copy_to_user_page(vma, page, vaddr, dst, src, len)`. Local structs: `page`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
