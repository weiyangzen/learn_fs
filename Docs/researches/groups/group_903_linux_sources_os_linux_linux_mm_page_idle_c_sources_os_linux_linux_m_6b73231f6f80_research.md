# Group Research: group_903_linux_sources_os_linux_linux_mm_page_idle_c_sources_os_linux_linux_m_6b73231f6f80

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/page_idle.c -->
# File Research: sources/os/linux/linux/mm/page_idle.c

Implements Linux idle page tracking through the `/sys/kernel/mm/page_idle/bitmap` binary sysfs file. The bitmap lets privileged userspace mark PFNs idle and later query whether they stayed idle after clearing hardware/software referenced state.

Key responsibilities:
- Creates the `page_idle` sysfs attribute group under `mm_kobj`, exposing a 0600 binary `bitmap` attribute.
- Converts bitmap offsets to PFN ranges using 64-bit chunks and rejects unaligned reads/writes.
- Filters PFNs to online, head, LRU folios via `page_idle_get_folio()`, intentionally ignoring non-user-memory pages.
- On writes, clears current PTE/PMD young state through reverse mapping and marks selected folios idle.
- On reads, rechecks idle folios by clearing PTE/PMD references and MMU notifier young state before reporting a bit as still idle.
- Uses `rmap_walk()` and `page_vma_mapped_walk()` to visit mappings, including PTE-mapped THP and PMD-mapped THP cases.

Important behavior:
- Only LRU folios are tracked because they are safe for reverse-map walking; isolated and non-LRU pages are silently treated as non-idle.
- Referenced mappings clear `folio_idle` and set `folio_young` to avoid confusing reclaim after idle tracking clears access bits.
- The read/write return value is byte progress through completed bitmap chunks, not necessarily the original count if `max_pfn` truncates the request.
- PMD/PTE young clearing is paired with `mmu_notifier_clear_young()` so secondary MMUs participate in access tracking.

Dependencies:
- Relies on page idle flags from `linux/page_idle.h`, page extensions, rmap, `page_vma_mapped_walk()`, MMU notifiers, THP helpers, memory hotplug PFN validation, and sysfs binary attributes.

Notable risks:
- The folio must remain LRU after taking a reference; the helper revalidates this race explicitly.
- Correctness depends on holding the folio lock while walking mappings and on gracefully skipping locked or unmapped folios.
- Bitmap ABI alignment is strict: userspace must use `sizeof(u64)` aligned positions and lengths.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/page_idle.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/page_io.c -->
# File Research: sources/os/linux/linux/mm/page_io.c

Swap I/O implementation for writing swapcache folios to backing storage and reading them back. It covers swapfile activation extent discovery, zero-page swap optimization, zswap integration, block-device swap I/O, and filesystem-provided swap I/O.

Key responsibilities:
- Implements generic swapfile activation by walking file blocks with `bmap()`, requiring page-sized contiguous disk runs and building swap extents.
- Handles swap write completion and read completion for block-device BIO paths.
- Detects zero-filled folios on swapout, records entries in the swap `zeromap`, and avoids physical I/O for those pages.
- Clears stale zeromap bits when non-zero data is written to reused swap entries.
- Integrates zswap store/load and memcg zswap writeback policy.
- Provides write paths for filesystem swap operations (`swap_rw` with `swap_iocb` batching), synchronous block I/O, and asynchronous BIO block I/O.
- Provides read paths for filesystem swap operations, synchronous BIO, asynchronous BIO, zeromap reads, and zswap loads.
- Maintains swap-in/swap-out VM, memcg, THP, and multi-size THP statistics.

Important behavior:
- `swap_writeout()` first frees stale swapcache entries if possible, then lets architecture code preserve metadata via `arch_prepare_to_swap()`.
- Zero-filled folios are counted and unlocked without I/O; swapin reconstructs them by zeroing the folio and marking it uptodate.
- Filesystem swap I/O batches adjacent folios into a mempool-allocated `swap_iocb`; unplug submits through `mapping->a_ops->swap_rw()`.
- Block-device synchronous swap I/O waits with a stack BIO; asynchronous I/O owns a heap BIO and completion callback.
- Swap read accounting includes PSI/delayacct stall tracking for workingset refaults.
- Read/write errors unlock or end writeback safely and leave failed write folios dirty/reclaimable enough to avoid data loss.

Dependencies:
- Uses swap metadata, swap extents, `swap_info_struct`, folios, BIO/block layer APIs, writeback, zswap, memcg, blk-cgroup association, PSI, delay accounting, object cgroup counters, and filesystem `swap_rw` address-space operations.

Notable risks:
- Folios must enter write paths locked and in swapcache; write paths must unlock or start/end writeback in exactly the right branch.
- Zeromap correctness depends on locked swapcache folios and atomic bitmap updates, especially when swap entries are reused.
- Large folio swapin from partially zeromapped batches is intentionally not handled and is warned/error-directed.
- Filesystem batching must preserve contiguous file offsets and matching swap files before extending a plug.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/page_io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/page_isolation.c -->
# File Research: sources/os/linux/linux/mm/page_isolation.c

Pageblock isolation support for memory hotplug/offline, CMA allocation, and contiguous range allocation. It marks pageblocks `MIGRATE_ISOLATE`, prevents allocator reuse of free pages in a target range, and verifies that isolated ranges have become free or otherwise acceptable.

Key responsibilities:
- Classifies pages as movable or unmovable for a requested isolation mode.
- Scans pageblocks for unmovable pages before changing migratetype to isolate.
- Sets and unsets pageblock isolation while moving free pages between normal and isolate freelists.
- Handles pageblock boundary cases where a free or in-use higher-order page crosses the isolation boundary.
- Isolates full PFN ranges with `start_isolate_page_range()` and rolls back partial isolation on failure.
- Provides `undo_isolate_page_range()` and `test_pages_isolated()` for cleanup and final verification.
- Emits page-isolation tracepoints for test results.

Important behavior:
- Reserved pages are treated as unmovable, except `ZONE_MOVABLE` lets non-reserved pages be assumed movable.
- Hugetlb pages are movable only when architecture and hstate migration support allow it; non-LRU compound pages are otherwise rejected.
- For memory offline, HWPoison and PageOffline pages are treated as acceptable special cases.
- CMA isolation may treat CMA pageblocks as movable even when ordinary isolation would not.
- Boundary isolation first handles the start and end pageblocks to avoid accounting corruption from pages spanning a pageblock boundary.
- Unisolation may isolate and put back a large buddy page to force correct merging after clearing the isolate state.

Dependencies:
- Uses pageblock flags, buddy allocator internals, zone locks, migrate types, hugetlb migration support, memory hotplug semantics, `PageOffline`, HWPoison, `page_has_movable_ops()`, and allocator helpers from `internal.h`.

Notable risks:
- The checks are explicitly approximate for LRU and movable-ops pages; callers must still migrate/free pages and then verify isolation.
- No high-level synchronization prevents overlapping isolation attempts; races are detected through already-isolated pageblocks and reported as `-EBUSY`.
- PCP pages may still exist after isolation unless callers use stronger draining or PCP disable/enable sequencing as needed.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/page_isolation.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/page_owner.c -->
# File Research: sources/os/linux/linux/mm/page_owner.c

Page allocation ownership tracker built on `page_ext` and stack depot. When enabled by the early `page_owner` parameter, it records allocation and free stack traces, task identity, GFP mask, order, migration reason, timestamps, and exposes the data through debugfs.

Key responsibilities:
- Defines the `page_owner` page-extension payload and registers `page_owner_ops`.
- Enables tracking through an early boot parameter and initializes stack depot early when requested.
- Records allocation stacks with `__set_page_owner()` and free stacks with `__reset_page_owner()`.
- Maintains stack-record reference counts by base-page count and a linked list of observed stack records for aggregate reporting.
- Marks early allocated pages after page-owner initialization with a dedicated early stack handle.
- Updates owner metadata when pages split, migrate, or copy ownership between folios.
- Prints page-owner details for `dump_page()` diagnostics and `debugfs/page_owner`.
- Exposes aggregate stack reports under `debugfs/page_owner_stacks`, including optional handles, stack traces, page counts, and a count threshold.
- Provides mixed pageblock counting support for `/proc/pagetypeinfo`.

Important behavior:
- Recursion is avoided with `current->in_page_owner` because stack depot and list maintenance can allocate memory.
- Dummy, failure, and early stack handles distinguish recursive capture, failed stack saves, and allocations that predated full tracking.
- Freeing a page clears `PAGE_EXT_OWNER_ALLOCATED` but retains historical owner/free information.
- Migration copies the old owner to the new folio and rewrites old folio handles to preserve stack reference-count balance.
- The debugfs page scanner skips buddy pages, unowned pages, freed pages, and tail PFNs of higher-order allocations.
- Memcg information is included when available, including offline cgroups and slab/objcg cases.

Dependencies:
- Relies on `page_ext`, stack depot, stacktrace capture, debugfs, seq_file, memcg, migration reason names, pageblock migratetypes, local clock timestamps, GFP flag formatting, and page allocator hooks.

Notable risks:
- Stack-record counting is manual because this code does not use the stack depot GET API; refcount balance depends on every allocation/free/migration path.
- Debugfs scans are intentionally lock-light and can miss pages racing with concurrent allocation or free.
- Early allocated page discovery avoids zone lock contention and may skip some pages rather than risk heavy boot-time locking.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/page_owner.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/page_poison.c -->
# File Research: sources/os/linux/linux/mm/page_poison.c

Debug page poisoning implementation used by page allocator debugging when architecture debug-pagealloc mapping support is absent or when poisoning is requested. It fills freed pages with `PAGE_POISON` and checks the pattern on allocation.

Key responsibilities:
- Parses the early `page_poison=` boot parameter and exports early/runtime static-key state.
- Poisons pages by locally mapping each page, disabling KASAN checks for the current task, and filling with `PAGE_POISON`.
- Unpoisons pages by checking for bytes that differ from the poison pattern.
- Reports corruption with rate-limited messages, hex dumps, stack dumps, and `dump_page()`.
- Distinguishes a single-bit flip from broader memory corruption for diagnostics.
- Provides a no-op `__kernel_map_pages()` fallback when `CONFIG_ARCH_SUPPORTS_DEBUG_PAGEALLOC` is unavailable.

Important behavior:
- KASAN is temporarily disabled because freed pages are still treated specially by sanitizers.
- The check scans for the first and last corrupted byte so the dump covers the corrupted span only.
- Every page in a multi-page allocation is poisoned or checked independently.

Dependencies:
- Uses highmem local mappings, KASAN tag reset helpers, ratelimit state, `PAGE_POISON`, debug page dumping, and early kernel parameter parsing.

Notable risks:
- Poisoning is diagnostic and expensive; it must stay synchronized with allocator initialization and debug-pagealloc policy.
- Corruption reporting is rate-limited to avoid flooding after widespread memory damage.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/page_poison.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/page_reporting.c -->
# File Research: sources/os/linux/linux/mm/page_reporting.c

Free page reporting core. It lets one registered device driver receive batches of free pages so the platform can mark them unused, discard them, or otherwise report them to a host, while returning the pages to the buddy allocator afterward.

Key responsibilities:
- Provides the `page_reporting_order` module parameter and exported symbol.
- Maintains a single RCU-protected registered `page_reporting_dev_info`.
- Enables the allocator hot-path static key used by `page_reporting_notify_free()`.
- Schedules delayed reporting work after suitable free pages are observed.
- Walks zones, orders, and migratetypes to isolate unreported free pages into scatterlists.
- Calls the registered device `report()` callback on full or leftover scatterlists.
- Puts isolated pages back and marks them `PageReported` when reporting succeeds and the page was not coalesced into a different order.
- Supports unregister by removing the RCU pointer and canceling delayed work.

Important behavior:
- The worker has three visible states: idle, requested, and active; requests during an active pass cause another delayed pass.
- Work is delayed by two seconds to accumulate a useful batch and avoid excessive reporting frequency.
- Zone processing requires enough free memory above a low-watermark plus reporting-capacity reserve before it will pull pages.
- Isolated pages are not taken from `MIGRATE_ISOLATE` freelists.
- Each freelist pass has a budget based on the freelist size, preventing one list from monopolizing the worker.
- The zone lock is dropped while invoking the device callback and reacquired to drain pages back to the allocator.

Dependencies:
- Uses buddy free areas, pageblock migratetypes, `__isolate_free_page()`, `__putback_isolated_page()`, `PageReported`, scatterlists, workqueues, RCU, static branches, module parameters, and zone watermarks.

Notable risks:
- The callback runs outside the zone lock, so the code must rotate freelists and restart safely after dropping the lock.
- Marking a page reported is valid only if it returns as the same buddy order; coalesced pages need reporting at the larger order later.
- Registration is singleton by design; concurrent users receive `-EBUSY`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/page_reporting.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/page_reporting.h -->
# File Research: sources/os/linux/linux/mm/page_reporting.h

Internal header connecting the buddy allocator free path to the page reporting worker.

Key responsibilities:
- Declares the `page_reporting_enabled` static key and `page_reporting_order`.
- Declares `__page_reporting_notify()` for the slow notification path.
- Defines `page_reported()` to cheaply test whether reporting is enabled and a page has `PageReported`.
- Defines `page_reporting_notify_free()` for the allocator hot path.
- Provides no-op fallbacks when `CONFIG_PAGE_REPORTING` is disabled.

Important behavior:
- `page_reporting_notify_free()` first checks the static branch, then filters by order before scheduling the expensive reporting path.
- The function is explicitly intended for `__free_one_page()` and keeps the common disabled case minimal.

Dependencies:
- Includes pageblock flags, page isolation, jump labels, slab helpers, page tables, and scatterlist definitions needed by page reporting users.

Notable risks:
- The order threshold controls how often the allocator enters the reporting notification path; too small a threshold increases hot-path overhead.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/page_reporting.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/page_table_check.c -->
# File Research: sources/os/linux/linux/mm/page_table_check.c

Runtime page-table sanity checker. It uses `page_ext` counters to catch illegal mappings, especially anonymous pages mapped writable more than once or pages simultaneously mapped as anonymous and file-backed.

Key responsibilities:
- Registers `page_table_check_ops` as a page-extension user when enabled by config or the early `page_table_check=` parameter.
- Maintains per-page anonymous and file mapping counters.
- Checks counters when PTE/PMD/PUD entries are cleared or installed.
- Verifies counters are zero when pages are freed or allocated through `__page_table_check_zero()`.
- Exports clear/set hooks used by architecture and generic page-table manipulation code.
- Checks userfaultfd write-protect invariants for present and swap/migration PTE/PMD entries.

Important behavior:
- `init_mm` mappings are ignored.
- Slab pages are invalid for these checks and trigger `BUG_ON()`.
- Anonymous mappings must not coexist with file mappings; writable anonymous mappings must not have a count above one.
- Clear paths decrement counters and assert they do not go negative.
- Set paths clear the old entries first, then increment counters for user-accessible pages across batched PTE/PMD/PUD operations.
- `__page_table_check_pte_clear_range()` walks a PTE page under a non-leaf PMD and clears each PTE's accounting.

Dependencies:
- Uses `page_ext`, page-table helper predicates, swap/softleaf helpers, userfaultfd WP helpers, atomic counters, RCU-protected page extension iteration, and exported static branch state.

Notable risks:
- This checker is intentionally fatal on invariant violations; false positives in page-table helper predicates would crash the kernel.
- Correctness depends on all page-table mutation paths calling the matching clear/set hooks around replacement.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/page_table_check.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/page_vma_mapped.c -->
# File Research: sources/os/linux/linux/mm/page_vma_mapped.c

Reverse-mapping helper that finds whether a PFN range is mapped in a specific VMA and returns locked page-table entries for callers that need to inspect or modify them.

Key responsibilities:
- Implements `page_vma_mapped_walk()` for normal, THP, migration, device-private, device-exclusive, and HugeTLB mappings.
- Maps and locks PTE tables, with a stricter synchronous mode for callers that need stronger page-table stability.
- Validates PTE/PMD entries against the target PFN range.
- Handles PMD-mapped THP, PMD migration entries, PTE-mapped THP, and hugepage VMAs.
- Provides `page_mapped_in_vma()` for memory-failure users to find the virtual address of a page mapping.

Important behavior:
- Callers loop until `page_vma_mapped_walk()` returns false; each true return leaves the relevant page-table lock held until `page_vma_mapped_walk_done()`.
- PTE matching supports migration entries only when `PVMW_MIGRATION` is set.
- Device-private and device-exclusive swap-like entries are treated as valid page mappings for reverse-map accounting.
- PMD values are rechecked after locking to detect THP split or concurrent page-table changes.
- Crossing a PMD boundary unmaps the old PTE table, clears state, and sets `PVMW_PGTABLE_CROSSED`.
- HugeTLB walks use `hugetlb_walk()` and `huge_pte_lock()` and expose the huge PTE through `pvmw->pte`.

Dependencies:
- Uses rmap structures, page-table helpers, hugetlb, THP, softleaf swap entry helpers, HMM device memory encodings, VMA address helpers, and memory-failure conditional code.

Notable risks:
- Locking is delicate: callers receive PTE/PMD pointers only while the corresponding page-table lock is held.
- Non-sync PTE mapping intentionally optimizes for the common page-locked case but must retry if the PMD changes under it.
- Range overlap checks avoid overflow and must account for large entries covering more than one base page.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/page_vma_mapped.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/pagewalk.c -->
# File Research: sources/os/linux/linux/mm/pagewalk.c

Generic page-table walking framework and folio lookup helper. It drives caller-supplied callbacks over PGD/P4D/PUD/PMD/PTE levels, VMA ranges, kernel page tables, address-space mappings, HugeTLB mappings, and single-address folio walks.

Key responsibilities:
- Implements recursive page-table traversal across all levels with folded-level depth normalization.
- Invokes optional callbacks for PGD, P4D, PUD, PMD, PTE, holes, HugeTLB entries, VMA pre/post hooks, and VMA filtering.
- Supports internal PTE installation through unsafe walker variants while rejecting it from exported safe walkers.
- Splits huge PUD/PMD entries when lower-level handlers require descending into a VMA-backed subtree.
- Handles page-table races by using `ACTION_AGAIN`, `ACTION_CONTINUE`, and `ACTION_SUBTREE`.
- Provides public walkers for `mm` ranges, single VMA ranges, whole VMAs, kernel page tables, debug no-VMA walks, and all VMAs in an address_space interval.
- Implements `folio_walk_start()` to lock the page-table entry for a single address and return the mapped folio, with optional zeropage support.

Important behavior:
- `walk_page_range_mm_unsafe()` performs the core VMA iteration, treating gaps as `pte_hole()` callbacks and honoring `test_walk()`.
- Safe exported walkers call `check_ops_safe()` and reject `install_pte`, reserving page-table population for internal MM code.
- No-VMA walks do not lock PTEs for callbacks and use kernel PTE mapping where appropriate for `init_mm` or kernel addresses.
- `walk_page_mapping()` iterates the mapping interval tree under `i_mmap_rwsem` and clips each VMA to the requested page-index interval.
- `folio_walk_start()` performs a direct page-table descent, locks the relevant PUD/PMD/PTE, records level and entry pointer/value, and requires `folio_walk_end()` by the caller.
- Folio walking deliberately warns against substituting for GUP/pinning and only supports short-term references under the mmap lock.

Dependencies:
- Uses `linux/pagewalk.h`, VMA and mmap locking, hugetlb locking, THP split helpers, architecture TLB/cache hooks, page-table allocation helpers, interval trees, `vm_normal_page*()` helpers, and folio walk structures.

Notable risks:
- Walker callbacks run under caller-specified locking assumptions; incorrect `walk_lock` choice can make VMA/page-table state unstable.
- Hugepage splitting and retry behavior are intentionally conservative to avoid descending through stale or invalid page-table pages.
- Kernel/debug walkers require external synchronization for page tables that can be freed outside normal mmap locking, such as hot-remove-sensitive kernel ranges.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/pagewalk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/percpu-internal.h -->
# File Research: sources/os/linux/linux/mm/percpu-internal.h

Internal per-CPU allocator definitions shared by the percpu core, vmalloc backend, kernel-memory backend, and debug statistics code.

Key responsibilities:
- Defines `pcpu_block_md`, the bitmap-block metadata used for allocation scan hints and contiguous free-space hints.
- Defines optional per-object extension storage for memcg and allocation profiling metadata.
- Defines `struct pcpu_chunk`, including allocation/free bitmaps, chunk metadata, base address, populated bitmap, object extensions, and debug counters.
- Declares global percpu allocator state such as chunk lists, slot indices, first/reserved chunks, and the allocator spinlock.
- Provides conversion helpers between pages, bitmap bits, metadata blocks, and full accounted object size.
- Defines `struct percpu_stats` and inline stats update helpers when `CONFIG_PERCPU_STATS` is enabled.
- Provides no-op stats helpers when percpu stats are disabled.

Important behavior:
- Allocation maps operate in units of `PCPU_MIN_ALLOC_SIZE`; metadata block counts derive from physical pages served by the chunk.
- `pcpu_obj_full_size()` accounts for all possible CPUs and optional object cgroup extension storage.
- Stats updates for allocation/deallocation require `pcpu_lock`; chunk allocation/deallocation helpers take the lock internally.
- `need_pcpuobj_ext()` enables object extensions when memcg kmem accounting or memory allocation profiling requires them.

Dependencies:
- Uses percpu allocator public definitions, memcg state, optional memory allocation profiling tags, spinlocks, and chunk list globals provided by the main percpu allocator implementation.

Notable risks:
- The chunk layout is cacheline-conscious; changing fields can affect false sharing on allocator hot paths.
- Bitmap conversion helpers must stay consistent with `PCPU_MIN_ALLOC_SIZE`, `PCPU_BITMAP_BLOCK_SIZE`, and populated page accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/percpu-internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/percpu-km.c -->
# File Research: sources/os/linux/linux/mm/percpu-km.c

Contiguous kernel-memory backend for the dynamic per-CPU allocator, intended for NOMMU-style configurations that cannot use vmalloc-backed chunks.

Key responsibilities:
- Provides no-op populate/depopulate and unmap TLB flush hooks because each chunk is allocated as already-contiguous kernel memory.
- Creates chunks by allocating a `pcpu_chunk` descriptor and a power-of-two order block of pages.
- Tags each backing page with its owning per-CPU chunk for reverse lookup.
- Initializes chunk data/base address and marks all pages populated.
- Destroys chunks by freeing the contiguous page block and chunk metadata.
- Converts per-CPU addresses to pages with `virt_to_page()`.
- Verifies allocation info is compatible with the contiguous backend.
- Disables reclaim-based chunk depopulation for this backend.

Important behavior:
- Only one allocation group is supported; NUMA grouping is rejected.
- The actual page allocation is rounded up to a power of two, and the backend warns about wasted pages when the configured chunk size is not naturally aligned.
- It rejects configurations that combine contiguous percpu allocation with a paged first chunk.

Dependencies:
- Uses core percpu allocator helpers, `alloc_pages()`, `__free_pages()`, `order_base_2()`, page-to-chunk tagging, stats hooks, tracepoints, and the global `pcpu_lock`.

Notable risks:
- Memory waste can be significant if chunk size is not a power-of-two multiple of page size.
- The backend cannot reclaim/depopulate chunks, so fragmentation and memory retention differ from the vmalloc backend.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/percpu-km.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/percpu-stats.c -->
# File Research: sources/os/linux/linux/mm/percpu-stats.c

Debugfs statistics exporter for the dynamic per-CPU allocator.

Key responsibilities:
- Defines global `pcpu_stats` and saved allocation-info snapshot storage.
- Creates `debugfs/percpu_stats` at late init.
- Prints allocator configuration, global allocation/chunk statistics, and per-chunk fragmentation state.
- Scans all chunk lists and the reserved chunk under `pcpu_lock`.
- Computes per-chunk allocation sizes and free fragments from allocation and boundary bitmaps.
- Reports chunk role labels such as first chunk, reserved chunk, sidelined chunk, and to-depopulate chunk.

Important behavior:
- The output buffer for chunk analysis is sized from the maximum live `nr_alloc` across chunks, then revalidated under lock; if too small, it retries.
- Fragment sizes are stored as negative values and allocation sizes as positive values so sorting separates free fragments before allocations.
- Fragmentation is measured only from the beginning of a chunk to the last allocation.
- Statistics are in bytes unless the printed name indicates otherwise.

Dependencies:
- Uses debugfs, seq_file, sort, vmalloc/vfree, percpu internal chunk structures, allocation maps, boundary maps, global chunk lists, and `pcpu_lock`.

Notable risks:
- The debugfs read can be relatively expensive because it scans every chunk while holding the percpu allocator lock during reporting.
- The bitmap-derived fragmentation view depends on allocation/boundary map consistency maintained by the allocator core.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/percpu-stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/percpu-vm.c -->
# File Research: sources/os/linux/linux/mm/percpu-vm.c

Default vmalloc-backed dynamic per-CPU chunk allocator backend. It reserves vmalloc address ranges for chunks and populates/unpopulates physical pages per CPU on demand.

Key responsibilities:
- Resolves chunk virtual addresses back to pages with `vmalloc_to_page()`.
- Maintains a serialized temporary page-pointer array for populate/depopulate operations.
- Allocates one page per possible CPU per chunk page index, preferably on the CPU's node.
- Maps allocated pages into per-CPU vmalloc chunk addresses.
- Unmaps and frees populated pages during depopulation.
- Performs cache and TLB flushes around map/unmap operations.
- Creates chunks by allocating `pcpu_chunk` metadata and grouped vmalloc areas.
- Destroys chunks by freeing vmalloc areas and metadata.
- Decides when chunks should be reclaimed/depopulated based on empty populated pages.

Important behavior:
- The temporary pages array is shared and must be used under `pcpu_alloc_mutex`.
- Population allocates pages first, then maps them; mapping failure frees the newly allocated pages.
- Mapping each CPU's pages also tags pages with the owning chunk for reverse lookup.
- Depopulation gathers currently mapped pages, unmaps the virtual ranges, and frees the physical pages.
- Flushes cover the whole low-to-high per-CPU chunk range rather than issuing per-CPU flushes.
- Reclaim avoids the first and reserved chunks, and considers isolated chunks or chunks with at least a quarter of pages empty when global empty-populated-page pressure is high.

Dependencies:
- Uses vmalloc/vmap APIs, per-CPU group offsets and sizes, CPU/node topology, page-to-chunk tagging, cache/TLB flush helpers, core percpu allocator metadata, stats hooks, tracepoints, and `pcpu_alloc_mutex`.

Notable risks:
- Map/unmap error handling must undo partial CPU mappings and flush TLBs correctly.
- The backend assumes immutable/pre-mapped chunks are not passed to dynamic page lookup paths.
- Reclaim heuristics affect memory footprint and future allocation latency by deciding when populated pages are returned.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/percpu-vm.c -->