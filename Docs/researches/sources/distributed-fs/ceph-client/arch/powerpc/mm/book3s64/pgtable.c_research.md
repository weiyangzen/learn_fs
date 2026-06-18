# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/pgtable.c

Purpose: Provides common Book3S64 page-table helpers shared by hash and radix modes, including huge PMD/PUD operations, MMU cleanup, memory hotplug dispatch, partition table management, page-table fragment allocation/freeing, meminfo accounting, protection updates, TLBIE controls, memremap alignment, and VMA protection construction.

Important APIs and functions: Global `mmu_psize_defs`, `mmu_vmemmap_psize`, fragment sizing exports, `pmdp_set_access_flags()`, `pudp_set_access_flags()`, `set_pmd_at()`, `set_pud_at()`, `pmdp_invalidate()`, `pudp_invalidate()`, `pmdp_huge_get_and_clear_full()`, `pudp_huge_get_and_clear_full()`, `pfn_pmd()`, `pfn_pud()`, `pmd_modify()`, `pud_modify()`, `mmu_cleanup_all()`, `create_section_mapping()`, `remove_section_mapping()`, `mmu_partition_table_init()`, `mmu_partition_table_set_entry()`, `pmd_fragment_alloc()`, `pmd_fragment_free()`, `pgtable_free_tlb()`, `__tlb_remove_table()`, `ptep_modify_prot_start()`, `ptep_modify_prot_commit()`, `pmd_move_must_withdraw()`, `memremap_compat_align()`, and `vm_get_page_prot()`.

Control flow: Huge access updates delegate to `__ptep_set_access_flags()`. Huge invalidation clears present bits and flushes the appropriate range. Memory hotplug dispatches to radix or hash implementations. Partition table setup allocates PATB, sets PTCR, updates ultravisor/NMMU state, and flushes old LPID translations if requested. PMD fragments are cached in `mm->context.pmd_frag`, with refcounts in `ptdesc`. TLB table freeing encodes the page-table level in low pointer bits for deferred free. Protection commit routes radix through radix-specific commit and hash through unchecked PTE set.

State and persistence: Persistent global state includes page-size definitions, fragment geometry, partition table entries, TLBIE enable flags, direct map counters, and cached page-table fragments. Per-mm fragment state is cleaned during context teardown.

Dependencies and integration: This file bridges generic mm, THP, radix/hash backends, ultravisor/powernv firmware, debugfs, procfs, page_table_check, memory hotplug, and memremap/ZONE_DEVICE.

Risks: It contains many architecture dispatch points, so mode checks must stay correct. Partition table flush must use the previous translation mode. Deferred table-free pointer tagging depends on alignment and `MAX_PGTABLE_INDEX_SIZE`. Hash does not support disabling `tlbie`.

Test signals: THP PMD/PUD operations, memory hotplug, kexec cleanup, KVM partition table changes, debugfs `tlbie_enabled`, proc meminfo direct-map counts, pmd fragment stress, and pkey bits in `vm_get_page_prot()`.
