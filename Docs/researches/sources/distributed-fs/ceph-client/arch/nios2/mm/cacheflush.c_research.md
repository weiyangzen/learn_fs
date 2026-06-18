# sources/distributed-fs/ceph-client/arch/nios2/mm/cacheflush.c

Purpose: implements Nios II cache maintenance, page/folio D-cache tracking, icache synchronization, and
update_mmu_cache_range TLB reload behavior.

Important APIs/types/functions: functions: `Copyright`, `__invalidate_dcache`, `__flush_icache`, `flush_aliases`, `flush_cache_all`,
`flush_cache_mm`, `flush_cache_dup_mm`, `flush_icache_range`, `flush_dcache_range`,
`invalidate_dcache_range`, `flush_cache_range`, `flush_icache_pages`, and 9 more; prototypes:
`__volatile__`, `__volatile`, `flush_dcache_mmap_lock_irqsave`, `__flush_icache`, `__flush_dcache`,
`clear_bit`, `__flush_dcache_folio`, `flush_aliases`, `set_bit`, `reload_tlb_page`; types:
`mm_struct`, `vm_area_struct`, `address_space`, `folio`, `page`; exports: `flush_dcache_range`,
`invalidate_dcache_range`, `flush_dcache_folio`, `flush_dcache_page`.

Control flow: Cache paths iterate line-sized ranges with Nios II flush/invalidate instructions, mark folios dirty
or clean, synchronize executable mappings, and reload the TLB entry after installing a userspace
PTE.

State and persistence: State is mostly hardware cache contents, folio dirty-cache flags, DMA-visible memory coherency, and
instruction-cache visibility after code or user-page updates.

Dependencies and integration points: Dependencies include `linux/export.h`, `linux/sched.h`, `linux/mm.h`, `linux/fs.h`,
`linux/pagemap.h`, `asm/cacheflush.h`, `asm/cpuinfo.h`. Integration points include generic Linux MM,
irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II
control-register assembly. This source is part of the Nios II architecture port under the vendored
ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
