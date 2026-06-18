# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_pgtable.c

Purpose: Provides hash-MMU page-table operations around vmemmap bolting, kernel mapping, transparent huge page updates, HPTE flushing during PMD transitions, and strict kernel RWX permission changes.

Important APIs and functions: `hash__vmemmap_create_mapping()` and `hash__vmemmap_remove_mapping()` bolt/remove vmemmap mappings. `hash__map_kernel_page()` maps ioremap/kernel pages. THP APIs include `hash__pmd_hugepage_update()`, `hash__pmdp_collapse_flush()`, `hash__pgtable_trans_huge_deposit()`, `hash__pgtable_trans_huge_withdraw()`, `hpte_do_hugepage_flush()`, `hash__pmdp_huge_get_and_clear()`, and `hash__has_transparent_hugepage()`. Strict RWX hooks are `hash__mark_rodata_ro()` and `hash__mark_initmem_nx()`.

Control flow: Vmemmap creation bolts the physical range into the HPT and removes partial mappings on failure. Kernel mapping either builds Linux page tables after slab is available or directly bolts early mappings. THP PMD updates use an atomic loop that waits for `H_PAGE_BUSY`, updates bits, traces, and flushes HPTEs when `H_PAGE_HASHPTE` was set. Collapse clears the PMD, serializes against lockless PTE lookup with IPIs, then flushes all base HPTEs. Deposit stores the PTE fragment in the second half of the PMD page; withdraw clears that slot and zeros hash-index metadata. Strict RWX changes bolted HPTE protection, using `stop_machine()` on LPAR to run secondaries in real mode while the master updates entries.

State and persistence: Persistent state is page-table memory, PMD slot metadata, bolted HPTEs, and direct-map page counts. The static `chmem_parms` lives in real-mode-accessible memory and is serialized by `chmem_lock`.

Dependencies and integration: Integrates with generic THP callbacks, sparsemem vmemmap, memory hotplug, `mmu_hash_ops`, `flush_hash_hugepage()`, and page-table-check instrumentation.

Risks: PMD format differs from PTE format, so the serialization against `__find_linux_pte()` is essential. Deposited page-table storage is hash-specific and must remain valid across THP faults. RWX changes on LPAR have delicate real-mode and CPU rendezvous requirements.

Test signals: THP collapse/split/mprotect tests, sparsemem hotplug add/remove, strict kernel RWX boot checks, ioremap before/after slab availability, and page_table_check warnings are important.
