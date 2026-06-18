# sources/distributed-fs/ceph-client/include/linux/huge_mm.h

## Purpose
Defines the public MM interface for transparent huge pages (THP), multi-size THP statistics, huge PMD/PUD fault handling, splitting, migration, and huge zero folio helpers. It is a high fan-out header for MM code and architecture page-table code, with most behavior gated by `CONFIG_TRANSPARENT_HUGEPAGE`, `CONFIG_PGTABLE_HAS_HUGE_LEAVES`, and `CONFIG_HAVE_ARCH_TRANSPARENT_HUGEPAGE_PUD`.

## APIs, Control Flow, and State
Important exports include `do_huge_pmd_anonymous_page()`, `do_huge_pmd_wp_page()`, `copy_huge_pmd()`, `zap_huge_pmd()`, `change_huge_pmd()`, PUD equivalents, `vmf_insert_pfn_pmd/pud()`, and folio insertion helpers. THP policy flows through `transparent_hugepage_flags`, per-order anonymous masks, `thp_vma_suitable_orders()`, and `thp_vma_allowable_orders()`, which first applies sysfs/madvise/global policy for anonymous VMAs and then delegates to `__thp_vma_allowable_orders()`. Split control is exposed through `split_huge_page_to_list_to_order()`, `folio_split()`, `try_folio_split_to_order()`, and `deferred_split_folio()`. State is mostly global or per-cpu: THP flags, zero-folio pointers, per-order `mthp_stats`, and mm flags disabling THP. Disabled builds provide stubs returning false, zero, or `-EINVAL`.

## Dependencies, Integration, Risks, and Tests
Depends on core `mm_types`, VMA flags, pgtable primitives, sysfs kobjects, memcg, and architecture THP support. Integration points are page fault handling, madvise, khugepaged, NUMA migration, DAX/PFNMAP insertion, and zero-page mapping. Risks are alignment/order mistakes, split races, stale huge-zero-folio lifetime assumptions, and calling enabled-only paths in !THP builds. Test signals include THP sysfs policy, `smaps` THP eligibility, PMD/PUD fault tests, split/deferred split counters, migration tests, and multi-size THP stat movement.
