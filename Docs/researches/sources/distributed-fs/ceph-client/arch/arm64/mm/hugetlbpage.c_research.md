# sources/distributed-fs/ceph-client/arch/arm64/mm/hugetlbpage.c

## Purpose
This file implements the ARM64 HugeTLB architecture hooks. It translates generic hugetlb requests into ARM64 page-table formats for PUD, PMD, contiguous-PMD, and contiguous-PTE huge pages, while preserving the architecture's break-before-make requirements for contiguous mappings. It also registers the supported hstates at boot and handles ARM64-specific HugeTLB migration, lookup, clearing, access-flag, write-protect, and protection-modification flows.

## Important APIs, Types, and Functions
The public hooks are `arch_hugetlb_cma_order()`, `arch_hugetlb_migration_supported()`, `huge_ptep_get()`, `set_huge_pte_at()`, `huge_pte_alloc()`, `huge_pte_offset()`, `hugetlb_mask_last_page()`, `arch_make_huge_pte()`, `huge_pte_clear()`, `huge_ptep_get_and_clear()`, `huge_ptep_set_access_flags()`, `huge_ptep_set_wrprotect()`, `huge_ptep_clear_flush()`, `arch_hugetlb_valid_size()`, `huge_ptep_modify_prot_start()`, and `huge_ptep_modify_prot_commit()`. The key helpers are `__hugetlb_valid_size()`, `num_contig_ptes()`, `find_num_contig()`, `get_clear_contig()`, `get_clear_contig_flush()`, `clear_flush()`, and `__cont_access_flags_changed()`.

`arch_hugetlb_cma_order()` chooses the largest gigantic HugeTLB page order for CMA reservation, preferring PUD-sized sections when supported and otherwise contiguous-PMD size. `__hugetlb_valid_size()` defines the ARM64 HugeTLB support matrix. `arch_make_huge_pte()` sets the correct huge/contiguous attributes for the chosen page size, converting through `pud_pte()` and `pmd_pte()` where needed.

## Control Flow
Boot initialization flows through `hugetlbpage_init()`, which asserts `HUGE_MAX_HSTATE >= 4` and registers PUD, contiguous-PMD, PMD, and contiguous-PTE hstates according to platform support. Allocation follows the page-table hierarchy in `huge_pte_alloc()`: PGD/P4D/PUD are allocated first, then the function returns a cast PUD entry, a shared or allocated PMD entry, an allocated PTE page, or a contiguous-PMD pointer depending on `sz`. Lookup mirrors this in `huge_pte_offset()`, including normalization to `CONT_PMD_MASK` or `CONT_PTE_MASK` for contiguous groups.

Contiguous entries drive most mutation complexity. `set_huge_pte_at()` computes the number of entries and underlying granule size, emits invalid entries directly, and performs `clear_flush()` before a valid-to-valid contiguous update. `huge_ptep_set_access_flags()` detects whether write, dirty, or accessed bits differ across the contiguous group; if so, it clears and flushes the whole group, preserves dirty/young state, and writes the rebuilt entries. `huge_ptep_set_wrprotect()` and `huge_ptep_clear_flush()` use the same group-wide clear/flush path.

## State and Persistence
Persistent state is stored in page tables, not file-local dynamic structures. Dirty and young bits are folded from all entries in a contiguous group into the returned representative PTE by `huge_ptep_get()` and `get_clear_contig()`. Boot hstate registration persists in the generic hugetlb subsystem. The CMA order hook affects long-lived CMA reservation sizing when `CONFIG_CMA` is enabled.

## Dependencies and Integration Points
The file depends on generic hugetlb, MM, TLB flush, and page-table helpers from `<linux/hugetlb.h>`, `<asm/tlbflush.h>`, and `<asm/tlb.h>`. It integrates with generic hugetlb through standard `arch_*` and `huge_ptep_*` hooks, with architecture feature detection through `pud_sect_supported()` and `alternative_has_cap_unlikely(ARM64_WORKAROUND_2645198)`, and with PMD sharing through `want_pmd_share()` and `huge_pmd_share()`.

## Risks
The major risk is violating ARM64 break-before-make rules for contiguous entries, which can produce TLB conflicts or architectural undefined behavior. Incorrect contiguous group sizing can lose dirty/accessed state or clear the wrong entries. `huge_pte_offset()` returns cast pointers at multiple levels, so callers must pass matching sizes. Erratum 2645198 adds a conditional flush when executable user mappings become non-executable; missing that path can leave stale executable permissions.

## Test Signals
Useful signals include hugetlb mmap/fault/unmap tests for all supported huge sizes, migration tests under `CONFIG_ARCH_ENABLE_HUGEPAGE_MIGRATION`, dirty/accessed preservation tests for contiguous huge pages, PMD sharing tests, and boot logs showing expected `hugetlb_add_hstate()` sizes. TLB or permission regressions often surface as memory faults, failed hugepage mappings, warnings from the `VM_WARN_ON()`/`WARN_ON()` checks, or architecture-specific selftests around mprotect and exec permission changes.
