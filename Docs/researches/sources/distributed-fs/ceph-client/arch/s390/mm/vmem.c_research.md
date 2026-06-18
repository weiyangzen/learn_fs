## sources/distributed-fs/ceph-client/arch/s390/mm/vmem.c

Purpose: manages s390 kernel virtual memory mappings for the direct map, vmemmap, KASAN range, and ad hoc 4K mappings. It allocates/frees page-table levels, uses large direct-map entries when possible, supports memory hotplug, and initializes kernel text/rodata protections.

Important APIs, types, and functions: `vmem_crst_alloc()`, `vmem_pte_alloc()`, `vmemmap_populate()`, `vmemmap_free()`, `vmem_add_mapping()`, `vmem_remove_mapping()`, `arch_get_mappable_range()`, `vmem_get_alloc_pte()`, `__vmem_map_4k_page()`, `vmem_map_4k_page()`, `vmem_unmap_4k_page()`, and `vmem_map_init()`. Internal walkers are `modify_pte_table()`, `modify_pmd_table()`, `modify_pud_table()`, `modify_p4d_table()`, and `modify_pagetable()`.

Control flow: mapping changes are serialized by `vmem_mutex` at public entry points. `modify_pagetable()` validates alignment and ensures the range is limited to direct-map/vmemmap/KASAN-safe regions, then recursively allocates or removes levels. Direct mappings use 2 GiB PUD or 1 MiB PMD large entries when aligned, supported, and debug pagealloc allows it; vmemmap mappings allocate backing pages or use altmap and optimize partially used PMD frames with `PAGE_UNUSED` markers. Removing mappings clears entries, frees empty tables, and flushes the kernel TLB range. `vmem_map_init()` applies ROX/RO protections to kernel text and rodata and may force 4K direct-map entries under debug pagealloc.

State and persistence: persistent global state includes `vmem_mutex` and `unused_sub_pmd_start`; page tables and direct-map counters are mutated. Vmemmap backing pages may come from memblock, buddy allocator, or altmap.

Dependencies and integration points: depends on memblock, memory hotplug, vmem_altmap, pageattr splitting, direct-map counters, debug_pagealloc, EDAT facilities, KASAN bounds, lowcore/absolute mapping limits, TLB flushing, and kernel section symbols.

Risks: partial vmemmap PMD optimization relies on `PAGE_UNUSED` poisoning and consecutive section behavior. Removal must not touch page tables outside allowed kernel mapping areas. Direct-map large-page accounting must match actual entries. `vmem_get_alloc_pte()` treats existing large entries as errors because callers expect 4K-only areas.

Test signals: memory hot-add/remove, vmemmap populate/free with and without altmap, debug_pagealloc forcing 4K direct map, KASAN shadow mapping, direct-map large-page counters, 4K map/unmap APIs, and rodata/text permission checks after boot.
