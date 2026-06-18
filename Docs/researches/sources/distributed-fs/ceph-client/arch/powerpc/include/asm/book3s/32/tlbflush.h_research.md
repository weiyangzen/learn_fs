# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/32/tlbflush.h

Purpose: provides TLB and hash-table flush wrappers for 32-bit Book3S CPUs, selecting hash-specific flushes or direct TLB invalidation depending on MMU features.

Important APIs/types/functions: declares `hash__flush_tlb_mm()`, `hash__flush_tlb_page()`, `hash__flush_range()`, `hash__flush_gather()`, `_tlbie()`, and `_tlbia()`. Defines `tlb_flush()`, `flush_range()`, `flush_tlb_mm()`, `flush_tlb_page()`, `flush_tlb_range()`, `flush_tlb_kernel_range()`, and local flush aliases.

Control flow: each wrapper tests `MMU_FTR_HPTE_TABLE`. Hash-capable CPUs delegate to hash flush functions; 603/non-hash paths use `_tlbie()` for single pages or `_tlbia()` for broad invalidation.

State and persistence: affects processor TLBs and hash page-table entries. No software state is stored in the header.

Dependencies and integration points: integrates with `mmu_gather`, `vm_area_struct`, `init_mm`, page-table update paths, and assembler implementations of hash flushing.

Risks: range sizing chooses `_tlbie` only for one page on non-hash CPUs; wrong boundaries can leave stale translations. SMP `_tlbie` is extern, while UP inline emits `tlbie; sync`.

Test signals: page-table unmap/remap tests, process teardown with `mmu_gather`, SMP TLB shootdown tests, and non-hash 603 boot coverage.
