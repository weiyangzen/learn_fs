# Research: sources/distributed-fs/ceph-client/include/linux/pagewalk.h

Purpose: `pagewalk.h` defines generic page-table and folio-walk callback contracts. It lets callers traverse user or kernel page-table ranges, inspect or install entries, skip VMAs, and temporarily lock page-table entries that map a folio.

Important APIs/types/functions: `enum page_walk_lock`, `struct mm_walk_ops`, `enum page_walk_action`, `struct mm_walk`, `walk_page_range()`, `walk_kernel_page_table_range()`, lockless kernel walking, `walk_page_range_vma()`, `walk_page_vma()`, `walk_page_mapping()`, `folio_walk_flags_t`, `FW_ZEROPAGE`, `enum folio_walk_level`, `struct folio_walk`, `folio_walk_start()`, and `folio_walk_end()`.

Control flow and state: a caller fills `mm_walk_ops`, chooses a lock policy, and passes private state through `struct mm_walk`. Walk callbacks run from top-level entries down to PTEs; `pud_entry` and `pmd_entry` may set `walk->action` to descend, continue, or retry. `test_walk`, `pre_vma`, and `post_vma` gate VMA-level traversal. `install_pte` changes missing-entry behavior by forcing allocation and invoking the install hook at PTE level.

Dependencies and integration points: it depends on `linux/mm.h`, page-table types, VMA locking helpers, and architecture-specific folded page-table levels. It integrates with memory introspection, migration, NUMA, soft-dirty, pagemap, idle-page tracking, and filesystem mapping walks.

Risks and test signals: risks include incorrect mmap/VMA lock mode, unsafe access after hugetlb callbacks drop locks, mishandled folded levels, failure to split or handle huge PMDs, and leaked PTE mappings if `folio_walk_end()` is skipped. Test signals include lockdep, page-table debug checks, hugepage walk coverage, VMA skip/abort behavior, and install-PTE allocation failure paths.
