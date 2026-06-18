# sources/distributed-fs/ceph-client/arch/xtensa/mm/tlb.c

Purpose: Implements local Xtensa TLB flush/update operations and optional debug sanity checking.

Important APIs, types, and functions: `local_flush_tlb_all()`, `local_flush_tlb_mm()`, `local_flush_tlb_range()`, `local_flush_tlb_page()`, `local_flush_tlb_kernel_range()`, `update_mmu_tlb_range()`, `get_pte_for_vaddr()`, `check_tlb_entry()`, and `check_tlb_sanity()`.

Control flow: Full flush iterates all auto-refill ways/entries for I- and D-TLB. MM flush invalidates or reassigns ASIDs depending on whether the mm is active. Range/page flush temporarily switches RASID to the target ASID, invalidates ITLB for executable mappings and DTLB for all, then restores RASID. Kernel range flush either invalidates individual mappings or falls back to full flush.

State and persistence: Mutates TLB entries, per-mm per-CPU ASID state, `mm->context.cpu`, and RASID register. Debug code inspects TLB virtual/translation registers and PTEs.

Dependencies and integration: Used by cache/MM/fault/SMP paths; relies on ASID management in `mmu_context`, Xtensa TLB register helpers, VM flags, and folio refcount/mapcount checks for sanity diagnostics.

Risks: Incorrect RASID switching can invalidate wrong address spaces; range threshold must reflect total TLB entries; debug sanity can BUG on serious inconsistencies; kernel range bounds are architecture-specific.

Test signals: mmap/munmap/mprotect stress, ASID rollover, executable mapping flushes, SMP shootdowns through `smp.c`, DEBUG_TLB_SANITY runs, and kernel vmalloc TLB invalidation.
