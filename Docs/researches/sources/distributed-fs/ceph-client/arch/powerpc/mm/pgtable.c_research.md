# sources/distributed-fs/ceph-client/arch/powerpc/mm/pgtable.c

## Purpose
This file contains common PowerPC page-table operations: the kernel `swapper_pg_dir`, PTE filtering for I-cache/D-cache coherency and execute permission, PTE installation, access-flag updates, hugepage PTE writes, debug lock assertions, vmalloc-to-physical lookup, Linux page-table walking, and the VM protection map.

## Important APIs, Types, And Functions
Important APIs include `set_ptes()`, `set_pte_at_unchecked()`, `unmap_kernel_page()`, `ptep_set_access_flags()`, `huge_ptep_set_access_flags()`, `set_huge_pte_at()`, `assert_pte_locked()`, `vmalloc_to_phys()`, and `__find_linux_pte()`. Helpers `set_pte_filter()`, `set_pte_filter_hash()`, `set_access_flags_filter()`, and `maybe_pte_to_folio()` enforce cache and execute semantics.

## Control Flow
PTE installation filters the requested PTE before writing it. Hash or embedded nohash systems without coherent I-cache/no-execute support may flush `flush_dcache_icache_folio()` and set `PG_dcache_clean`, or temporarily remove execute permission until an execution fault proves the page must execute. `set_ptes()` writes a run of PTEs after `page_table_check_ptes_set()` and asserts no hardware-valid replacement is happening without flush. Access-flag updates apply the execution-fault filter and call `__ptep_set_access_flags()` when changed. `__find_linux_pte()` walks PGD/P4D/PUD/PMD safely using local copies and detects leaf huge mappings.

## State And Persistence
Persistent state includes `swapper_pg_dir`, modified PTEs, folio `PG_dcache_clean`, and protection constants in `protection_map`. No separate allocator state is owned here.

## Dependencies And Integration Points
It integrates generic Linux MM hooks with PowerPC MMU feature flags, radix/hash detection, hugetlb, THP serialization states, page-table check, TLB flush helpers, and cache maintenance.

## Risks And Test Signals
Risks include executable stale I-cache, over-filtering `_PAGE_EXEC`, writing hardware-valid PTEs without invalidation, THP split/collapse races in `__find_linux_pte()`, and hugepage size stepping errors. Test signals include JIT or mmap executable faults, `mprotect(PROT_EXEC)`, hugetlb mappings, THP stress, page-table debug, vmalloc lookups, and non-coherent embedded CPUs.
