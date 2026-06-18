# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_tlb.c

Purpose: Implements hash-MMU TLB and HPTE flush batching for Linux PTE changes, range flushes, PMD-table flushes, and `mmu_gather` teardown.

Important APIs and functions: `hpte_need_flush()` records or immediately performs HPTE invalidation for a changed PTE. `__flush_tlb_pending()` drains a per-CPU `ppc64_tlb_batch`. `hash__tlb_flush()` integrates with `mmu_gather`. `__flush_hash_table_range()` flushes init-mm HPTEs over an address range without clearing Linux PTEs. `flush_hash_table_pmd_range()` flushes all hashed PTEs under a PMD.

Control flow: `hpte_need_flush()` determines page size, huge offset, segment size, VSID, VPN, and `real_pte_t`. If lazy MMU mode is not active, it calls `flush_hash_page()` immediately. Otherwise it batches entries, forcing a drain when the `mm`, page size, or segment size changes, and drains when the batch fills. `__flush_tlb_pending()` uses the single-page path for one entry or `flush_hash_range()` for multiple. Range helpers temporarily enable lazy MMU mode with interrupts disabled, scan PTEs, and enqueue only entries with `H_PAGE_HASHPTE`.

State and persistence: The only local state is the per-CPU `ppc64_tlb_batch`, containing mm, page size, segment size, VPNs, and real PTEs. It is transient but correctness-critical until drained.

Dependencies and integration: Depends on `find_init_mm_pte()`, `pte_pagesize_index()`, `get_user_vsid()`, `get_kernel_vsid()`, `flush_hash_page()`, `flush_hash_range()`, and generic lazy MMU batching. Export visibility is enabled for KUnit on the batch and drain function.

Risks: Batches must not mix address spaces or page sizes. Flushes are sometimes done without the normal PTE lock because callers intentionally leave Linux PTEs intact; that is slower but relies on not modifying PTEs. Forgetting to drain before freeing pages can permit stale TLB access to freed memory.

Test signals: KUnit around batching, `mmu_gather` teardown, memory pressure during lazy MMU mode, PCI/IO hotplug range flushes, and THP collapse PMD-range flushes are key.
