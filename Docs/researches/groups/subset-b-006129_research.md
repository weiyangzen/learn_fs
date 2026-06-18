# subset-b-006129 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hugetlb_vmemmap.c -->
## sources/distributed-fs/ceph-client/mm/hugetlb_vmemmap.c

Purpose: implements HugeTLB Vmemmap Optimization (HVO), deduplicating and later restoring the `struct page` vmemmap backing for HugeTLB folios. It remaps redundant tail vmemmap PTEs to shared read-only tail pages, frees the old vmemmap pages, and restores full vmemmap backing before a HugeTLB folio returns to the buddy allocator.

Important APIs and functions: exported callers are `hugetlb_vmemmap_restore_folio()`, `hugetlb_vmemmap_restore_folios()`, `hugetlb_vmemmap_optimize_folio()`, `hugetlb_vmemmap_optimize_folios()`, `hugetlb_vmemmap_optimize_bootmem_folios()`, and, with `CONFIG_SPARSEMEM_VMEMMAP_PREINIT`, early and late bootmem init functions. Core internals are `vmemmap_remap_range()`, `vmemmap_split_pmd()`, `vmemmap_remap_free()`, `vmemmap_remap_alloc()`, `vmemmap_remap_pte()`, `vmemmap_restore_pte()`, and `vmemmap_get_tail()`.

Control flow: optimization first checks `vmemmap_should_optimize_folio()`, obtains a per-zone shared tail page, allocates and copies a head vmemmap page, walks the kernel page tables, splits PMD mappings if needed, installs a writable head PTE and read-only shared tail PTEs, then frees displaced vmemmap pages after TLB synchronization. Batch optimization pre-splits PMDs, defers flushes with `VMEMMAP_REMAP_NO_TLB_FLUSH`, flushes globally, and retries when freed vmemmap memory can satisfy earlier allocation pressure. Restore allocates replacement vmemmap pages, initializes tail metadata from existing compound-tail data, remaps PTEs back to private pages, and clears the optimized folio flag.

State and persistence: state lives in folio flags, `zone->vmemmap_tails[]`, page-table entries under `init_mm`, memmap accounting counters, and bootmem hugepage flags. It has no filesystem persistence.

Dependencies and integration: depends on HugeTLB hstates, sparsemem vmemmap, memory hotplug self-hosted vmemmap checks, memblock/buddy allocators, page-table walkers, `init_mm.page_table_lock`, and TLB flush APIs. Integration is with HugeTLB allocation/free paths and boot-time gigantic page setup.

Risks and test signals: hazards are stale TLB access during deferred flushes, PMD split races, failed partial remaps, self-hosted hotplug vmemmap, incorrect compound-tail initialization, and zone-spanning bootmem pages. Useful tests include HugeTLB allocation/free with HVO on and off, bootmem gigantic pages, memory hotplug, OOM during PMD split/head-page allocation, and debug checks for read-only tail writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hugetlb_vmemmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hugetlb_vmemmap.h -->
## sources/distributed-fs/ceph-client/mm/hugetlb_vmemmap.h

Purpose: declares the HugeTLB vmemmap optimization interface and computes how much vmemmap memory can be optimized for each HugeTLB hstate.

Important APIs and types: the header exposes restore and optimize entry points for single folios and folio lists, bootmem-specific optimize/init hooks, `HUGETLB_VMEMMAP_RESERVE_SIZE`, `HUGETLB_VMEMMAP_RESERVE_PAGES`, `hugetlb_vmemmap_size()`, `hugetlb_vmemmap_optimizable_size()`, and `hugetlb_vmemmap_optimizable()`. When `CONFIG_HUGETLB_PAGE_OPTIMIZE_VMEMMAP` is disabled, inline stubs preserve call-site simplicity.

Control flow: callers can use the functions unconditionally. Enabled builds route into `hugetlb_vmemmap.c`; disabled builds return success or no-op, with `hugetlb_vmemmap_restore_folios()` moving input folios to the non-HVO list through `list_splice_init()`.

State and persistence: the header owns no state. It defines policy constants: one vmemmap page is reserved and the rest may be deduplicated when `sizeof(struct page)` is power-of-two and the HugeTLB vmemmap footprint exceeds the reserve.

Dependencies and integration: includes HugeTLB, IO, and memblock headers because the implementation spans HugeTLB metadata, boot memory, and sparse vmemmap setup. Integration points are HugeTLB free/alloc paths and sparsemem preinit code.

Risks and test signals: the main risks are arithmetic assumptions around `sizeof(struct page)` and call sites incorrectly assuming optimization exists in disabled builds. Tests should cover configs with and without `CONFIG_HUGETLB_PAGE_OPTIMIZE_VMEMMAP`, tiny hstates whose vmemmap is not optimizable, and list-restore behavior when optimization is compiled out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hugetlb_vmemmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hwpoison-inject.c -->
## sources/distributed-fs/ceph-client/mm/hwpoison-inject.c

Purpose: provides a debugfs-backed software injector for memory failure handling. It lets privileged tests poison or unpoison a PFN and optionally filter candidate pages by backing device, stable page flags, or memory cgroup.

Important APIs and functions: module init creates `debugfs/hwpoison` files `corrupt-pfn`, `unpoison-pfn`, and filter controls. Core functions are `hwpoison_inject()`, `hwpoison_unpoison()`, `hwpoison_filter()`, `hwpoison_filter_dev()`, `hwpoison_filter_flags()`, and, under `CONFIG_MEMCG`, `hwpoison_filter_task()`. It registers the filter with `hwpoison_filter_register()` from memory-failure internals.

Control flow: a write to `corrupt-pfn` requires `CAP_SYS_ADMIN`, validates the PFN, derives its folio, optionally shakes it toward LRU/free state, rejects unsupported non-LRU/non-HugeTLB/non-free pages when filtering is enabled, then invokes `memory_failure(pfn, MF_SW_SIMULATED)`. `-EOPNOTSUPP` is translated to success for unsupported test targets. A write to `unpoison-pfn` calls `unpoison_memory()`.

State and persistence: state is held in static filter variables exposed through debugfs. It persists only while the module is loaded. Exit disables filters, unregisters from memory-failure code, and removes the debugfs subtree.

Dependencies and integration: integrates with debugfs, page cache mappings, inode superblock devices, memcg inode IDs, `stable_page_flags()`, HugeTLB/LRU/free-page tests, and memory-failure recovery.

Risks and test signals: filter checks are intentionally racy and only narrow test scope; final ownership validation happens in `memory_failure()`. Risk areas include poisoning shared dirty pages outside the intended memcg, device filters on anonymous pages, and unsupported page types. Tests should exercise each debugfs knob, capability enforcement, valid/invalid PFNs, memcg filtering, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hwpoison-inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/init-mm.c -->
## sources/distributed-fs/ceph-client/mm/init-mm.c

Purpose: defines the kernel's singleton `init_mm` and a dummy VMA operations table used when a VMA's real hooks must no longer be invoked after failure or close handling.

Important APIs and data: exports `const struct vm_operations_struct vma_dummy_vm_ops`, initializes `struct mm_struct init_mm`, and provides `setup_initial_init_mm()` to fill kernel text/data/brk boundaries.

Control flow: initialization is static. `init_mm` starts with `swapper_pg_dir`, preinitialized maple tree state, reference counts, locks, optional per-VMA lock state, user namespace, scheduler MM CID lock, flexible-array initialization, and architecture-specific `INIT_MM_CONTEXT`. Later early boot calls `setup_initial_init_mm()` with linker-derived addresses.

State and persistence: `init_mm` is persistent global kernel state for kernel page tables and kernel mappings. It is not tied to a process lifetime and uses an NR_CPUS-sized cpumask strategy indirectly through static struct layout rather than dynamic allocation.

Dependencies and integration: integrates with architecture page tables, maple tree VMA storage, mmap locking, user namespaces, IOMMU/MMU context hooks, and many MM users that operate on kernel mappings.

Risks and test signals: incorrect static initialization can break kernel page-table walking, VMA accounting, locking, or architecture MM context assumptions. Test signals are mostly boot-time: successful boot, page table manipulation against `init_mm`, VMA fault/error paths that install `vma_dummy_vm_ops`, and lockdep coverage around initialized locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/init-mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/internal.h -->
## sources/distributed-fs/ceph-client/mm/internal.h

Purpose: central private header for MM subsystem implementation. It gathers declarations, inline helpers, flags, and shared structs used across page allocation, reclaim, rmap, page faults, VMA manipulation, compaction, sparsemem, GUP, vmalloc, memory failure, shrinkers, and mmap remapping.

Important APIs and types: notable definitions include `struct pagetable_move_control` and `PAGETABLE_MOVE()`, GFP masks, folio mapcount helpers, `mmap_file()`, `vma_close()`, anon-vma locking/refcount helpers, `folio_pte_batch_flags()`, swap PTE batching helpers, `struct alloc_context`, buddy allocator helpers (`buddy_order()`, `page_is_buddy()`, `find_buddy_page_pfn()`), compound folio setup helpers, `struct compact_control`, `folio_within_range()`, mlock helpers, GUP flags and `gup_must_unshare()`, sparsemem setup helpers, hwpoison declarations, vmalloc/internal remap declarations, and MMU notifier young-bit wrappers.

Control flow: this file has little standalone execution; it shapes control flow by providing inline policy to other MM files. Examples include fault handlers calling `vmf_anon_prepare()`, reclaim paths using `acct_reclaim_writeback()`, rmap/page-fault paths using PTE batch detection, allocators using buddy validation and allocation flags, and mmap paths using `maybe_rmap_unlock_action()` after hidden-rmap remaps.

State and persistence: most state is external, but helpers interpret and mutate persistent kernel state in folios, pages, VMAs, zones, page tables, mem_sections, anon_vmas, and mm_structs. The header defines invariants such as lock expectations, mapcount sentinel bits, allocation reserve flags, and `sysctl_max_map_count` access.

Dependencies and integration: depends on almost every core MM abstraction plus `vma.h`. It is an integration nexus for cross-file private contracts and must remain consistent with architecture page table APIs, memcg/swap, compaction, sparsemem, vmalloc, hugetlb, DAX, KSM, and notifier implementations.

Risks and test signals: because helpers are widely inlined, subtle changes can cause global MM regressions. Risk areas are lock ordering, race windows in buddy and GUP paths, incorrect PTE batch merging, mapcount overflow assumptions, and config-specific stubs. Test signals include MM selftests, KASAN/KCSAN/lockdep, swap migration, THP/large folio tests, mlock, GUP-fast, memory hotplug, compaction, reclaim, and mmap/mremap stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/interval_tree.c -->
## sources/distributed-fs/ceph-client/mm/interval_tree.c

Purpose: implements interval trees for file-backed VMA mappings and anonymous VMA chains. These trees support efficient reverse mapping lookups by page offset ranges.

Important APIs and functions: `INTERVAL_TREE_DEFINE()` generates `vma_interval_tree_*` and private `__anon_vma_interval_tree_*` operations. The file implements `vma_interval_tree_insert_after()`, `anon_vma_interval_tree_insert()`, `anon_vma_interval_tree_remove()`, `anon_vma_interval_tree_iter_first()`, `anon_vma_interval_tree_iter_next()`, and debug-only `anon_vma_interval_tree_verify()`.

Control flow: VMA interval start is `vm_pgoff`; end is `vma_last_pgoff()`. `vma_interval_tree_insert_after()` inserts a VMA immediately after a previous VMA with the same start offset, updating augmented subtree-last values on the right/left descent and then rebalancing with `rb_insert_augmented()`. Anon-vma functions are wrappers around generated interval-tree functions and optionally cache start/last offsets for debug verification.

State and persistence: persistent state lives in `vm_area_struct.shared.rb`, `shared.rb_subtree_last`, and `anon_vma_chain.rb/rb_subtree_last`. The file does not allocate memory or own lifetime; callers manage locking and node lifetime.

Dependencies and integration: integrates with file mapping `i_mmap` trees, reverse mapping, anonymous VMA tracking, Linux rbtree augmented callbacks, and debug VM RB checks.

Risks and test signals: risks are corrupted augmented interval maxima, insertion ordering bugs for equal starts, and stale cached offsets under VMA changes. Tests should stress mmap/munmap/mremap of shared mappings, truncate/invalidate reverse mapping walks, anon COW/fork paths, and `CONFIG_DEBUG_VM_RB` verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/interval_tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/ioremap.c -->
## sources/distributed-fs/ceph-client/mm/ioremap.c

Purpose: provides generic helpers for mapping physical IO memory into kernel virtual address space and unmapping it again.

Important APIs and functions: `generic_ioremap_prot()` allocates a VM area and maps physical pages with a supplied page protection. Weak-style wrappers `ioremap_prot()` and `iounmap()` are exported when not overridden by architecture macros. `generic_iounmap()` unmaps addresses inside the ioremap range.

Control flow: `generic_ioremap_prot()` rejects use before slab availability, rejects zero-size and physical wraparound, folds the physical page offset into the returned virtual address, page-aligns the mapping, obtains a `VM_IOREMAP` area within `IOREMAP_START..IOREMAP_END`, records `area->phys_addr`, and calls `ioremap_page_range()`. On mapping failure it frees the area. Unmap masks the supplied pointer down to the page base and calls `vunmap()` only if `is_ioremap_addr()` accepts it.

State and persistence: mapped state lives in vmalloc metadata (`struct vm_struct`) and kernel page tables until `iounmap()` removes it. No persistent storage exists.

Dependencies and integration: integrates with vmalloc area management, architecture page protections, IO memory mapping ranges, and exported driver-facing ioremap APIs.

Risks and test signals: risks include early-driver calls before slab, address overflow, leaking VM areas on failure, incorrect offset restoration, and arch-specific cacheability/protection mismatches. Tests should cover unaligned physical starts, zero and wrapping sizes, forced `ioremap_page_range()` failure, valid unmap, and arch override builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/ioremap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/Makefile -->
## sources/distributed-fs/ceph-client/mm/kasan/Makefile

Purpose: defines how the KASAN runtime and KASAN KUnit tests are built while preventing instrumentation recursion.

Important build rules: disables KASAN, UBSAN, and KCOV for the runtime directory; removes ftrace from runtime objects; defines `CC_FLAGS_KASAN_RUNTIME` with `-fno-conserve-stack`, `-fno-stack-protector`, and `-DDISABLE_BRANCH_PROFILING`; applies KASAN test compiler flags separately to `kasan_test_c.o`; and passes Rust KASAN flags to `kasan_test_rust.o`.

Control flow: object selection is config-driven. `common.o` and `report.o` are always built under KASAN. Generic mode adds `init.o`, `generic.o`, generic report, shadow, and quarantine. HW tags mode adds hardware tag files and tag reports. SW tags mode adds init, software tag, shadow, tags, and reports. KUnit test composition includes the Rust helper only when `CONFIG_RUST` is enabled.

State and persistence: no runtime state; this file controls build-time composition and instrumentation boundaries.

Dependencies and integration: integrates with Kbuild, compiler feature detection for KASAN memintrinsic prefixing, C and Rust sanitizer flags, and KUnit object aggregation.

Risks and test signals: incorrect flags can instrument the sanitizer runtime itself, causing recursion, stack protector dependency loops, or tracing recursion. Test signals are successful builds across generic, SW_TAGS, HW_TAGS, VMALLOC, KUnit, Rust, and compiler configurations, plus absence of recursive KASAN reports during boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/common.c -->
## sources/distributed-fs/ceph-client/mm/kasan/common.c

Purpose: implements mode-independent KASAN runtime integration with page allocation, slab allocation, kmalloc redzones, mempools, stack tracking, task stack unpoisoning, and vmalloc resize handling.

Important APIs and functions: key entry points include `kasan_addr_to_slab()`, `kasan_save_stack()`, `kasan_set_track()`, `kasan_save_track()`, `__kasan_unpoison_pages()`, `__kasan_poison_pages()`, `__kasan_poison_slab()`, `__kasan_init_slab_obj()`, `__kasan_slab_pre_free()`, `__kasan_slab_free()`, `__kasan_slab_alloc()`, `__kasan_kmalloc()`, `__kasan_kmalloc_large()`, `__kasan_krealloc()`, mempool poison/unpoison helpers, `__kasan_check_byte()`, and vmalloc helpers under `CONFIG_KASAN_VMALLOC`.

Control flow: allocation paths assign or reuse tags, unpoison accessible bytes, poison redzones, and save allocation stack data when enabled. Free paths validate object identity and byte accessibility, report invalid or double frees, poison the object as freed, save free stack information, and optionally divert it into quarantine. Page alloc paths skip highmem, respect hardware-tag sampling, set per-page tags, and poison freed pages. Vmalloc paths coordinate tags across multiple `vm_struct`s and handle `vrealloc()` shrink/grow poisoning.

State and persistence: state is stored in page tags, slab object shadow/tag metadata, stack depot handles, current task KASAN depth for generic/SW tags, quarantine state, and static key `kasan_flag_enabled` for deferred/hardware tag modes.

Dependencies and integration: integrates with slab internals, KFENCE bypasses, page allocator hooks, mempool hooks, stackdepot, scheduler/task stacks, vmalloc, and mode-specific poison primitives.

Risks and test signals: risks include poisoning memory that must remain RCU-accessible, losing allocation/free stack metadata, tag reuse hiding UAFs, sampling false negatives, and mishandling KFENCE or highmem. Tests should cover slab, kmalloc, large kmalloc, krealloc, page alloc, mempool, vmalloc, invalid-free, double-free, RCU slab, and stack-trace reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/generic.c -->
## sources/distributed-fs/ceph-client/mm/kasan/generic.c

Purpose: implements Generic KASAN shadow-byte checking, compiler ABI entry points, global and alloca poisoning, and slab metadata layout.

Important APIs and functions: `kasan_init_generic()`, `kasan_check_range()`, `kasan_byte_accessible()`, `__asan_load/store{1,2,4,8,16,N}()`, noabort aliases, `__asan_alloca_poison()`, `__asan_allocas_unpoison()`, `__asan_set_shadow_*()`, `kasan_cache_create()`, metadata accessors, `kasan_record_aux_stack()`, `kasan_save_alloc_info()`, and `kasan_save_free_info()`.

Control flow: inline checkers map an address to shadow memory, specialize constant access sizes, detect partial-granule violations, report invalid regions, and short-circuit when KASAN is disabled. Global registration unpoisons the object and poisons its redzone. Alloca poisoning installs left/right stack redzones. Cache creation expands object sizes for allocation/free metadata and adaptive redzones while respecting kmalloc max size, constructors, `SLAB_TYPESAFE_BY_RCU`, and slub debug metadata.

State and persistence: Generic mode uses shadow memory bytes plus per-object `kasan_alloc_meta` and `kasan_free_meta`. Free metadata validity is encoded through the object's first shadow byte as `KASAN_SLAB_FREE_META`; allocation metadata is zeroed when invalid.

Dependencies and integration: depends on compiler-emitted ASAN ABI calls, slab cache creation, stackdepot, module global registration, kmemleak, KFENCE bypass, and quarantine hooks.

Risks and test signals: risks include compiler ABI mismatch, false negatives in optimized inline checks, incorrect partial-granule handling, metadata overlap with slab debug data, and cache-size overflow. Tests should include compiler-instrumented loads/stores, memintrinsics, globals, stack/alloca redzones, cache metadata sizing, auxiliary stacks, quarantine, and KUnit generic-only cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/hw_tags.c -->
## sources/distributed-fs/ceph-client/mm/kasan/hw_tags.c

Purpose: implements hardware tag-based KASAN boot parameters, mode selection, CPU tag-check enablement, vmalloc tagging, and KUnit-only helpers.

Important APIs and state: defines early parameters `kasan=`, `kasan.mode=`, `kasan.vmalloc=`, `kasan.write_only=`, `kasan.page_alloc.sample=`, and `kasan.page_alloc.sample.order=`. Exports `kasan_mode`, `kasan_flag_vmalloc`, page allocation sampling globals, and `kasan_init_hw_tags_cpu()`, `kasan_init_hw_tags()`, `__kasan_unpoison_vmalloc()`, `__kasan_poison_vmalloc()`, and `kasan_enable_hw_tags()`.

Control flow: boot parsing records requested state. Per-CPU init skips disabled KASAN and enables hardware tag checks. Boot CPU init verifies MTE support, applies sync/async/asymmetric mode selection, toggles vmalloc tagging static key, initializes tag infrastructure, enables KASAN, and prints the active mode. Vmalloc unpoisoning tags only suitable `VM_ALLOC` normal-protection mappings, assigns or preserves a tag, unpoisons requested bytes, poisons the in-page redzone, and stores page tags for `page_address(vmalloc_to_page())` access.

State and persistence: persistent runtime state is static-key controlled enablement, selected mode, write-only flag, vmalloc tag state, page allocation sampling counters, and per-page tags for vmalloc backing pages.

Dependencies and integration: integrates with arm64 MTE-style arch hooks, static keys, early param parsing, vmalloc metadata, page tag APIs, and KUnit visibility exports.

Risks and test signals: risks include enabling unsupported MTE or write-only modes, tagging executable/non-VM_ALLOC mappings, stale tag checks after synchronous faults, and sampling reducing coverage. Tests should cover boot parameter matrix, CPU hotplug, vmalloc tagging on/off, async fault forcing, write-only behavior, and KUnit tag range tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/hw_tags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/init.c -->
## sources/distributed-fs/ceph-client/mm/kasan/init.c

Purpose: builds and tears down zero shadow mappings used by Generic and software tag-based KASAN before full shadow memory is available and for large accessible-but-uninstrumented ranges.

Important APIs and data: defines `kasan_early_shadow_page` and early page-table arrays for P4D/PUD/PMD/PTE levels. Main exported helpers are `kasan_populate_early_shadow()`, `kasan_remove_zero_shadow()`, and `kasan_add_zero_shadow()`.

Control flow: population walks kernel page tables from PGD down, installing shared early shadow tables for aligned large ranges and allocating lower-level tables via memblock before slab or page-table allocators after slab availability. All PTEs map the write-protected `kasan_early_shadow_page`. Removal walks the shadow page-table hierarchy, clears mappings only when they point to the early shadow page/tables, and frees now-empty page-table pages. Add-zero-shadow computes shadow bounds and rolls back on failure.

State and persistence: state is in global early shadow page-table arrays and kernel page tables under `init_mm`. The early shadow page later acts as reusable zero shadow for valid ranges not backed by real KASAN shadow.

Dependencies and integration: depends on memblock, `init_mm`, architecture page-table levels, `kasan_mem_to_shadow()`, slab availability, and kernel page-table allocation/free APIs.

Risks and test signals: risks include incorrect alignment to `KASAN_MEMORY_PER_SHADOW_PAGE`, clearing real shadow mappings by mistake, leaking page-table pages, and using allocation APIs before they are initialized. Tests include early boot with multiple page-table levels, memory hotplug or vmalloc shadow add/remove paths, and debug page-table validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/kasan.h -->
## sources/distributed-fs/ceph-client/mm/kasan/kasan.h

Purpose: private KASAN runtime header defining mode-specific constants, metadata layouts, report structures, tag helpers, poisoning APIs, compiler ABI declarations, and KUnit hooks.

Important APIs and types: includes `struct kasan_track`, `struct kasan_report_info`, `struct kasan_global`, Generic metadata structs, tag-mode stack ring structs, report helpers, metadata accessors, quarantine hooks, tag helpers `set_tag()`/`get_tag()`, hardware tag wrappers, poison/unpoison APIs, `kasan_random_tag()`, KUnit suite hooks, and compiler-generated `__asan_*` and `__hwasan_*` entry point declarations.

Control flow: the header selects behavior by config. Generic KASAN requires per-object metadata and uses shadow byte values for stack/global/slab/page states. Tag-based modes use invalid tags, optional stack ring tracking, and hardware or software tag accessors. Hardware-tag inline poison/unpoison maps directly to arch tag range operations; non-hardware modes use out-of-line implementations.

State and persistence: defines the shape of persistent metadata stored in slab redzones or objects, stack depot handles, tag-mode stack rings, static keys for stacktrace/vmalloc behavior, and page allocation sampling globals.

Dependencies and integration: integrates compiler ABI, slab internals, KFENCE, stackdepot, architecture MTE hooks, KUnit, Rust test linkage, and public KASAN headers.

Risks and test signals: ABI structs and magic values must not drift from compiler expectations. Risks include wrong granule size, tag mismatch semantics, metadata offset misuse, and config stubs hiding missing implementations. Tests should span all KASAN modes, compiler-generated instrumentation, Rust helper linkage, report formatting, quarantine, and hardware-tag KUnit exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/kasan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/kasan_test_c.c -->
## sources/distributed-fs/ceph-client/mm/kasan/kasan_test_c.c

Purpose: KUnit suite that deliberately triggers memory safety violations to verify KASAN detection across allocator families, compiler instrumentation, tag modes, vmalloc, globals, stacks, usercopy, and Rust interop.

Important APIs and functions: suite setup uses `kasan_kunit_test_suite_start()`, enables multi-shot reporting, and registers a console trace probe. `KUNIT_EXPECT_KASAN_RESULT()` wraps expressions, handles sync and async hardware-tag fault behavior, and checks whether a KASAN report appeared. Test cases are registered in `kasan_kunit_test_cases[]` under suite name `kasan`.

Control flow: each test allocates memory, hides pointers from compiler optimization where needed, performs an in-bounds sanity access when relevant, then executes a deliberately invalid access inside the expectation macro. The suite covers kmalloc OOB/UAF/double-free/invalid-free, large kmalloc, page allocation, krealloc grow/shrink, memintrinsics, atomics and bitops, `ksize()`, RCU/workqueue auxiliary stacks, custom kmem caches, mempools, globals, stack and alloca redzones, string/memory routines, vmalloc/vmap/vm_map_ram, tag match-all behavior, Rust UAF, kernel nofault copy, and usercopy helpers.

State and persistence: temporary global state records whether a KASAN report or async fault was observed. Allocations are freed or tied to KUnit cleanup. Multi-shot KASAN state is saved and restored around the suite.

Dependencies and integration: integrates with KUnit, tracepoints, slab/page/vmalloc/mempool APIs, user-memory test helpers, hardware-tag controls, compiler instrumentation, optional Rust, and many config gates.

Risks and test signals: tests intentionally corrupt or access poisoned memory, so they rely on KASAN report suppression from failing KUnit itself. Risks are compiler optimization removing accesses, config-specific false expectations, async fault timing, and destructive tests without quarantine. Passing KUnit cases are the primary signal that KASAN mode behavior matches expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/kasan_test_c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/kasan_test_rust.rs -->
## sources/distributed-fs/ceph-client/mm/kasan/kasan_test_rust.rs

Purpose: Rust helper for the KASAN KUnit suite. It provides a minimal unsafe Rust use-after-free trigger so the C test suite can verify that Rust code is sanitized.

Important APIs and functions: exposes `#[no_mangle] extern "C" fn kasan_test_rust_uaf() -> u8`, declared from `kasan.h` and called by `rust_uaf()` in the C KUnit tests.

Control flow: creates a `KVec<u8>`, pushes 4096 bytes using `GFP_KERNEL`, takes a raw mutable pointer to element 2048, drops the vector to free storage, then unsafely dereferences the stale pointer. The dereference is intentionally incorrect and should trigger KASAN.

State and persistence: all state is local to the helper. The vector allocation is released before the invalid access; there is no persistent state.

Dependencies and integration: depends on kernel Rust prelude, `KVec`, `GFP_KERNEL`, raw pointer operations, and C ABI linkage into the KASAN KUnit object when `CONFIG_RUST` is enabled.

Risks and test signals: the test panics on allocation failure through `unwrap()`, so it assumes test memory is available. The signal is a KASAN report observed by the C test harness when `CONFIG_RUST` and KASAN KUnit tests are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/kasan_test_rust.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/quarantine.c -->
## sources/distributed-fs/ceph-client/mm/kasan/quarantine.c

Purpose: implements Generic KASAN's quarantine for freed slab objects, delaying reuse so use-after-free accesses remain detectable.

Important APIs and data: public hooks are `kasan_quarantine_put()`, `kasan_quarantine_reduce()`, and `kasan_quarantine_remove_cache()`. Internal structures include `qlist_head`, per-CPU `cpu_quarantine`, global round-robin quarantine batches, `quarantine_lock`, SRCU domain `remove_cache_srcu`, per-CPU `shrink_qlist`, and CPU hotplug callbacks.

Control flow: freed objects with valid free metadata are appended to a per-CPU queue with IRQs disabled. When a per-CPU queue exceeds `QUARANTINE_PERCPU_SIZE`, it moves into the global batch ring under lock and advances the tail when a batch reaches target size. Reduction recomputes max size from total RAM and online CPUs, removes the oldest global batch if over budget, and frees objects outside the lock. Cache removal first drains per-CPU queues on all CPUs, scans global batches for matching cache objects, frees them, and waits for SRCU readers so concurrent reductions cannot miss objects.

State and persistence: state is in per-CPU and global linked lists of `kasan_free_meta.quarantine_link`, global byte counters, batch indices, offline flags, and size limits. It is runtime-only.

Dependencies and integration: integrates with Generic KASAN free metadata, slab `___cache_free()`, CPU hotplug, SRCU, raw spinlocks, local IRQ control, total RAM accounting, and cache shutdown/shrink hooks.

Risks and test signals: risks include missing objects during cache teardown, IRQ races with per-CPU queues, quarantine memory growth, wrong object-to-cache reconstruction, and init-on-free metadata leakage. Tests should stress UAF detection before reuse, cache destruction with quarantined objects, CPU hotplug, memory pressure reduction, and init-on-free configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/quarantine.c -->
