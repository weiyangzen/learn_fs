# sources/distributed-fs/ceph-client/arch/powerpc/mm/pgtable-frag.c

## Purpose
This file implements allocation and freeing of PTE tables using fragments carved from page-table pages. It lets PowerPC share one physical page across several PTE fragments where `PTE_FRAG_NR > 1`, while preserving refcounts, page-table constructors/destructors, RCU freeing, and THP deferral rules.

## Important APIs, Types, And Functions
The public functions are `pte_fragment_alloc()`, `pte_fragment_free()`, `pte_frag_destroy()`, and under THP `pte_free_defer()`. Internal helpers include `get_pte_from_cache()`, `__alloc_for_ptecache()`, and `pte_free_now()`. State is stored in `mm->context` through `pte_frag_get()`/`pte_frag_set()` and in `ptdesc->pt_frag_refcount`.

## Control Flow
Allocation first tries `get_pte_from_cache()` under `mm->page_table_lock`, consumes the next fragment pointer, and clears the cache when the page boundary wraps. If the cache is empty, `__alloc_for_ptecache()` allocates a page-table descriptor, runs `pagetable_pte_ctor()`, initializes the fragment refcount, and either returns the whole page for single-fragment configurations or caches the remaining fragments for the mm. Freeing converts the address to `ptdesc`, handles reserved tables specially, decrements the fragment refcount, and either frees immediately for kernel or inactive folios, or schedules RCU freeing when user page tables may still be walked.

## State And Persistence
Fragment availability persists in the per-mm cached pointer. Refcounts persist in `pt_frag_refcount` until all fragments of a page-table page are released. Folio active state marks deferred freeing for THP-related paths.

## Dependencies And Integration Points
This integrates with generic page-table allocation (`pagetable_alloc/free`, `pagetable_pte_ctor/dtor`), mm locking, RCU, hugepage/THP paths, and the `mm->context` storage initialized by `init_new_context()` in the nohash context code.

## Risks And Test Signals
Risks include fragment refcount imbalance, cache pointer wrap errors, freeing reserved page tables incorrectly, and RCU lifetime bugs under concurrent page-table walkers. Test signals include fork/exit churn, THP collapse/split, user and kernel PTE allocation, `PTE_FRAG_NR == 1` builds, and page-table debug checks.
