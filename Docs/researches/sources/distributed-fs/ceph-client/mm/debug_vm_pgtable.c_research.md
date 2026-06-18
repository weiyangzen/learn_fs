# sources/distributed-fs/ceph-client/mm/debug_vm_pgtable.c

## Purpose
This file is a late-boot self-test for architecture page-table helper semantics. It validates that generic and architecture-specific PTE/PMD/PUD/P4D/PGD helpers satisfy expectations documented in `Documentation/mm/arch_pgtable_helpers.rst`.

It is not a KUnit test; it runs via `late_initcall(debug_vm_pgtable)` and emits `WARN_ON()` failures when helpers violate expected behavior.

## Important APIs, Types, And Functions
`struct pgtable_debug_args` holds a synthetic `mm_struct`, VMA, page-table pointers, allocated lower-level page-table pages, test virtual address, page protections, test PFNs, fixed physical PFNs, swap entries, and allocation bookkeeping.

Test functions cover:

- Basic present entry transforms: `pte_basic_tests()`, `pmd_basic_tests()`, `pud_basic_tests()`, `p4d_basic_tests()`, `pgd_basic_tests()`.
- Advanced set/clear/access operations: `pte_advanced_tests()`, `pmd_advanced_tests()`, `pud_advanced_tests()`.
- Clear/populate operations: `pte_clear_tests()`, `pmd_clear_tests()`, `pmd_populate_tests()`, `pud_clear_tests()`, `pud_populate_tests()`, `p4d_clear_tests()`, `p4d_populate_tests()`, `pgd_clear_tests()`, `pgd_populate_tests()`.
- Huge/leaf/THP/HugeTLB behavior: `pmd_leaf_tests()`, `pud_leaf_tests()`, `pmd_huge_tests()`, `pud_huge_tests()`, `pmd_thp_tests()`, `pud_thp_tests()`, `hugetlb_basic_tests()`.
- Special encodings: `pte_special_tests()`, protnone tests, soft-dirty tests, swap exclusive tests, swap conversion tests, softleaf/THP migration tests, and `swap_migration_tests()`.

Setup and teardown are handled by `init_args()`, `init_fixed_pfns()`, `debug_vm_pgtable_alloc_huge_page()`, `debug_vm_pgtable_free_huge_page()`, `destroy_args()`, `phys_align_check()`, and `get_random_vaddr()`.

## Control Flow
`debug_vm_pgtable()` initializes a synthetic MM/VMA and page-table hierarchy, allocates representative pages where possible, then runs basic tests for all protection flag combinations from `VM_NONE` through `VM_SHARED | VM_EXEC | VM_WRITE | VM_READ`.

It then runs non-iterated tests for upper-level same checks, leaf/huge/protnone/soft-dirty/swap/migration/THP/HugeTLB semantics. Modifying tests are grouped under the proper page-table lock: PTE lock for PTE clear/advanced tests, PMD lock for PMD operations, PUD lock for PUD operations, and `mm->page_table_lock` for P4D/PGD operations. Finally it calls `destroy_args()` to clear entries, free allocated table pages, free huge/normal pages, free VMA, and `mmput()` the synthetic mm.

Many tests are compiled out or return early depending on configuration and runtime support: transparent huge pages, PUD THP, huge vmap, HugeTLB, soft dirty, migration, folded page-table levels, and NUMA balancing.

## State And Persistence
The test uses transient synthetic MM state and allocated pages. It writes test entries into the allocated page tables and clears them before teardown. It also uses a random user virtual address for the test hierarchy and fixed valid PFNs derived from memblock ranges or `start_kernel` physical address for helpers that need existing physical addresses but do not dereference memory.

No persistent state is kept after the late initcall completes, except warnings/logs if failures occur.

## Dependencies And Integration Points
The file depends on a broad set of MM and architecture APIs: pgtable helper macros, pte/pmd/pud/p4d/pgd allocation and locking, THP, HugeTLB, huge vmap, swap encoding, migration entries, memblock ranges, cache/TLB flushing, vmalloc, and folded-level helpers.

It is tightly coupled to architecture page-table definitions and serves as a cross-architecture compliance guard for generic MM assumptions.

## Risks And Edge Cases
Because it runs at late init, failures surface as warnings during boot rather than structured test results. Allocations can fail; some tests silently skip when required pages or features are unavailable, reducing coverage on constrained systems.

The test intentionally uses valid but sometimes not allocated fixed PFNs for helpers that should not touch memory. Architecture helper changes that begin dereferencing these PFNs could turn semantic tests into real memory hazards.

Cache flushing after setting entries is needed for arm64 `PG_arch_1` behavior; future architecture-specific side effects may require similar care. The migration test manually sets and clears `PageLocked` around migration-entry construction; mistakes there can trigger BUG_ON paths.

## Test Signals
The file is itself a boot-time self-test. Passing means no `WARN_ON()` fired during `debug_vm_pgtable()`. It complements KUnit by exercising architecture page-table helper contracts under real compiled configuration.
