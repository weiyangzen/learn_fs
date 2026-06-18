## sources/distributed-fs/ceph-client/mm/hugetlb_vmemmap.c

Purpose: implements HugeTLB Vmemmap Optimization (HVO), deduplicating and later restoring the `struct page` vmemmap backing for HugeTLB folios. It remaps redundant tail vmemmap PTEs to shared read-only tail pages, frees the old vmemmap pages, and restores full vmemmap backing before a HugeTLB folio returns to the buddy allocator.

Important APIs and functions: exported callers are `hugetlb_vmemmap_restore_folio()`, `hugetlb_vmemmap_restore_folios()`, `hugetlb_vmemmap_optimize_folio()`, `hugetlb_vmemmap_optimize_folios()`, `hugetlb_vmemmap_optimize_bootmem_folios()`, and, with `CONFIG_SPARSEMEM_VMEMMAP_PREINIT`, early and late bootmem init functions. Core internals are `vmemmap_remap_range()`, `vmemmap_split_pmd()`, `vmemmap_remap_free()`, `vmemmap_remap_alloc()`, `vmemmap_remap_pte()`, `vmemmap_restore_pte()`, and `vmemmap_get_tail()`.

Control flow: optimization first checks `vmemmap_should_optimize_folio()`, obtains a per-zone shared tail page, allocates and copies a head vmemmap page, walks the kernel page tables, splits PMD mappings if needed, installs a writable head PTE and read-only shared tail PTEs, then frees displaced vmemmap pages after TLB synchronization. Batch optimization pre-splits PMDs, defers flushes with `VMEMMAP_REMAP_NO_TLB_FLUSH`, flushes globally, and retries when freed vmemmap memory can satisfy earlier allocation pressure. Restore allocates replacement vmemmap pages, initializes tail metadata from existing compound-tail data, remaps PTEs back to private pages, and clears the optimized folio flag.

State and persistence: state lives in folio flags, `zone->vmemmap_tails[]`, page-table entries under `init_mm`, memmap accounting counters, and bootmem hugepage flags. It has no filesystem persistence.

Dependencies and integration: depends on HugeTLB hstates, sparsemem vmemmap, memory hotplug self-hosted vmemmap checks, memblock/buddy allocators, page-table walkers, `init_mm.page_table_lock`, and TLB flush APIs. Integration is with HugeTLB allocation/free paths and boot-time gigantic page setup.

Risks and test signals: hazards are stale TLB access during deferred flushes, PMD split races, failed partial remaps, self-hosted hotplug vmemmap, incorrect compound-tail initialization, and zone-spanning bootmem pages. Useful tests include HugeTLB allocation/free with HVO on and off, bootmem gigantic pages, memory hotplug, OOM during PMD split/head-page allocation, and debug checks for read-only tail writes.
