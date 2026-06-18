# sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/cacheflush.h

## Purpose

defines ABI-specific cache flush primitives and aliases used by generic C-SKY cache maintenance code
for C-SKY ABI v2

## Important APIs, Types, and Functions

Source read size: 61 lines, 1906 bytes. Includes: `linux/mm.h`. Functions: `flush_dcache_folio`,
`flush_dcache_page`. Key macros/defines: `__ABI_CSKY_CACHEFLUSH_H`, `flush_cache_all()`,
`flush_cache_mm(mm)`, `flush_cache_dup_mm(mm)`, `flush_cache_range(vma, start, end)`,
`flush_cache_page(vma, vmaddr, pfn)`, `PG_dcache_clean`, `flush_dcache_folio`,
`ARCH_IMPLEMENTS_FLUSH_DCACHE_PAGE`, `flush_dcache_mmap_lock(mapping)`,
`flush_dcache_mmap_unlock(mapping)`, `flush_icache_range(start, end)`, `flush_cache_vmap(start,
end)`, `flush_cache_vmap_early(start, end)`, `flush_cache_vunmap(start, end)`,
`copy_to_user_page(vma, page, vaddr, dst, src, len)`, `copy_from_user_page(vma, page, vaddr, dst,
src, len)`.

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
