# sources/distributed-fs/ceph-client/include/linux/pgtable.h

## Purpose
Generic Linux page-table API layer that sits above architecture `<asm/pgtable.h>` definitions. It supplies portable fallbacks, validation checks, walking helpers, batching helpers, TLB/cache hook declarations, page-protection utilities, huge-page helpers, PFN-map tracking hooks, and page-table modification tracking used by generic MM, vmalloc, ioremap, rmap, GUP, and fault paths.

## Important APIs, Types, and Functions
Key address traversal helpers include `pte_index()`, `pmd_index()`, `pud_index()`, `pgd_index()`, `pte_offset_kernel()`, `pmd_offset()`, `pud_offset()`, `pgd_offset()`, `pmd_off()`, `pmd_off_k()`, and `virt_to_kpte()`. PTE/PMD/PUD access helpers include `ptep_get()`, `pmdp_get()`, `pudp_get()`, lockless getters, `set_ptes()`, `set_pte_at()`, `ptep_get_and_clear()`, `get_and_clear_ptes()`, `clear_ptes()`, `wrprotect_ptes()`, `clear_young_dirty_ptes()`, `modify_prot_start_ptes()`, and `modify_prot_commit_ptes()`. Huge mapping support is represented by THP-oriented helpers such as `pmdp_huge_get_and_clear()`, `pudp_huge_get_and_clear()`, `pmdp_invalidate()`, `pmdp_invalidate_ad()`, deposit/withdraw hooks, `p?d_set_huge()`, `p?d_clear_huge()`, and `p?d_leaf()` fallbacks. `pgtbl_mod_mask` and `enum pgtable_level` describe modified page-table levels.

## Control Flow
Most logic is inline fallback control flow selected by `#ifndef` architecture overrides and `CONFIG_MMU`, THP, high-PTE, soft-dirty, huge-vmap, and lazy-MMU configuration. Page-table walkers compute level indexes and boundary ends, skip folded levels transparently, and clear bad entries through externally implemented `*_clear_bad()` routines. Batched PTE helpers loop over same-PMD, same-folio ranges, advance PFNs, and preserve dirty/accessed bits where needed. Lazy MMU mode uses per-task counters in `current->lazy_mmu_state`, entering architecture lazy mode only at the outer transition and flushing/leaving when nested sections close or pause/resume brackets require it.

## State and Persistence
The header does not own persistent storage, but it mutates durable MM state through caller-held page-table locks. It tracks PTE dirty/accessed metadata, soft-dirty metadata, swap metadata hooks, zero-page identity, PFN cache-mode tracking, and page-table synchronization masks. Correctness depends on refcounted pages, `mm_struct` page tables, `vm_area_struct` permissions, TLB flush ordering, RCU/highpte unmap discipline, and architecture page-table atomicity guarantees.

## Dependencies and Integration Points
Depends on `<asm/pgtable.h>`, `<linux/mm_types.h>`, `<linux/page_table_check.h>`, architecture TLB/cache hooks, THP, GUP, swap, vmalloc/ioremap, PAT-style PFN map tracking, and page-fault/rmap code. Architecture ports integrate by defining `__HAVE_ARCH_*` hooks, folded page-table macros, leaf predicates, pgprot modifiers, lockless accessors, and synchronization masks.

## Risks
The main risks are architecture fallback mismatch, lost hardware dirty/accessed bits during non-atomic updates, missing TLB flushes, incorrect behavior with folded levels, bad huge-page PFN fallbacks, and callers violating documented locking/context constraints. The lazy MMU API explicitly warns against sleeping and stale raw PTE reads while updates are batched.

## Test Signals
Relevant signals include MM selftests, GUP-fast stress, THP collapse/split/migration tests, mprotect/soft-dirty/userfaultfd tests, swap-in/out metadata tests, page-table-check failures, KASAN/KCSAN findings around page-table races, vmalloc/ioremap mapping tests, and architecture boot tests with different page-table level folding.
