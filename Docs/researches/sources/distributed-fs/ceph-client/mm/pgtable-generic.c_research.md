# sources/distributed-fs/ceph-client/mm/pgtable-generic.c

## Purpose
`pgtable-generic.c` supplies generic implementations of page-table helpers declared by `linux/pgtable.h` when an architecture does not override them. It covers bad-entry clearing, access/young/dirty permission updates, transparent-hugepage page-table helpers, safe PTE mapping and locking under RCU, deferred PTE freeing, and optional asynchronous freeing of kernel page-table pages.

## Important APIs, Types, and Functions
Bad-entry handlers include `pgd_clear_bad()`, `p4d_clear_bad()`, `pud_clear_bad()`, and `pmd_clear_bad()`, each reporting an architecture error and clearing the entry. Generic access helpers include `ptep_set_access_flags()`, `ptep_clear_flush_young()`, and `ptep_clear_flush()`. THP helpers include `pmdp_set_access_flags()`, `pmdp_clear_flush_young()`, `pmdp_huge_clear_flush()`, optional `pudp_huge_clear_flush()`, `pgtable_trans_huge_deposit()`, `pgtable_trans_huge_withdraw()`, `pmdp_invalidate()`, `pmdp_invalidate_ad()`, `pmdp_collapse_flush()`, and `pte_free_defer()`.

PTE mapping helpers are `__pte_offset_map()`, `pte_offset_map_ro_nolock()`, `pte_offset_map_rw_nolock()`, and `pte_offset_map_lock()`. They provide the generic concurrency protocol for safely looking up PTE tables while another thread might remove a table, replace it with a THP PMD, or free it after RCU grace. Optional `pagetable_free_kernel()` queues kernel page-table descriptors to a work item when `CONFIG_ASYNC_KERNEL_PGTABLE_FREE` is enabled.

## Control Flow
Bad-entry handlers are invoked by page-table walk macros when an entry is neither none nor valid; they log through architecture-specific `*_ERROR()` hooks and clear the entry to stop further misuse. Access-flag helpers compare old and new entries, install more-permissive entries when changed, and flush enough TLB state for spurious faults or young-bit clearing.

THP helpers operate on PMD/PUD-sized ranges and enforce hugepage alignment with `VM_BUG_ON()`. Deposit/withdraw maintains a FIFO list of preallocated PTE tables hanging off a huge PMD so THP split/collapse code can swap between huge PMD and PTE-table representations. Invalidation helpers establish invalid PMDs and flush huge PMD ranges; collapse flushing clears PTE-table PMDs and flushes the full range because PTE mappings are being collapsed into a huge PMD.

The PTE lookup path starts `rcu_read_lock()`, obtains a lockless PMD value, rejects none, non-present, THP, or bad PMDs, and maps the PTE page. Some configurations disable interrupts around split high/low PMD reads so a successful map cannot be based on mismatched halves. `pte_offset_map_lock()` then takes the page-table lock associated with the captured PMD value and rechecks that the PMD is still the same; on mismatch it unlocks, unmaps, and retries.

## State and Persistence Behavior
The file persists no independent state except the optional `kernel_pgtable_work` queue/list. Its operations mutate page-table entries, THP deposit lists, and deferred-free RCU/workqueue state. PTE mapping helpers deliberately hold RCU read-side state until callers unmap, ensuring disconnected page-table pages remain valid while inspected. Asynchronous kernel page-table freeing persists a list of `ptdesc` objects until the worker invalidates IOMMU SVA KVA mappings and frees them.

## Dependencies and Integration Points
The implementation depends on architecture page-table accessors and flush primitives, MMU/TLB APIs, THP configuration, RCU, IOMMU SVA invalidation, and page-table allocation/free helpers. It is integrated across fault handling, mprotect, reclaim, rmap, THP split/collapse, GUP, page walkers, and kernel page-table teardown. Architectures can override many functions with `__HAVE_ARCH_*` macros, making this file the fallback contract.

## Risks and Edge Cases
The highest-risk area is concurrent PTE-table lookup while page tables are removed or replaced by huge mappings. Callers must obey the documented distinction between read-only nolock lookup, writable nolock lookup requiring later stability checks, and locked lookup. THP helpers require exact hugepage alignment and correct TLB flush granularity. Deposit/withdraw list corruption would break THP split/collapse. Deferred freeing requires RCU or worker ordering to prevent use-after-free by lockless walkers. Async kernel page-table free must invalidate IOMMU KVA range before freeing page tables.

## Test Signals
Signals include architecture builds with and without each `__HAVE_ARCH_*` override; THP split, collapse, mprotect, young-bit aging, and fault tests; lockless GUP racing with THP collapse/split and page-table teardown; bad-entry injection or debug assertions; RCU KASAN/KCSAN coverage around `pte_offset_map*`; kernel page-table free with `CONFIG_ASYNC_KERNEL_PGTABLE_FREE`; and IOMMU SVA tests that validate stale KVA translations are invalidated before async free.
