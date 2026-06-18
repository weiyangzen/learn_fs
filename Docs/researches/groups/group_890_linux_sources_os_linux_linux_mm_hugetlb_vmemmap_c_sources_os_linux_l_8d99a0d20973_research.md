# Group Research: group_890_linux_sources_os_linux_linux_mm_hugetlb_vmemmap_c_sources_os_linux_l_8d99a0d20973

Scope: `Docs/research_subset_a.md`; all listed files are under `sources/os/linux/linux`. Each source file listed in the work item was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/hugetlb_vmemmap.c -->
# File Research: sources/os/linux/linux/mm/hugetlb_vmemmap.c

Implements HugeTLB Vmemmap Optimization (HVO): deduplicating `struct page` backing memory for hugetlb folios by remapping most vmemmap PTEs to shared read-only tail metadata pages, then freeing redundant vmemmap pages.

Key flow:
- `vmemmap_remap_range()` walks kernel page tables for vmemmap ranges under `init_mm`, splitting PMD mappings when needed and optionally remapping PTEs.
- `vmemmap_remap_free()` replaces a hugetlb folio’s vmemmap mappings with a copied head page and a per-zone shared tail page, collecting old vmemmap pages for later free.
- `vmemmap_remap_alloc()` restores optimized vmemmap by allocating replacement pages and remapping them back.
- `hugetlb_vmemmap_optimize_folio(s)()` and `hugetlb_vmemmap_restore_folio(s)()` are the public HVO transitions used by hugetlb code.
- Boot-time pre-HVO support under `CONFIG_SPARSEMEM_VMEMMAP_PREINIT` can preinitialize section metadata for aligned gigantic bootmem hugetlb pages.

Important dependencies:
- Uses `init_mm.page_table_lock`, `walk_kernel_page_table_range()`, TLB flushing, `memmap_pages_add()`, `memmap_boot_pages_add()`, `init_compound_tail()`, and sparsemem helpers.
- Exposes runtime control via early param `hugetlb_free_vmemmap=` and sysctl `vm.hugetlb_optimize_vmemmap`.

Critical invariants:
- HVO requires `hugetlb_vmemmap_optimizable(h)` and skips already optimized folios.
- Head vmemmap page remains writable; tail entries are mapped read-only.
- Delayed TLB flushing is carefully coordinated when optimizing/restoring batches.
- Memory-hotplug self-hosted vmemmap pages are rejected with `-ENOTSUPP`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/hugetlb_vmemmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/hugetlb_vmemmap.h -->
# File Research: sources/os/linux/linux/mm/hugetlb_vmemmap.h

Header for HugeTLB Vmemmap Optimization.

Defines:
- `HUGETLB_VMEMMAP_RESERVE_SIZE` as one page.
- `HUGETLB_VMEMMAP_RESERVE_PAGES` as the number of `struct page` entries covered by that reserved page.
- Public HVO functions for optimize, restore, batch optimize/restore, and bootmem initialization when enabled.
- Inline disabled stubs when `CONFIG_HUGETLB_PAGE_OPTIMIZE_VMEMMAP` is off.

Key helpers:
- `hugetlb_vmemmap_size(h)` returns the byte size of vmemmap metadata for a hugetlb page.
- `hugetlb_vmemmap_optimizable_size(h)` returns reclaimable vmemmap bytes after reserving one metadata page; it requires `sizeof(struct page)` to be a power of two.
- `hugetlb_vmemmap_optimizable(h)` is the boolean predicate used by implementation and callers.

Design note:
The disabled stubs preserve hugetlb call sites without forcing feature ifdefs. The batch restore stub moves all folios to `non_hvo_folios` and returns zero, matching “nothing needed” semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/hugetlb_vmemmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/hwpoison-inject.c -->
# File Research: sources/os/linux/linux/mm/hwpoison-inject.c

Debugfs module for injecting software-simulated hardware memory poison into an arbitrary PFN.

Interfaces created under debugfs `hwpoison/`:
- `corrupt-pfn`: write PFN to call `memory_failure(pfn, MF_SW_SIMULATED)`.
- `unpoison-pfn`: write PFN to call `unpoison_memory()`.
- Filter controls for enable, device major/minor, page flags mask/value, and memcg inode when `CONFIG_MEMCG` is enabled.

Key behavior:
- Injection requires `CAP_SYS_ADMIN` and a valid PFN.
- Optional filtering can restrict targets by backing device, stable page flags, and memcg.
- When filters are active, it calls `shake_folio()` and only proceeds for LRU folios, hugetlb folios, or free buddy pages.
- A racy precheck is used before `memory_failure()`, which then repeats reliable checks under proper locking.
- `-EOPNOTSUPP` from `memory_failure()` is converted to success for testing convenience.

Dependencies:
- Uses internal memory-failure hooks declared in `mm/internal.h`: `hwpoison_filter_register()`, `hwpoison_filter_unregister()`, and `shake_folio()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/hwpoison-inject.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/init-mm.c -->
# File Research: sources/os/linux/linux/mm/init-mm.c

Defines the global kernel `init_mm` and a dummy VMA ops table.

Core content:
- `const struct vm_operations_struct vma_dummy_vm_ops;` provides an empty operations table used when a VMA’s real hooks must no longer be invoked after error/close paths.
- `struct mm_struct init_mm` initializes the kernel address-space descriptor with:
  - `swapper_pg_dir`
  - maple tree `mm_mt`
  - reference counts
  - mmap/page-table/arg locks
  - per-VMA lock state when configured
  - scheduler mm CID lock when configured
  - architecture `INIT_MM_CONTEXT()`

`setup_initial_init_mm()` records kernel text/data/brk boundaries in `init_mm`.

Importance:
This is foundational shared state. Many files in this group use `init_mm` directly for kernel page table operations, including HVO vmemmap remapping, generic ioremap, and KASAN shadow setup.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/init-mm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/internal.h -->
# File Research: sources/os/linux/linux/mm/internal.h

Large internal MM header collecting cross-file declarations, inline helpers, data structures, and configuration stubs for Linux memory management implementation files.

Major areas covered:
- VMA and page-table movement state via `struct pagetable_move_control` and `PAGETABLE_MOVE()`.
- GFP masks, allocation warning helpers, page writeback, reclaim, and show-mem flags.
- Folio mapping helpers, swap-entry batching, PTE batching for large folios, anon-vma locking/refcounting, and VMA hook safety helpers.
- Page-cache, truncate, reclaim, LRU, mlock, fault, readahead, and address-space invalidation declarations.
- Buddy allocator internals, pageblock helpers, compound folio initialization, page allocation/free declarations, watermarks, CMA, compaction, and sparsemem hooks.
- Memory-failure declarations used by hwpoison injection.
- Vmalloc/ioremap remap preparation, GUP internal flags and COW-unshare rules, soft-dirty helpers, shrinker debug helpers, workingset hooks, mmu-notifier wrappers, and max-map-count access.

Important inline logic:
- `folio_pte_batch_flags()` identifies contiguous PTE batches mapping a large folio while optionally merging dirty/young/write state.
- `swap_pte_batch()` detects contiguous swap PTE batches with matching swap cgroup IDs.
- `page_is_buddy()` and `find_buddy_page_pfn()` encode buddy allocator coalescing rules.
- `gup_must_unshare()` decides when read-only `FOLL_PIN` must break COW/exclusivity.
- `mmap_file()` and `vma_close()` replace VMA hooks with dummy ops after error/close to prevent unsafe later callbacks.

Role:
This header is not one subsystem; it is an internal MM contract surface. Many declarations here connect implementation files across `mm/`, and incorrect changes have broad allocator, reclaim, fault, page-table, and filesystem mmap impact.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/interval_tree.c -->
# File Research: sources/os/linux/linux/mm/interval_tree.c

Implements interval trees used for reverse mapping of file-backed and anonymous VMAs.

Key pieces:
- Defines `vma_interval_tree` over `struct vm_area_struct` using `shared.rb`, `shared.rb_subtree_last`, `vm_pgoff`, and `vma_last_pgoff()`.
- `vma_interval_tree_insert_after()` inserts a VMA immediately after another VMA with the same start offset, updating augmented subtree-last values.
- Defines anon-vma interval tree wrappers over `struct anon_vma_chain`.
- Public wrappers insert, remove, and iterate anon-vma interval tree nodes.
- Under `CONFIG_DEBUG_VM_RB`, cached start/last offsets are stored and verified.

Purpose:
These trees let the MM quickly find VMAs mapping a file offset range or anonymous folio range, supporting rmap, unmap, migration, reclaim, and memory-failure operations.

Invariant:
`vma_interval_tree_insert_after()` requires identical start pgoff between `node` and `prev`, enforced by `VM_BUG_ON_VMA()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/interval_tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/ioremap.c -->
# File Research: sources/os/linux/linux/mm/ioremap.c

Generic implementation of ioremap/iounmap helpers.

`generic_ioremap_prot()`:
- Rejects calls before slab is available.
- Rejects zero-size and wraparound physical ranges.
- Page-aligns the physical address and size while preserving the original offset.
- Allocates a vmalloc area in `[IOREMAP_START, IOREMAP_END)` using `__get_vm_area_caller()`.
- Stores `phys_addr` in the `vm_struct`.
- Maps the range via `ioremap_page_range()`.
- Returns a tagged `__iomem` pointer with the original offset restored.

`ioremap_prot()` is exported when the architecture has not supplied its own macro/implementation.

`generic_iounmap()`:
- Masks to page boundary.
- Calls `vunmap()` only for addresses recognized by `is_ioremap_addr()`.

`iounmap()` is exported when not architecture-defined.

This file is a small generic fallback; architecture code may override the public names while still using these helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/ioremap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kasan/Makefile -->
# File Research: sources/os/linux/linux/mm/kasan/Makefile

Build rules for KASAN runtime and KUnit tests.

Key build controls:
- Disables KASAN, UBSAN, and KCOV instrumentation for KASAN runtime objects to avoid self-instrumentation recursion.
- Removes ftrace from runtime objects for the same reason.
- Adds KASAN runtime flags:
  - optional `-fno-conserve-stack`
  - `-fno-stack-protector`
  - `-DDISABLE_BRANCH_PROFILING`
- Configures test CFLAGS from `$(CFLAGS_KASAN)`, adding `-fno-builtin` when compiler memintrinsic instrumentation is not prefix-based.

Objects:
- Always builds `common.o` and `report.o`.
- Generic KASAN adds `init.o`, `generic.o`, `report_generic.o`, `shadow.o`, `quarantine.o`.
- Hardware tag KASAN adds `hw_tags.o`, `report_hw_tags.o`, `tags.o`, `report_tags.o`.
- Software tag KASAN adds `init.o`, `report_sw_tags.o`, `shadow.o`, `sw_tags.o`, `tags.o`, `report_tags.o`.
- KUnit test object includes C tests and Rust test helper when Rust is enabled.

Role:
This Makefile is part of KASAN correctness: instrumentation flags are as important as object selection because KASAN cannot safely instrument its own low-level runtime.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kasan/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kasan/common.c -->
# File Research: sources/os/linux/linux/mm/kasan/common.c

Common KASAN runtime code shared across modes.

Main responsibilities:
- Defines/export runtime enabled static key for deferred or hardware-tag modes.
- Saves stack traces and allocation/free tracks.
- Enables/disables per-task KASAN depth for generic/software-tag modes.
- Poisons/unpoisons page, slab, kmalloc, large kmalloc, mempool, stack, and vmalloc ranges.
- Assigns tags for tag-based modes while preserving stable tags for constructor or `SLAB_TYPESAFE_BY_RCU` caches.
- Validates invalid free and double free by checking object alignment and accessibility.
- Integrates with quarantine for generic mode and skips KFENCE addresses.

Important paths:
- `__kasan_unpoison_pages()` assigns a random tag, unpoisons page memory, and records page tags unless highmem or sampled out.
- `__kasan_slab_alloc()` assigns object tags and unpoisons slab objects.
- `__kasan_slab_free()` poisons freed objects, records free metadata, and optionally quarantines.
- `__kasan_kmalloc()` and `__kasan_kmalloc_large()` poison precise redzones.
- `__kasan_krealloc()` unpoisons new accessible size and re-poisons kmalloc redzones.
- `__kasan_unpoison_vmap_areas()` gives multi-area vmalloc allocations a shared tag.

Correctness notes:
KASAN avoids touching KFENCE allocations, uses mode-specific precision, and treats `still_accessible` RCU frees specially to avoid hiding `SLAB_TYPESAFE_BY_RCU` misuse.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kasan/common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kasan/generic.c -->
# File Research: sources/os/linux/linux/mm/kasan/generic.c

Core Generic KASAN runtime.

Main functionality:
- `kasan_init_generic()` enables KASAN after architecture shadow setup.
- Inline shadow checks implement fast validation for 1, 2, 4, 8, 16, and variable-size accesses.
- `kasan_check_range()` validates address metadata, overflow, zero size, and poisoned shadow state.
- Exports compiler ABI entry points: `__asan_load*`, `__asan_store*`, `__asan_loadN`, `__asan_storeN`, and noabort aliases.
- Handles compiler-emitted alloca poisoning/unpoisoning and shadow byte setters.
- Registers global variables by unpoisoning the object and poisoning global redzones.
- Computes adaptive slab redzone sizes and lays out KASAN allocation/free metadata.
- Saves allocation/free stack metadata and auxiliary stacks.

Important metadata logic:
- `kasan_cache_create()` marks caches with `SLAB_KASAN | SLAB_NO_MERGE`, adds alloc/free metadata when possible, and grows object size to include adaptive redzones.
- Free metadata may live inside the object or in the redzone depending on object size, constructor, `SLAB_TYPESAFE_BY_RCU`, and SLUB debug.
- `KASAN_SLAB_FREE_META` shadow byte marks valid free metadata.

Role:
This file is the byte-precise shadow-memory KASAN engine. Tag-based modes use different access-check mechanisms and do not use this metadata/quarantine-heavy layout.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kasan/generic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kasan/hw_tags.c -->
# File Research: sources/os/linux/linux/mm/kasan/hw_tags.c

Hardware tag-based KASAN runtime, mainly for architectures with memory tagging such as arm64 MTE.

Boot parameters:
- `kasan=off|on`
- `kasan.mode=sync|async|asymm`
- `kasan.vmalloc=off|on`
- `kasan.write_only=off|on`
- `kasan.page_alloc.sample=<interval>`
- `kasan.page_alloc.sample.order=<order>`

Core behavior:
- `kasan_init_hw_tags_cpu()` enables tag checks on each MTE-capable CPU unless KASAN is disabled.
- `kasan_init_hw_tags()` verifies hardware support, applies boot parameter selections, initializes tags, enables KASAN, and prints mode/vmalloc/stacktrace/write-only state.
- `kasan_enable_hw_tags()` selects sync/async/asymmetric hardware tag checks and attempts write-only mode when requested.
- Page allocation sampling state is exposed through globals and per-CPU skip counters.

Vmalloc handling under `CONFIG_KASAN_VMALLOC`:
- Only VM_ALLOC mappings with normal protections are tagged.
- Non-VM_ALLOC and executable mappings are left untagged.
- `__kasan_unpoison_vmalloc()` assigns/reuses a tag, unpoisons valid bytes, poisons in-page redzone, and stores page tags so direct page access works.
- `__kasan_poison_vmalloc()` does not retag because backing pages follow page-allocator paths.

KUnit exports provide hooks to force async faults and query write-only mode.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kasan/hw_tags.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kasan/init.c -->
# File Research: sources/os/linux/linux/mm/kasan/init.c

KASAN shadow memory initialization and zero-shadow mapping management.

Key data:
- `kasan_early_shadow_page`: early read-only shadow backing page, later reused as zero shadow.
- Early page-table arrays for p4d/pud/pmd/pte levels depending on `CONFIG_PGTABLE_LEVELS`.

Initialization flow:
- `early_alloc()` allocates page-table memory from memblock before slab is ready.
- `kasan_populate_early_shadow()` populates a shadow range with mappings to the shared early shadow page, using large page-table coverage where alignment permits.
- `zero_pte/pmd/pud/p4d_populate()` build zero-shadow mappings and allocate lower-level tables either from slab or memblock.

Removal/addition:
- `kasan_remove_zero_shadow(start, size)` walks shadow page tables and clears entries that map the early shadow page, freeing now-empty page-table levels.
- `kasan_add_zero_shadow(start, size)` repopulates zero shadow for a memory range and rolls back on failure.

Invariants:
- Add/remove sizes must be aligned to `KASAN_MEMORY_PER_SHADOW_PAGE`.
- Removal validates that present PTEs point at the early shadow page before clearing.
- This code directly manipulates `init_mm` page tables and is therefore architecture/page-table-layout sensitive.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kasan/init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kasan/kasan.h -->
# File Research: sources/os/linux/linux/mm/kasan/kasan.h

Private KASAN header shared by KASAN runtime, reports, quarantine, and tests.

Defines:
- Static-key helpers for stack collection and vmalloc tagging.
- Hardware-tag mode enum and globals.
- Page allocation sampling helpers for hardware-tag mode.
- Mode-dependent `kasan_requires_meta()`, `KASAN_GRANULE_SIZE`, shadow constants, poison values, and metadata layout constants.
- Report structures, compiler ABI structures for globals/source locations, alloc/free metadata, quarantine link, and tag-mode stack ring entries.

Important APIs declared:
- Access checking and reporting: `kasan_check_range()`, `kasan_report()`, invalid-free reporting.
- Metadata/report helpers: allocation size, first bad address, mode completion, metadata rows, tag printing, stack frame printing.
- Slab metadata: alloc/free meta accessors and initialization.
- Stack trace saving and alloc/free info recording.
- Generic quarantine operations, with no-op stubs for non-generic modes.
- Tag helpers: `set_tag()`, `get_tag()`, `kasan_random_tag()`, hardware tag arch wrappers.
- Poison/unpoison primitives and generic-only partial last-granule poisoning.
- KUnit test hooks and compiler-emitted ASAN/HWASAN function declarations.

Role:
This file is the internal ABI contract between compiler instrumentation, architecture tag operations, generic shadow poisoning, KASAN reports, and allocator integration. Several struct layouts and constants are explicitly compiler ABI and must not change casually.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kasan/kasan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kasan/kasan_test_c.c -->
# File Research: sources/os/linux/linux/mm/kasan/kasan_test_c.c

KUnit test suite for KASAN bug-detection capabilities across generic, software-tag, and hardware-tag modes.

Harness:
- Suite init refuses to run if KASAN is disabled.
- Enables KASAN KUnit test mode and temporary multi-shot reporting.
- Registers a console trace probe to detect `BUG: KASAN:` and asynchronous fault messages.
- `KUNIT_EXPECT_KASAN_RESULT()` runs expressions, handles hardware-tag sync fault re-enable, optionally forces async faults, and compares observed reports with expectation.
- Helpers skip tests depending on config and checked memintrinsic availability.

Coverage areas:
- kmalloc/slab/page allocation out-of-bounds, use-after-free, invalid free, double free, `krealloc()`, `ksize()`, and `kfree_sensitive()`.
- memcpy/memset/memmove and string/memchr/memcmp instrumentation.
- Atomics and bitops instrumentation.
- RCU/workqueue auxiliary stack reporting.
- Custom kmem caches, `SLAB_TYPESAFE_BY_RCU`, cache destruction, memcg accounted caches, and bulk allocation.
- Mempool poisoning for kmalloc, large kmalloc, slab, and page pools.
- Global, stack, and dynamic alloca redzones.
- vmalloc/vmap/vm_map_ram tagging and vmalloc OOB behavior.
- Tag-mode properties: non-assignment of match-all tags, match-all pointer tag behavior, and absence of match-all memory tags.
- Rust UAF smoke test through `kasan_test_rust_uaf()`.
- `copy_to_kernel_nofault()` when built-in and copy-to/from-user instrumentation.

Test list:
The `kasan_kunit_test_cases[]` table registers all scenarios and marks atomics as slow. The suite is named `kasan`.

Important nuance:
Many tests are mode-specific because generic KASAN has byte-precise shadow and quarantine, while tag-based modes use granule tags and may not precisely detect unaligned or adjacent-object cases.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kasan/kasan_test_c.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kasan/kasan_test_rust.rs -->
# File Research: sources/os/linux/linux/mm/kasan/kasan_test_rust.rs

Rust helper crate for the KASAN KUnit suite.

Exports:
- `#[no_mangle] extern "C" fn kasan_test_rust_uaf() -> u8`

Behavior:
- Allocates a `KVec<u8>`.
- Pushes 4096 bytes of `0x42`.
- Takes a raw mutable pointer to element 2048.
- Drops the vector.
- Unsafely dereferences the stale pointer.

Purpose:
This intentionally creates a Rust use-after-free through `unsafe` code so the C KUnit suite can verify that Rust code is sanitized by KASAN. The matching C test is `rust_uaf()` in `kasan_test_c.c`, gated by `CONFIG_RUST`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kasan/kasan_test_rust.rs -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kasan/quarantine.c -->
# File Research: sources/os/linux/linux/mm/kasan/quarantine.c

Generic KASAN quarantine implementation for delaying reuse of freed slab objects.

Data structures:
- `qlist_head`: singly linked queue with head, tail, byte count, and offline flag.
- Per-CPU `cpu_quarantine` queues.
- Global round-robin `global_quarantine[]` batch array protected by `quarantine_lock`.
- Per-CPU `shrink_qlist` staging queues.
- SRCU domain `remove_cache_srcu` for cache-removal synchronization.

Key behavior:
- `kasan_quarantine_put()` queues freed objects in per-CPU quarantine. When a per-CPU queue exceeds 1 MiB, it is moved to global quarantine and batched.
- `kasan_quarantine_reduce()` trims global quarantine when over its dynamic max, recalculating limits from total RAM and online CPUs.
- `kasan_quarantine_remove_cache()` removes and frees all quarantined objects belonging to a cache, coordinating per-CPU lists, global lists, and in-flight reduction with `on_each_cpu()` and SRCU.
- CPU hotplug callbacks mark per-CPU queues offline/online and free quarantined objects on offline.

Important details:
- `qlink_to_object()` reconstructs object address from KASAN free metadata offset.
- `qlink_free()` preserves metadata for UAF-before-realloc reports, but zeros in-object free metadata when `init_on_free` requires it.
- Quarantine is generic-KASAN-only; tag-based modes use stack rings and tag mismatch rather than delayed reuse.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kasan/quarantine.c -->