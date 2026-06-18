# Research: subset-b-000790

Grouped research for PowerPC Book3S64 MMU implementation files under `sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_64k.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_64k.c

Purpose: Implements hash page-table fault insertion/update for 64K Linux base pages, including the special case where hardware uses 4K HPTEs inside a 64K software PTE. This is a low-level Book3S hash MMU path used after `hash_page_mm()` has found a present Linux PTE and selected the effective page size.

Important APIs and functions: `__hash_page_4K()` handles sub-4K hardware mappings for a Linux 64K page. `__hash_page_64K()` handles direct 64K HPTE insertion/update. `__rpte_sub_valid()` and `hpte_soft_invalid()` validate per-subpage hash slot metadata held in `real_pte_t`. Both hashing functions consume `mmu_hash_ops` callbacks for `hpte_insert`, `hpte_updatepp`, `hpte_remove`, and `hpte_invalidate`, and use helpers such as `htab_convert_pte_flags()`, `hash_page_do_lazy_icache()`, `pte_get_hash_gslot()`, `flush_hash_page()`, and `hpt_do_stress()`.

Control flow: Both paths first atomically set `H_PAGE_BUSY`, `_PAGE_ACCESSED`, and conditionally `_PAGE_DIRTY` with `pte_xchg()`, returning to the fault path on busy PTEs or permission mismatch. The 4K path applies subpage protection, computes the subpage index, invalidates a previous 64K HPTE when converting to combo mode, updates an existing subpage HPTE if valid, otherwise inserts into primary then secondary hash groups and evicts/retries on full groups. The 64K path refuses unsupported cache-inhibited large-page mappings, updates an existing HPTE if possible, or inserts a new 64K HPTE.

State and persistence: Persistent state lives in the Linux PTE bits: `H_PAGE_BUSY`, `H_PAGE_HASHPTE`, `H_PAGE_COMBO`, `_PAGE_HPTEFLAGS`, and packed hash slot indexes. The 4K path initializes invalid subpage slot metadata with `INVALID_RPTE_HIDX`. No disk state exists; persistence is CPU/MMU runtime state.

Dependencies and integration: Called from `hash_utils.c` through `hash_page_mm()` and `hash_preload()`. It depends on page-size definitions, VSID/VPN hashing, `mmu_hash_ops` backend registration from native/pseries/PS3 code, and PowerPC PTE flag layout constraints asserted during hash MMU init.

Risks: Incorrect busy-bit handling can deadlock faults. Slot encoding must avoid software-invalid values, especially secondary slot value `0xf`. Failed hypervisor insertion restores the old PTE but leaves the fault path responsible for SIGBUS/debug output. Conversions between 64K and 4K combo mappings require HPTE invalidation or stale translations remain.

Test signals: Exercise user faults on 64K kernels with normal, write, execute, cache-inhibited, and subpage-protected mappings. THP demotion and `stress_hpt` help expose hash collision retry paths. KUnit or fault-injection coverage should validate `__rpte_sub_valid()` and soft-invalid slot handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_64k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_hugepage.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_hugepage.c

Purpose: Provides transparent huge page hash insertion for Book3S hash MMU, mapping a PMD-sized THP or devmap PMD with HPTEs whose actual page size is 16M while the base page size may be 4K or 64K.

Important APIs and functions: The sole exported implementation is `__hash_page_thp()`. It uses `get_hpte_slot_array()` to find the deposited PTE fragment used as per-subpage HPTE metadata, `hpte_valid()`, `hpte_hash_index()`, `mark_hpte_slot_valid()`, `flush_hash_hugepage()`, `htab_convert_pte_flags()`, and `mmu_hash_ops` update/insert/remove callbacks.

Control flow: The function atomically locks the PMD with `pmd_xchg()` and updates accessed/dirty state. It rejects non-THP PMDs by checking `H_PAGE_THP_HUGE`. It computes the base-page index within the huge PMD from the fault address and selected `psize`. For 4K base size, it invalidates older 64K HPTEs if the PMD was hashed without combo mode, then clears the slot array. If the target slot is valid it computes the global slot and tries `hpte_updatepp()`. On misses it inserts into primary then secondary hash groups, removing an entry and retrying when both are full. Finally it marks the slot valid, sets `H_PAGE_COMBO` for 4K base mappings, orders slot metadata with `smp_wmb()`, and clears `H_PAGE_BUSY`.

State and persistence: HPTE state is tracked by PMD bits plus the deposited PTE fragment slot array. The PMD busy bit serializes writers and protects slot-array updates. There is no persistent storage beyond in-memory page tables and hardware hash table entries.

Dependencies and integration: Invoked by `hash_page_mm()` when `find_linux_pte()` reports a huge PMD that is a THP. It integrates with `hash_pgtable.c` deposit/withdraw logic and native/pseries hash backends.

Risks: Slot-array lifetime is critical; withdraw/split paths must not race with hashing. The 4K fallback conversion path must clear old 64K metadata or future faults may update the wrong HPTE. Insert retry loops depend on backend eviction making progress.

Test signals: THP fault, split, collapse, mprotect, and devmap PMD tests on hash MMU are relevant. Useful stress signals include `stress_hpt`, concurrent THP collapse/split with page faults, and mixed 4K/64K slice page sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_hugepage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_native.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_native.c

Purpose: Implements the native bare-metal hash page table backend. It supplies the function table used by generic hash code to insert, remove, protect, invalidate, batch-flush, and clear HPTEs without hypervisor calls.

Important APIs and functions: `hpte_init_native()` registers `native_hpte_insert`, `native_hpte_remove`, `native_hpte_updatepp`, `native_hpte_updateboltedpp`, `native_hpte_removebolted`, `native_hpte_invalidate`, `native_hpte_clear`, `native_flush_hash_range`, and `native_hugepage_invalidate`. Local helpers include HPTE bit locking (`native_lock_hpte()`/`native_unlock_hpte()`), TLB invalidation primitives (`___tlbie()`, `__tlbie()`, `__tlbiel()`, `tlbie()`), `native_hpte_find()`, and `hpte_decode()`.

Control flow: Insert scans an HPTE group, locks an invalid entry, writes `r`, orders with `eieio()`, then writes valid `v` and releases the HPTE lock. Remove randomly scans a group for a valid non-bolted entry and clears it. Update-protection compares the encoded AVPN, locks and updates PPP/N/C bits, then invalidates the TLB unless suppressed. Invalidate clears a matching HPTE and always issues TLB invalidation because eviction may not flush. Batched flush first clears matching HPTEs for each recorded real PTE, then emits either local `tlbiel` or global `tlbie` operations with required barriers. Kexec clear walks the entire HPT and decodes entries without taking locks.

State and persistence: State is the global `htab_address` array and per-entry valid/bolted/lock bits. `native_tlbie_lock` serializes global TLB invalidation on CPUs lacking lockless `tlbie`. Lockdep state models HPTE locks.

Dependencies and integration: Depends on hash encoding helpers, CPU feature flags, tracepoints, `ppc64_tlb_batch`, and page-size definitions filled by `hash_utils.c`. It is selected during `hash__early_init_mmu()` when not using LPAR/PS3 backends.

Risks: Barrier placement is architecture-critical. Missing invalidation on remove/update can expose stale TLB entries. Kexec clear intentionally avoids locks and is unsafe outside the single-CPU/MMU-off context. POWER9 errata paths add extra invalidations and must track CPU feature bits.

Test signals: Boot native hash on POWER generations, kexec/crashdump, memory hotplug for bolted removal, THP invalidation, lockdep under HPTE contention, and TLB batching via `lazy_mmu_mode` are strong signals. Trace `tlbie` events can confirm expected flush scope.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_native.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_pgtable.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_pgtable.c

Purpose: Provides hash-MMU page-table operations around vmemmap bolting, kernel mapping, transparent huge page updates, HPTE flushing during PMD transitions, and strict kernel RWX permission changes.

Important APIs and functions: `hash__vmemmap_create_mapping()` and `hash__vmemmap_remove_mapping()` bolt/remove vmemmap mappings. `hash__map_kernel_page()` maps ioremap/kernel pages. THP APIs include `hash__pmd_hugepage_update()`, `hash__pmdp_collapse_flush()`, `hash__pgtable_trans_huge_deposit()`, `hash__pgtable_trans_huge_withdraw()`, `hpte_do_hugepage_flush()`, `hash__pmdp_huge_get_and_clear()`, and `hash__has_transparent_hugepage()`. Strict RWX hooks are `hash__mark_rodata_ro()` and `hash__mark_initmem_nx()`.

Control flow: Vmemmap creation bolts the physical range into the HPT and removes partial mappings on failure. Kernel mapping either builds Linux page tables after slab is available or directly bolts early mappings. THP PMD updates use an atomic loop that waits for `H_PAGE_BUSY`, updates bits, traces, and flushes HPTEs when `H_PAGE_HASHPTE` was set. Collapse clears the PMD, serializes against lockless PTE lookup with IPIs, then flushes all base HPTEs. Deposit stores the PTE fragment in the second half of the PMD page; withdraw clears that slot and zeros hash-index metadata. Strict RWX changes bolted HPTE protection, using `stop_machine()` on LPAR to run secondaries in real mode while the master updates entries.

State and persistence: Persistent state is page-table memory, PMD slot metadata, bolted HPTEs, and direct-map page counts. The static `chmem_parms` lives in real-mode-accessible memory and is serialized by `chmem_lock`.

Dependencies and integration: Integrates with generic THP callbacks, sparsemem vmemmap, memory hotplug, `mmu_hash_ops`, `flush_hash_hugepage()`, and page-table-check instrumentation.

Risks: PMD format differs from PTE format, so the serialization against `__find_linux_pte()` is essential. Deposited page-table storage is hash-specific and must remain valid across THP faults. RWX changes on LPAR have delicate real-mode and CPU rendezvous requirements.

Test signals: THP collapse/split/mprotect tests, sparsemem hotplug add/remove, strict kernel RWX boot checks, ioremap before/after slab availability, and page_table_check warnings are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_pgtable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_tlb.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_tlb.c

Purpose: Implements hash-MMU TLB and HPTE flush batching for Linux PTE changes, range flushes, PMD-table flushes, and `mmu_gather` teardown.

Important APIs and functions: `hpte_need_flush()` records or immediately performs HPTE invalidation for a changed PTE. `__flush_tlb_pending()` drains a per-CPU `ppc64_tlb_batch`. `hash__tlb_flush()` integrates with `mmu_gather`. `__flush_hash_table_range()` flushes init-mm HPTEs over an address range without clearing Linux PTEs. `flush_hash_table_pmd_range()` flushes all hashed PTEs under a PMD.

Control flow: `hpte_need_flush()` determines page size, huge offset, segment size, VSID, VPN, and `real_pte_t`. If lazy MMU mode is not active, it calls `flush_hash_page()` immediately. Otherwise it batches entries, forcing a drain when the `mm`, page size, or segment size changes, and drains when the batch fills. `__flush_tlb_pending()` uses the single-page path for one entry or `flush_hash_range()` for multiple. Range helpers temporarily enable lazy MMU mode with interrupts disabled, scan PTEs, and enqueue only entries with `H_PAGE_HASHPTE`.

State and persistence: The only local state is the per-CPU `ppc64_tlb_batch`, containing mm, page size, segment size, VPNs, and real PTEs. It is transient but correctness-critical until drained.

Dependencies and integration: Depends on `find_init_mm_pte()`, `pte_pagesize_index()`, `get_user_vsid()`, `get_kernel_vsid()`, `flush_hash_page()`, `flush_hash_range()`, and generic lazy MMU batching. Export visibility is enabled for KUnit on the batch and drain function.

Risks: Batches must not mix address spaces or page sizes. Flushes are sometimes done without the normal PTE lock because callers intentionally leave Linux PTEs intact; that is slower but relies on not modifying PTEs. Forgetting to drain before freeing pages can permit stale TLB access to freed memory.

Test signals: KUnit around batching, `mmu_gather` teardown, memory pressure during lazy MMU mode, PCI/IO hotplug range flushes, and THP collapse PMD-range flushes are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_utils.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_utils.c

Purpose: Central hash-MMU implementation for Book3S64. It discovers page and segment capabilities, initializes the hash page table and direct map, routes hash faults, preloads HPTEs after page faults, implements HPTE flag conversion and flush helpers, supports debug pagealloc/KFENCE, memory hotplug, HPT resizing/debugfs, and hash stress modes.

Important APIs and functions: Boot/setup APIs include `hash__early_init_devtree()`, `hash__early_init_mmu()`, `hash__early_init_mmu_secondary()`, `hash__setup_initial_memory_limit()`, and `print_system_hash_info()`. Mapping APIs include `htab_bolt_mapping()`, `htab_remove_mapping()`, `hash__create_section_mapping()`, `hash__remove_section_mapping()`, and `hash__kernel_map_pages()`. Fault APIs include `hash_page_mm()`, `hash_page()`, `do_hash_fault`, `__update_mmu_cache()`, and `hash_preload()`. Flush helpers include `pte_get_hash_gslot()`, `flush_hash_page()`, `flush_hash_hugepage()`, `flush_hash_range()`, and `hpte_insert_repeating()`.

Control flow: Early devtree scanning fills segment and page-size tables. Early MMU init selects a backend, configures page-table geometry, allocates or registers the HPT, bolts the linear map, optionally maps TCE/KFENCE regions, sets SLB state, and flushes local TLBs. Fault handling classifies the effective address region, derives VSID/segment/page size, finds the Linux PTE, handles huge pages or standard PTEs, demotes incompatible 64K segments, checks subpage protection, then calls the 4K/64K/THP/hugetlb hash insertion helpers. Cache update preload hashes young user PTEs after generic faults when safe. Flush helpers decode stored hash slot metadata and call backend invalidation.

State and persistence: Global runtime state includes `mmu_psize_defs`, `hpte_page_sizes`, `htab_address`, `htab_size_bytes`, `htab_hash_mask`, selected linear/virtual/vmalloc/io/vmemmap page sizes, segment size choices, `mmu_hash_ops`, stress static keys, debug-pagealloc/KFENCE slot arrays, and direct-map counts. This state persists for the boot lifetime.

Dependencies and integration: Integrates with firmware device tree, memblock, SLB, pseries/native/PS3 hash backends, sparsemem, hugetlb, THP, pkeys, transactional memory, SPU, EEH/TCE allocation, debugfs, and generic fault handling.

Risks: This file has high blast radius. Firmware page-size parsing drives HPTE encoding correctness. HPT sizing and bolted mapping failures can panic boot. Fault paths must avoid deadlocks by disabling interrupts/PMI around busy-bit manipulation. Segment demotion changes process slice state and requires SLB/PACA refresh. Stale HPTE slot metadata can corrupt future flushes.

Test signals: Boot on LPAR, native, and emulator paths; device-tree page-size permutations; 4K and 64K kernels; hugetlb/THP/subpage protection; memory hotplug and HPT resize; debug_pagealloc/KFENCE; transactional memory TLB abort behavior; and `stress_hpt` collision testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hugetlbpage.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hugetlbpage.c

Purpose: Implements hugeTLB support shared by Book3S64 hash/radix, with hash-specific HPTE insertion for explicit hugetlb mappings and common protection-change helpers.

Important APIs and functions: `__hash_page_huge()` hashes hugetlb PTEs when `CONFIG_PPC_64S_HASH_MMU` is enabled. `huge_ptep_modify_prot_start()` temporarily invalidates a huge PTE during protection changes. `huge_ptep_modify_prot_commit()` routes commit to radix or hash handling. `hugetlbpage_init_defaultsize()` selects the default large page size. Global `hpage_shift` is exported.

Control flow: `__hash_page_huge()` computes VPN, atomically sets `H_PAGE_BUSY`, accessed, and dirty bits, rejects THP PMDs, converts PTE flags to HPTE flags, derives the `real_pte_t` span (`PTRS_PER_PUD` for 16G, otherwise `PTRS_PER_PMD`), optionally applies lazy icache handling, updates an existing HPTE if present, or inserts a new repeating HPTE and stores slot metadata. Protection start clears `_PAGE_PRESENT` while preserving software present semantics via `_PAGE_INVALID`. Commit uses radix-specific flushing if radix is enabled, otherwise writes the huge PTE directly. Default size prefers 16M, then 1M, then 2M based on populated page-size definitions.

State and persistence: State is in hugetlb PTE flags, hash slot indexes, and exported `hpage_shift`. The protection-change window relies on the invalid-but-present PTE convention.

Dependencies and integration: Called from `hash_page_mm()` for non-THP huge mappings. Uses `htab_convert_pte_flags()`, `hash_page_do_lazy_icache()`, `hpte_insert_repeating()`, `pte_set_hidx()`, radix hugetlb commit helpers, and generic hugetlb hstate helpers.

Risks: 4K kernels bail out for young/dirty software management because hugepages span multiple contiguous upper-level entries. Hugepage shift must match `mmu_psize_defs[mmu_psize].shift` or `BUG_ON()` fires. Failed insertion restores the old PTE and propagates an error to the fault handler.

Test signals: Explicit hugeTLB faults for 16M/16G/1M/2M availability, mprotect on hugetlb VMAs, hash versus radix boot modes, and no-execute/lazy icache instruction faults provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hugetlbpage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/internal.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/internal.h

Purpose: Provides small internal declarations for Book3S64 MMU stress/static-key controls shared by hash and SLB code in this directory.

Important APIs and types: Declares `stress_slb_enabled`, `stress_hpt_enabled`, and `no_slb_preload`, plus static keys `stress_slb_key`, `stress_hpt_key`, and `no_slb_preload_key`. Inline helpers `stress_slb()`, `stress_hpt()`, and `slb_preload_disabled()` wrap `static_branch_unlikely()`. Declares `hpt_do_stress()`.

Control flow: Callers check the inline helpers in hot paths. Boot-time parsing in other files sets the booleans and early MMU initialization enables the static keys. When `stress_hpt()` is true, hash insertion paths call `hpt_do_stress()` after successful insertion to increase HPT churn.

State and persistence: State is global boot-lifetime boolean/static-key state. Static keys allow near-zero overhead in normal operation while enabling stress code dynamically during early boot.

Dependencies and integration: Depends on Linux jump labels. `hash_utils.c` defines `stress_hpt_enabled`, `stress_hpt_key`, and `hpt_do_stress()`. SLB code outside this file set likely defines the SLB symbols. `hash_64k.c` and related insertion paths include this header for `stress_hpt()`.

Risks: Header declarations must match exactly one definition elsewhere or link failures result. Static key enablement must occur after jump-label infrastructure is ready and before hot paths rely on it. Stress hooks are intentionally disruptive and should remain gated.

Test signals: Build coverage with and without hash/SLB stress options, boot with `stress_hpt` and SLB preload controls, and verify no overhead/regression in default boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/iommu_api.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/iommu_api.c

Purpose: Manages per-mm preregistered memory ranges for sPAPR TCE/IOMMU use, allowing user or device memory ranges to be pinned, looked up, translated to host physical addresses, mapped/unmapped, and released safely.

Important APIs and types: Defines private `struct mm_iommu_table_group_mem_t` with RCU list node, use count, mapped count, page shift, user address, entry count, union of `hpages`/`hpas`, and optional device HPA. Public exports include `mm_iommu_new()`, `mm_iommu_newdev()`, `mm_iommu_put()`, `mm_iommu_lookup()`, `mm_iommu_get()`, `mm_iommu_ua_to_hpa()`, `mm_iommu_is_devmem()`, `mm_iommu_mapped_inc()`, `mm_iommu_mapped_dec()`, `mm_iommu_preregistered()`, and `mm_iommu_init()`.

Control flow: Allocation accounts locked memory for normal user pages, allocates metadata, pins pages in chunks with `pin_user_pages(FOLL_WRITE | FOLL_LONGTERM)`, computes the largest usable IOMMU page shift, converts pinned page pointers to physical addresses in the reused union storage, checks overlap under `mem_list_mutex`, then adds the range to the mm RCU list. Device memory allocations skip pinning and store a base HPA. Put decrements `used`, refuses release while mappings remain, transitions `mapped` from 1 to 0, removes the range by RCU, unpins dirty pages, and unaccounts locked memory. Lookups are RCU protected; exact get increments `used` under the mutex.

State and persistence: State lives in `mm->context.iommu_group_mem_list`, per-range `used`, atomic `mapped`, pinned page references, dirty bits embedded in low HPA bits, and locked-mm accounting. The data lasts until `mm_iommu_put()` and RCU free.

Dependencies and integration: Requires `CONFIG_SPAPR_TCE_IOMMU` integration from `mmu_context.c`, GUP pinning, RCU lists, hugetlb page size detection, and mm locked-memory accounting. External IOMMU/KVM code consumes the exported opaque pointer.

Risks: The `hpages`/`hpas` union relies on pointer-sized storage reuse and ordered conversion after pinning. Long-term pins affect migration and memory pressure. Dirty marking is encoded in low physical-address bits and assumes 4K alignment. Overlap checks and use/mapped counters must prevent freeing while device mappings exist.

Test signals: VFIO/sPAPR TCE preregistration, overlapping registration rejection, long-term pin failure unwinding, hugetlb-backed preregistered memory, device-memory lookup, dirty unpin behavior, and mm teardown warnings for non-empty lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/iommu_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/mmu_context.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/mmu_context.c

Purpose: Allocates, initializes, switches, and destroys Book3S64 MMU contexts for both hash and radix translation modes.

Important APIs and functions: Context ID management uses `alloc_context_id()`, `hash__reserve_context_id()`, `hash__alloc_context_id()`, `__destroy_context()`, and `destroy_contexts()`. Lifecycle APIs include `init_new_context()`, `destroy_context()`, `arch_exit_mmap()`, and `cleanup_cpu_mmu_context()`. Hash helpers include `hash__init_new_context()` and `hash__setup_new_exec()`. Radix helpers include `radix__init_new_context()` and `radix__switch_mmu_context()`.

Control flow: Hash initialization allocates `hash_mm_context`, initializes or copies slice/subpage state depending on exec versus fork, reallocates all required context IDs, and initializes pkeys. Radix initialization allocates a PID from `mmu_base_pid`, writes the process table entry with the mm PGD and RTS field, issues `ptesync;isync`, and clears hash context. `init_new_context()` selects radix or hash, stores `mm->context.id`, initializes page-table fragment caches, IOMMU list, active CPU count, and copro count. Destruction clears radix process table entries when needed, frees hash subpage state or process IDs, frees hash context, and marks `MMU_NO_CONTEXT`. `arch_exit_mmap()` destroys fragment caches and clears radix process table before fullmm TLB flush.

State and persistence: Global state is the `IDA` context allocator. Per-mm persistent state includes context ID(s), hash context pointer, pte/pmd fragment caches, IOMMU registration list, active CPU/copro counters, and radix process table entries.

Dependencies and integration: Integrates with slice management, pkeys, pte/pmd fragment allocators, SPAPR TCE IOMMU, radix process tables, CPU hotplug, and generic task/mm lifecycle hooks.

Risks: Error unwinding during hash extended ID reallocation must not free inherited IDs incorrectly. Radix process table stores must be ordered before PID use. Fragment cache destruction must account for partial page-table pages. Teardown ordering with fullmm flush avoids stale process table caches.

Test signals: Fork/exec/exit loops under hash and radix, context ID exhaustion, subpage protection inheritance, pkeys initialization, mm teardown with IOMMU preregistration, CPU hotplug TLB flush, and radix PID switch tests are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/mmu_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/pgtable.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/pgtable.c

Purpose: Provides common Book3S64 page-table helpers shared by hash and radix modes, including huge PMD/PUD operations, MMU cleanup, memory hotplug dispatch, partition table management, page-table fragment allocation/freeing, meminfo accounting, protection updates, TLBIE controls, memremap alignment, and VMA protection construction.

Important APIs and functions: Global `mmu_psize_defs`, `mmu_vmemmap_psize`, fragment sizing exports, `pmdp_set_access_flags()`, `pudp_set_access_flags()`, `set_pmd_at()`, `set_pud_at()`, `pmdp_invalidate()`, `pudp_invalidate()`, `pmdp_huge_get_and_clear_full()`, `pudp_huge_get_and_clear_full()`, `pfn_pmd()`, `pfn_pud()`, `pmd_modify()`, `pud_modify()`, `mmu_cleanup_all()`, `create_section_mapping()`, `remove_section_mapping()`, `mmu_partition_table_init()`, `mmu_partition_table_set_entry()`, `pmd_fragment_alloc()`, `pmd_fragment_free()`, `pgtable_free_tlb()`, `__tlb_remove_table()`, `ptep_modify_prot_start()`, `ptep_modify_prot_commit()`, `pmd_move_must_withdraw()`, `memremap_compat_align()`, and `vm_get_page_prot()`.

Control flow: Huge access updates delegate to `__ptep_set_access_flags()`. Huge invalidation clears present bits and flushes the appropriate range. Memory hotplug dispatches to radix or hash implementations. Partition table setup allocates PATB, sets PTCR, updates ultravisor/NMMU state, and flushes old LPID translations if requested. PMD fragments are cached in `mm->context.pmd_frag`, with refcounts in `ptdesc`. TLB table freeing encodes the page-table level in low pointer bits for deferred free. Protection commit routes radix through radix-specific commit and hash through unchecked PTE set.

State and persistence: Persistent global state includes page-size definitions, fragment geometry, partition table entries, TLBIE enable flags, direct map counters, and cached page-table fragments. Per-mm fragment state is cleaned during context teardown.

Dependencies and integration: This file bridges generic mm, THP, radix/hash backends, ultravisor/powernv firmware, debugfs, procfs, page_table_check, memory hotplug, and memremap/ZONE_DEVICE.

Risks: It contains many architecture dispatch points, so mode checks must stay correct. Partition table flush must use the previous translation mode. Deferred table-free pointer tagging depends on alignment and `MAX_PGTABLE_INDEX_SIZE`. Hash does not support disabling `tlbie`.

Test signals: THP PMD/PUD operations, memory hotplug, kexec cleanup, KVM partition table changes, debugfs `tlbie_enabled`, proc meminfo direct-map counts, pmd fragment stress, and pkey bits in `vm_get_page_prot()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/pgtable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/pkeys.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/pkeys.c

Purpose: Implements PowerPC memory protection key discovery, default register policy, execute-only pkey support, KUAP/KUEP setup, and arch hooks for pkey access checks.

Important APIs and functions: `pkey_early_init_devtree()` discovers pkey support and initializes defaults. `setup_kuep()` and `setup_kuap()` program kernel user execution/access prevention. Under `CONFIG_PPC_MEM_KEYS`, hooks include `pkey_mm_init()`, `__arch_set_user_pkey_access()`, `execute_only_pkey()`, `__arch_override_mprotect_pkey()`, `arch_pte_access_permitted()`, `arch_vma_access_permitted()`, and `arch_dup_pkeys()`. Helpers parse device tree storage keys and manipulate AMR/IAMR bit fields.

Control flow: Early init rejects radix and pre-POWER7, scans CPU nodes for `ibm,processor-storage-keys`, falls back to 32 keys on known bare-metal POWER8/9 cases, clamps to arch-neutral pkey flag capacity, initializes AMR/IAMR/UAMOR defaults, reserves key 1, optionally reserves key 2 for execute-only, reserves key 3 for KUAP/KUEP, and marks unsupported keys reserved. KUAP/KUEP setup programs AMR/IAMR on each CPU and sets MMU feature bits on the boot CPU. User pkey access updates validate UAMOR permission, update current thread AMR/IAMR saved register images, and reject unsupported execute-disable requests.

State and persistence: Global boot-lifetime state includes `num_pkey`, `reserved_allocation_mask`, `initial_allocation_mask`, `default_amr`, `default_iamr`, `default_uamor`, `execute_only_key`, and `pkey_execute_disable_supported`. Per-mm state includes allocation bitmap and execute-only key. Per-thread state lives in AMR/IAMR register values.

Dependencies and integration: Integrates with device tree, CPU feature/PVR detection, firmware LPAR detection, `mprotect`, generic pkeys, VMA flags, PTE pkey bits, and kernel user protection options.

Risks: Radix does not support the same pkey mechanism, so early mode checks are important. UAMOR must prevent userspace from changing reserved keys. Execute-only behavior depends on IAMR support and key availability. Foreign VMA checks intentionally skip current-thread AMR enforcement.

Test signals: Boot with and without pkey device-tree properties, pkey_alloc/free/mprotect tests, execute-only mappings, KUAP/KUEP boot logs and access faults, fork pkey duplication, and ptrace/foreign-mm access behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/pkeys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/radix_hugetlbpage.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/radix_hugetlbpage.c

Purpose: Provides radix-specific hugetlb TLB flushing and protection-commit behavior.

Important APIs and functions: `radix__flush_hugetlb_page()`, `radix__local_flush_hugetlb_page()`, `radix__flush_hugetlb_tlb_range()`, and `radix__huge_ptep_modify_prot_commit()` are the file's public operations. They derive page size from the hugetlb hstate and delegate to radix TLB helpers.

Control flow: Single-page flush reads the VMA file hstate, gets the PowerPC page-size index, and calls global or local radix page-size flush. Range flush uses PWC flush when the range is at least `PUD_SIZE`, otherwise normal page-size range flush, then invalidates secondary MMU notifier TLBs. Protection commit checks for POWER9 NMMU relaxed-permission erratum: if the new PTE is a RW upgrade and the mm has coprocessor users, it flushes before setting the new huge PTE. It then calls `set_huge_pte_at()`.

State and persistence: No private persistent state. It observes `mm->context.copros` and hugetlb hstate metadata and mutates hugetlb PTEs through generic setters.

Dependencies and integration: Called by common hugetlb code in `hugetlbpage.c` and generic hugetlb/radix flush paths. Integrates with `mmu_notifier_arch_invalidate_secondary_tlbs()` for secondary TLB consumers.

Risks: Page-size selection must match the hstate or the wrong radix flush encoding may be used. POWER9 NMMU requires a flush before permission relaxation for coprocessor contexts; missing that can leave secondary translations with stale permissions.

Test signals: hugetlb mprotect RW upgrades with active coprocessor/NMMU users, local and global flush tests, PUD-sized range invalidations, and secondary MMU notifier validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/radix_hugetlbpage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/radix_pgtable.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/radix_pgtable.c

Purpose: Implements radix page-table initialization, kernel/direct mapping, strict RWX changes, partition/process table setup, memory hotplug removal, vmemmap population/free/optimization, THP helpers, PTE access updates, and generic hugepage page-table helpers.

Important APIs and functions: Mapping/init APIs include `radix__map_kernel_page()`, `radix__early_init_devtree()`, `radix__early_init_mmu()`, `radix__early_init_mmu_secondary()`, and `radix__mmu_cleanup_all()`. Memory/VMEMMAP APIs include `radix__create_section_mapping()`, `radix__remove_section_mapping()`, `radix__vmemmap_create_mapping()`, `radix__vmemmap_populate()`, `vmemmap_populate_compound_pages()`, `radix__vmemmap_remove_mapping()`, and `radix__vmemmap_free()`. THP and PTE APIs include `radix__pmd_hugepage_update()`, `radix__pud_hugepage_update()`, `radix__pmdp_collapse_flush()`, deposit/withdraw helpers, `radix__ptep_set_access_flags()`, `radix__ptep_modify_prot_commit()`, `pud_set_huge()`, `pud_clear_huge()`, `pud_free_pmd_page()`, `pmd_set_huge()`, `pmd_clear_huge()`, and `pmd_free_pte_page()`.

Control flow: Early mapping allocates page tables from memblock until slab is available, selecting PUD/PMD/PTE mappings based on alignment and supported page sizes. Direct-map creation walks mem ranges, splits around kernel text/rodata boundaries, updates direct-page counters, and handles KFENCE early pool mapping. Radix MMU init sets page-table geometry, builds process table, reserves guard PID, configures LPCR/PTCR or pseries backend, switches to init guard PID, and flushes TLBs. Hotplug removal recursively clears leaf/non-leaf tables and frees empty page tables. Vmemmap population chooses PMD-sized backing where possible, falls back to base pages for altmap boundaries, and supports compound-page tail-page deduplication. Access updates handle POWER9 NMMU permission-relaxation erratum by invalidating before installing relaxed PTEs.

State and persistence: Persistent state includes `mmu_base_pid`, radix process table, partition table entries, init-mm page tables, direct-map counters, vmemmap mappings/backing pages, and optional KFENCE pool. PTE/PMD/PUD contents are the primary durable runtime state.

Dependencies and integration: Integrates with memblock, sparsemem, altmap/DAX vmemmap optimization, KFENCE, strict RWX, THP, hugetlb, page_table_check, radix TLB flush helpers, powernv/pseries firmware, ultravisor, and generic memory hotplug.

Risks: Mapping-size selection must honor alignment, debug_pagealloc, and rodata/text boundaries. Vmemmap altmap boundary checks prevent mapping device memory outside its range. Recursive removal must not free non-empty tables. Process table and PID setup must avoid PID 0 aliases and stale user mappings. POWER9 coprocessor flush rules are subtle.

Test signals: Radix boot on bare metal and LPAR, direct-map page-size accounting, strict RWX, KFENCE early init, memory hotplug add/remove, sparsemem vmemmap with altmap/DAX compound optimizations, THP collapse/split, hugetlb huge PUD/PMD operations, and coprocessor permission-upgrade faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/radix_pgtable.c -->
