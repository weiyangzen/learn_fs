# sources/distributed-fs/ceph-client/arch/mips/include/asm/page.h

Purpose: defines MIPS page-size helpers, huge-page constants, page-table value wrappers, cache-alias handling, physical/virtual address conversion, PFN conversions, KASLR offset access, and memory-model inclusions.

Important APIs/types/functions: `page_size_ftlb` maps Config4 MMU extension definitions and `PAGE_SHIFT` to FTLB page-size encoding. Huge TLB macros define `HPAGE_SHIFT`, `HPAGE_SIZE`, `HPAGE_MASK`, and `HUGETLB_PAGE_ORDER` when enabled, otherwise compile-time traps. Externs include page clear/copy code generators, `ARCH_PFN_OFFSET`, `clear_page`, `copy_page`, `shm_align_mask`, `copy_user_highpage`, `__virt_addr_valid`, and `__kaslr_offset`. Types/macros define `pte_t`, `pgtable_t`, `pgd_t`, `pgprot_t`, `pte_val`, `__pte`, `pgd_val`, `__pgd`, `pgprot_val`, `__pgprot`, `pte_pgprot`, `ptep_buddy`, `__pa`, `__va`, `__pa_symbol`, `pfn_to_kaddr`, `virt_to_pfn`, `virt_to_page`, `virt_addr_valid`, and `kaslr_offset`.

Control flow: `page_size_ftlb` switches on MMU extension mode and panics on invalid configurations. `clear_user_page` clears a page and flushes data cache if virtual aliases differ. `___pa` selects address conversion strategy for MIPS64 compatibility/XKPHYS, standard MIPS32, or EVA. Other macros are direct conversions/wrappers.

State and persistence: no durable state is owned by the header. It reads global architecture state such as `ARCH_PFN_OFFSET`, `shm_align_mask`, cache flush function pointer, and `__kaslr_offset`. Page clear/copy functions mutate page memory.

Dependencies and integration points: includes MIPS spaces, constants, kernel helpers, MIPS registers, vDSO page definitions, PFN helpers, I/O conversions, generic memory model, and getorder. It is foundational for MIPS MM, DMA, page table, and cache-alias code.

Risks: physical/virtual conversion macros are documented for memory initialization only; using them on arbitrary vmalloc/ioremap addresses can be wrong. EVA conversion assumes `PAGE_OFFSET`/`PHYS_OFFSET` mapping. Cache alias flushing depends on `shm_align_mask`. The 64-bit physical-address-on-MIPS32 `pte_t` split layout must be handled through accessors.

Test signals: MM tests should cover FTLB page size encodings, huge-page constants, cache-alias page clear/copy behavior, `virt_addr_valid`, PFN/page conversions, KASLR offset access, and boot-time physical address conversions for supported memory maps.
