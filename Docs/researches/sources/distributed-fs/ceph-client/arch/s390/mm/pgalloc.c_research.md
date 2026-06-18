## sources/distributed-fs/ceph-client/arch/s390/mm/pgalloc.c

Purpose: allocates and frees s390 page-table and region/segment-table structures, upgrades user address-space table depth, and builds "base" ASCE mappings without enhanced DAT large-page features for I/O users.

Important APIs, types, and functions: `crst_table_alloc_noprof()`, `crst_table_free()`, `crst_table_upgrade()`, `page_table_alloc_noprof()`, `page_table_free()`, optional `pte_free_defer()`, `base_asce_alloc()`, and `base_asce_free()` are the externally relevant APIs. Internal base walkers include `base_page_walk()`, `base_segment_walk()`, `base_region3_walk()`, `base_region2_walk()`, and `base_region1_walk()`.

Control flow: CRST/PTE allocation uses generic pagetable allocation, accounting unless `init_mm`, DAT page-state marking, constructors, and invalid entry initialization. `crst_table_upgrade()` requires mmap write lock, allocates new upper levels when an address exceeds current ASCE limit, swaps `mm->pgd` and context ASCE under `page_table_lock`, then runs `on_each_cpu()` to update active lowcore/user control registers and flush local TLBs. Base ASCE allocation chooses the smallest ASCE type covering `addr + num_pages`, allocates tables recursively, fills PTEs using `lra`, and unwinds through `base_asce_free()` on failure.

State and persistence: mutates `mm->pgd`, `mm->context.asce`, `mm->context.asce_limit`, page table counters, and per-page DAT state. `base_pgt_cache` is lazily created and persists for base page tables.

Dependencies and integration points: depends on generic pagetable constructors/destructors, s390 control-register ASCE handling, TLB flushing, page-state helpers, RCU for THP PTE free, slab cache APIs, and I/O users needing non-EDAT ASCEs.

Risks: ASCE upgrade must update all active CPUs to prevent stale TLBs and incorrect address-space limits. Base ASCEs are explicitly not safe to attach to CPUs; doing so would leave uncleared TLB entries. Constructor/destructor pairing and table-level accounting must stay exact.

Test signals: mmap beyond current ASCE limits, fork/exit page-table allocation/free stress, THP split/free with RCU, I/O paths using `base_asce_alloc()`, low-memory allocation failure unwind, and multi-CPU ASCE upgrade TLB correctness.
