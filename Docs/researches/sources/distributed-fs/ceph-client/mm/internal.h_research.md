## sources/distributed-fs/ceph-client/mm/internal.h

Purpose: central private header for MM subsystem implementation. It gathers declarations, inline helpers, flags, and shared structs used across page allocation, reclaim, rmap, page faults, VMA manipulation, compaction, sparsemem, GUP, vmalloc, memory failure, shrinkers, and mmap remapping.

Important APIs and types: notable definitions include `struct pagetable_move_control` and `PAGETABLE_MOVE()`, GFP masks, folio mapcount helpers, `mmap_file()`, `vma_close()`, anon-vma locking/refcount helpers, `folio_pte_batch_flags()`, swap PTE batching helpers, `struct alloc_context`, buddy allocator helpers (`buddy_order()`, `page_is_buddy()`, `find_buddy_page_pfn()`), compound folio setup helpers, `struct compact_control`, `folio_within_range()`, mlock helpers, GUP flags and `gup_must_unshare()`, sparsemem setup helpers, hwpoison declarations, vmalloc/internal remap declarations, and MMU notifier young-bit wrappers.

Control flow: this file has little standalone execution; it shapes control flow by providing inline policy to other MM files. Examples include fault handlers calling `vmf_anon_prepare()`, reclaim paths using `acct_reclaim_writeback()`, rmap/page-fault paths using PTE batch detection, allocators using buddy validation and allocation flags, and mmap paths using `maybe_rmap_unlock_action()` after hidden-rmap remaps.

State and persistence: most state is external, but helpers interpret and mutate persistent kernel state in folios, pages, VMAs, zones, page tables, mem_sections, anon_vmas, and mm_structs. The header defines invariants such as lock expectations, mapcount sentinel bits, allocation reserve flags, and `sysctl_max_map_count` access.

Dependencies and integration: depends on almost every core MM abstraction plus `vma.h`. It is an integration nexus for cross-file private contracts and must remain consistent with architecture page table APIs, memcg/swap, compaction, sparsemem, vmalloc, hugetlb, DAX, KSM, and notifier implementations.

Risks and test signals: because helpers are widely inlined, subtle changes can cause global MM regressions. Risk areas are lock ordering, race windows in buddy and GUP paths, incorrect PTE batch merging, mapcount overflow assumptions, and config-specific stubs. Test signals include MM selftests, KASAN/KCSAN/lockdep, swap migration, THP/large folio tests, mlock, GUP-fast, memory hotplug, compaction, reclaim, and mmap/mremap stress.
