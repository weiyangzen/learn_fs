# Research: subset-b-006142

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_idle.c -->
# sources/distributed-fs/ceph-client/mm/page_idle.c

## Purpose
`page_idle.c` implements the kernel idle page tracking sysfs bitmap at `mm/page_idle/bitmap`. Userspace can mark PFNs idle and later read the bitmap to identify pages that stayed idle after the kernel cleared CPU and device young/accessed state from all mappings.

## Important APIs, Types, And Functions
- `page_idle_get_folio(pfn)` resolves an online head page to an LRU folio and pins it with `folio_try_get()`.
- `page_idle_clear_pte_refs_one()` is the rmap callback that walks PTE or PMD mappings and clears young bits via `ptep_test_and_clear_young()`, `pmdp_test_and_clear_young()`, and MMU notifier callbacks.
- `page_idle_clear_pte_refs()` locks a mapped folio and invokes `rmap_walk()` with anon-vma locking support.
- `page_idle_bitmap_read()` and `page_idle_bitmap_write()` implement the binary sysfs bitmap protocol in `u64` chunks.
- `page_idle_init()` registers the `page_idle` attribute group under `mm_kobj`.

## Control Flow
Writes validate `u64` alignment, convert file offset to PFN, and for each set bit fetch the folio, clear existing PTE references, set the idle flag, and drop the reference. Reads use the same PFN iteration but report a bit only when the folio is still idle after another reference-clearing pass. The rmap callback treats any accessed PTE or THP PMD mapping as evidence that the whole folio is referenced, clears the idle flag, and sets the young folio flag so reclaim is not misled by the idle-tracker access-bit harvesting.

## State And Persistence Behavior
State is runtime-only: folio idle and young flags, CPU page-table accessed bits, and device/MMU-notifier young state. The sysfs file is a view and command channel, not persistent storage. Only online, non-tail, LRU folios are considered; non-user pages always read as non-idle and ignore set attempts.

## Dependencies And Integration Points
The file depends on sysfs/kobject registration, memory hotplug PFN lookup, folio/LRU state, rmap walking, THP PMD helpers, MMU notifiers, page extension idle flags, and `mm_kobj`. It is used by userspace page-idle tools and indirectly by reclaim diagnostics because it manipulates young/referenced state.

## Risks
- The bitmap ABI requires `pos` and `count` to be multiples of 8 bytes; callers that use byte-granular offsets get `-EINVAL`.
- Young-bit clearing can race with mapping changes; the code uses folio locking plus rmap locking, but the result is inherently a sampled signal.
- Only LRU folios are tracked, so isolated, reserved, slab, and most kernel pages are invisible by design.
- Clearing accessed bits must preserve reclaim behavior through `folio_set_young()`.

## Test Signals
- Read/write `/sys/kernel/mm/page_idle/bitmap` with aligned and unaligned offsets.
- Mark mapped anonymous, file-backed, THP, and unmapped LRU folios idle, then access them and verify the read bitmap clears.
- Exercise memory hotplug/offline PFN holes and concurrent reclaim/migration while scanning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_idle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_io.c -->
# sources/distributed-fs/ceph-client/mm/page_io.c

## Purpose
`page_io.c` implements swap activation block mapping plus swap writeout and swap read-in for folios. It bridges reclaim and fault paths to block devices, filesystem-backed swap operations, zswap, swap zero-page elision, cgroup I/O association, and VM accounting.

## Important APIs, Types, And Functions
- `generic_swapfile_activate()` maps a regular swapfile through `bmap()` into page-sized aligned swap extents.
- `swap_writeout()` is the high-level reclaim entry that handles stale swap cache, architecture swap preparation, zero-filled folio detection, zswap storage, memcg zswap writeback policy, and real swap I/O.
- `__swap_writepage()` selects filesystem swap, synchronous block device, or asynchronous block device write paths.
- `swap_read_folio()` handles swap-in accounting and selects zeromap, zswap, filesystem swap, synchronous block device, or asynchronous block device read paths.
- `struct swap_iocb` batches filesystem-backed swap I/O in `bio_vec` arrays and embeds a `kiocb`.
- `sio_pool_init()`, `swap_write_unplug()`, and `__swap_read_unplug()` manage the swap-I/O mempool and submit batched `mapping->a_ops->swap_rw()` requests.
- `end_swap_bio_write()`, `end_swap_bio_read()`, `sio_write_complete()`, and `sio_read_complete()` complete block or filesystem I/O.

## Control Flow
Swapfile activation scans file blocks in page-sized units, requires every page slot to map to contiguous PAGE_SIZE-aligned disk blocks, records extents, and updates `sis->max`, `sis->pages`, and span. Writeout first tries to free stale swap cache, lets architecture code preserve metadata, records zero-filled folios in `sis->zeromap` without I/O, clears stale zeromap bits for nonzero data, tries `zswap_store()`, checks memcg zswap writeback policy, and finally delegates to `__swap_writepage()`. Filesystem-backed writes accumulate contiguous pages in a `swap_iocb` until the plug is full or discontiguous, then submit through `swap_rw()`. Block-device writes build either a stack bio for synchronous I/O or an allocated bio for async completion. Read-in wraps submission time in workingset delayacct/PSI accounting, services zeromap by zeroing and marking uptodate, tries `zswap_load()`, protects zswap if backing I/O is required, and submits via the selected filesystem or block path.

## State And Persistence Behavior
Persistent external state is the swap area contents and swap extent mapping stored in `swap_info_struct`. Runtime state includes folio dirty/writeback/uptodate/lock/reclaim bits, swapcache membership, `sis->zeromap`, zswap entries, memcg and objcg counters, VM events, `swap_iocb` objects from `sio_pool`, and bio ownership. Failed writes redirty pages and clear reclaim; successful reads mark folios uptodate and unlock them.

## Dependencies And Integration Points
This file integrates with reclaim, swap cache, block layer bios, filesystem `swap_rw`, `bmap`, zswap, memcg, blkcg, objcg accounting, PSI and delay accounting, THP/mTHP stats, architecture swap hooks, task lifetime handling for synchronous swap reads, and swap extent management from `mm/swapfile.c`.

## Risks
- Swapfile activation rejects holes, discontiguity, and misalignment; filesystem changes to `bmap()` behavior can make swap activation unsafe or unavailable.
- Zeromap correctness depends on clearing old bits before nonzero writes and handling large folios only when the queried zeromap batch is complete.
- Filesystem swap batching must not merge requests across files or noncontiguous offsets.
- Completion paths must always end writeback or unlock folios exactly once, even on partial filesystem I/O.
- Data-race reads of immutable swap flags rely on those flags not changing for the selected I/O mode.

## Test Signals
- Swapon regular files with holes, discontiguous blocks, and aligned extents.
- Swap out/in zero-filled and nonzero small and large folios, verifying `SWPOUT_ZERO`/`SWPIN_ZERO` and absence of stale zero reads.
- Exercise zswap hit, miss, store, writeback-disabled, and backing-device fallback paths.
- Test filesystem-backed swap with plugged contiguous I/O and discontiguous unplug boundaries.
- Inject block and filesystem I/O errors and verify dirtying, unlock/writeback completion, and ratelimited alerts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_isolation.c -->
# sources/distributed-fs/ceph-client/mm/page_isolation.c

## Purpose
`page_isolation.c` isolates ranges of physical memory at pageblock granularity for memory offlining and contiguous allocation. It marks pageblocks `MIGRATE_ISOLATE`, moves free pages to isolation freelists, handles boundary cases where large pages cross isolation boundaries, and tests whether isolated ranges have become free.

## Important APIs, Types, And Functions
- `page_is_unmovable()` classifies a page as unmovable for a given `enum pb_isolate_mode`.
- `has_unmovable_pages()` scans one pageblock intersection for pages that prevent isolation.
- `set_migratetype_isolate()` and `unset_migratetype_isolate()` mutate pageblock migration type and zone isolation accounting.
- `isolate_single_pageblock()` isolates a boundary pageblock and validates or handles larger pages crossing the boundary.
- `start_isolate_page_range()`, `undo_isolate_page_range()`, and `test_pages_isolated()` are the external range operations.
- `__test_page_isolated_in_pageblock()` verifies that pages are free, HWPoisoned/offline-acceptable, or otherwise not blocking offlining.

## Control Flow
Range isolation aligns the requested PFNs to pageblock boundaries, isolates the first boundary block, isolates the last boundary block, and then walks interior pageblocks. Each pageblock isolation takes `zone->lock`, rejects already isolated blocks, accepts unaccepted pages when necessary, checks only the relevant intersection for unmovable pages, calls `pageblock_isolate_and_move_free_pages()`, and increments `zone->nr_isolate_pageblock`. Boundary isolation additionally scans the surrounding MAX_ORDER-aligned area to detect a compound or free allocation that straddles the target boundary. Undo walks aligned blocks and unsets isolate state. Testing waits for deferred hugetlb frees, confirms all pageblocks are isolated, then under the zone lock scans for buddy pages or special offlining exemptions.

## State And Persistence Behavior
The file mutates allocator runtime state: pageblock migratetype bits, free lists, `zone->nr_isolate_pageblock`, buddy orders, and trace events. There is no disk persistence. Isolation is intentionally reversible and must be undone on partial failure.

## Dependencies And Integration Points
It depends on buddy allocator internals, pageblock flags, memory hotplug, CMA allocation modes, hugetlb migration support, movable page operations, unaccepted memory acceptance, page owner dump diagnostics, and `trace/events/page_isolation.h`. It is used by memory offlining and contiguous range allocation paths.

## Risks
- Page mobility classification is a conservative sample and can race with allocation, freeing, LRU isolation, or movable-ops setup.
- Overlapping isolation attempts are serialized only by pageblock state and can fail with `-EBUSY`.
- Free pages can remain on per-CPU page lists after isolation unless callers drain or disable PCP lists when stronger guarantees are needed.
- Large compound pages crossing pageblock boundaries are difficult; unsupported cases intentionally fail isolation.
- Forgetting to undo partially isolated ranges leaves allocator capacity stranded on isolate lists.

## Test Signals
- Memory offline and `alloc_contig_range()` over ranges with movable LRU pages, CMA pages, hugetlb pages, HWPoison pages, PageOffline pages, holes, and unaccepted pages.
- Boundary tests where MAX_ORDER pages cross the start or end PFN.
- Concurrent overlapping isolation attempts should return `-EBUSY` and restore prior state.
- Trace `test_pages_isolated` and inspect zone isolate counters/free lists after success and rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_isolation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_owner.c -->
# sources/distributed-fs/ceph-client/mm/page_owner.c

## Purpose
`page_owner.c` records allocation and free provenance for physical pages when booted with `page_owner=on`. It stores stack-depot handles and metadata in `page_ext`, exposes current allocation records and stack aggregates through debugfs, and supports diagnostics such as migration reason tracking and mixed pageblock analysis.

## Important APIs, Types, And Functions
- `struct page_owner` stores allocation order, migrate reason, GFP mask, alloc/free stack handles, timestamps, pid/tgid, and command names.
- `page_owner_ops` registers a `page_ext_operations` provider with early initialization.
- `save_stack()`, `inc_stack_record_count()`, and `dec_stack_record_count()` manage stack depot records and per-stack live page counts.
- `__set_page_owner()`, `__reset_page_owner()`, `__split_page_owner()`, `__folio_copy_owner()`, and `__folio_set_owner_migrate_reason()` are allocator/migration hooks.
- `pagetypeinfo_showmixedcount_print()` scans zones for pageblocks whose allocated pages have a migratetype different from the pageblock type.
- `read_page_owner()`, `print_page_owner()`, `__dump_page_owner()`, and stack seq-file helpers expose diagnostics.
- `pageowner_init()` creates `debugfs` files `page_owner` and `page_owner_stacks/*`.

## Control Flow
Early boot parses `page_owner=`, requests early stack depot, then `init_page_owner()` registers dummy/failure/early stack handles, annotates pages allocated before the machinery was ready, seeds stack-list entries, and enables the static key. Allocation hooks save a stack, write metadata to every base page in the allocation, set `PAGE_EXT_OWNER` and `PAGE_EXT_OWNER_ALLOCATED`, and increment the stack record by base page count. Free hooks save a free stack, clear allocated state, store free metadata, and decrement the allocation stack count except for early placeholders. Migration copy moves ownership metadata from old to new folio and preserves refcount balance by assigning the new folio's prior handle back to the old folio. Debugfs reads scan PFNs, skip free/tail/unowned pages, copy metadata out from under page_ext access, and format stack/memcg details to userspace.

## State And Persistence Behavior
All state is volatile kernel debug state. Per-page metadata lives in page extensions, stack traces live in stack depot, stack aggregate list nodes are allocated dynamically, and debugfs exposes snapshots. Static branch `page_owner_inited` gates overhead after boot. No data persists across reboot.

## Dependencies And Integration Points
The file integrates with page allocator hooks, `page_ext`, stack depot, stacktrace capture, debugfs, seq_file, memcg, migration reason names, pageblock migratetypes, zone iteration, and `pagetypeinfo`. It must avoid recursion because stack capture and list insertion can allocate memory.

## Risks
- Metadata is diagnostic and can race with allocation/free scans; debugfs may miss pages or show sampled state.
- Recursive allocation while recording ownership would deadlock or corrupt attribution without `current->in_page_owner`.
- Stack record refcounts are maintained manually because this code does not use `STACK_DEPOT_FLAG_GET`.
- Early allocated pages use a special handle and do not participate in normal decrement balancing.
- Large zone scans can be expensive and should remain debug-only.

## Test Signals
- Boot with and without `page_owner=on`, verify static-key gating and debugfs file creation.
- Allocate/free high-order pages, split pages, migrate folios, and compare `page_owner` output and stack aggregate counts.
- Exercise memcg-charged pages and offline memcgs in formatted output.
- Run `pagetypeinfo` mixed counts with movable/unmovable allocations.
- Use KASAN/KCSAN/lockdep to catch recursion, list publication, and page_ext lifetime issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_owner.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_poison.c -->
# sources/distributed-fs/ceph-client/mm/page_poison.c

## Purpose
`page_poison.c` implements debug page poisoning for the page allocator. When enabled, freed pages are filled with `PAGE_POISON`; allocation checks verify the pattern to detect use-after-free or memory corruption.

## Important APIs, Types, And Functions
- `_page_poisoning_enabled_early` and `_page_poisoning_enabled` expose boot-time and static-key runtime enable state.
- `early_page_poison_param()` parses `page_poison=`.
- `__kernel_poison_pages()` fills one or more pages with the poison byte.
- `__kernel_unpoison_pages()` checks one or more pages before reuse.
- `check_poison_mem()` locates the corrupt range, distinguishes single-bit flips, prints a hex dump, stack, and page details under rate limiting.
- `__kernel_map_pages()` is a no-op fallback when architecture debug-pagealloc unmapping is unavailable.

## Control Flow
On free, allocator hooks call `__kernel_poison_pages()`, which locally maps each page, disables KASAN for the current task, clears any memory tag before `memset()`, and unmaps. On allocation, `__kernel_unpoison_pages()` maps each page and calls `check_poison_mem()` over the full page. The checker returns silently for intact poison, otherwise rate limits error reporting and emits diagnostics.

## State And Persistence Behavior
State is the byte pattern stored in freed page memory plus enable flags/static key. There is no persistent storage. KASAN state is temporarily disabled only around the poison memory access so KASAN does not treat the deliberately poisoned free page as normal in-use memory.

## Dependencies And Integration Points
The file integrates with page allocator debug hooks, early kernel parameters, static keys exported to other MM code, highmem local mapping, KASAN tag reset/disable helpers, ratelimited printk, hex dumps, `dump_stack()`, and `dump_page()`.

## Risks
- It is a debug feature with significant memory bandwidth cost on free and allocation.
- Corruption reports are sampled by rate limiting; repeated corruptions can be suppressed.
- The check assumes every freed page was poisoned, so partial or skipped poisoning in caller paths would cause false positives.
- KASAN interaction must keep tag reset and disable/enable balanced.

## Test Signals
- Boot with `page_poison=on` and allocate/free pages across orders and highmem-capable paths.
- Deliberately corrupt a freed page in a test module and verify single-bit versus general corruption messages.
- Run with KASAN enabled to ensure poisoning does not trigger spurious sanitizer reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_poison.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_reporting.c -->
# sources/distributed-fs/ceph-client/mm/page_reporting.c

## Purpose
`page_reporting.c` implements free page reporting, a mechanism for a registered backend device to receive batches of free pages so it can treat them as unused, commonly for virtualized memory hinting. It scans buddy free lists, isolates unreported pages into scatterlists, calls the device callback, and marks pages reported when they return unchanged to the buddy allocator.

## Important APIs, Types, And Functions
- `page_reporting_order` is both a module parameter and exported symbol controlling the minimum order to report.
- `struct page_reporting_dev_info *pr_dev_info` is the single RCU-protected registered backend.
- `__page_reporting_notify()` schedules reporting after allocator notifications.
- `page_reporting_cycle()` scans one zone/order/migratetype free list and feeds full scatterlists to `prdev->report()`.
- `page_reporting_process_zone()` applies watermarks, iterates reportable free lists, and flushes leftovers.
- `page_reporting_process()` is the delayed work handler and state-machine driver.
- `page_reporting_register()` and `page_reporting_unregister()` are exported backend registration APIs.

## Control Flow
Registration chooses the report order from the module parameter, device preference, or `pageblock_order`, initializes work and state, requests an initial pass, publishes `pr_dev_info` with RCU, and enables the static key. Free-page notifications call `__page_reporting_notify()` only when enabled and the freed order is large enough. Requests coalesce through atomic states `IDLE`, `REQUESTED`, and `ACTIVE`, with delayed work capped to at most one pass every two seconds. Processing allocates a scatterlist, then for each zone verifies a low watermark plus reporting capacity. Each cycle locks the zone, skips already reported pages and isolate migratetypes, isolates free pages into the scatterlist, drops the lock to call `report()`, reacquires the lock, drains pages back to their migratetype lists, and sets `PageReported` only when the page remains a buddy page at the same order.

## State And Persistence Behavior
Runtime state includes the global report order, RCU backend pointer, backend delayed work and atomic state, buddy free lists, `PageReported` flags, scatterlist contents, and zone free-page ordering. There is no disk persistence. Unregister clears the RCU pointer, waits for readers, and cancels delayed work.

## Dependencies And Integration Points
The file depends on buddy allocator internals, page isolation primitives, pageblock migratetypes, scatterlists, delayed work, RCU, static keys, module parameters, and backend-defined `struct page_reporting_dev_info::report`. Its hot-path companion is `page_reporting_notify_free()` in `page_reporting.h`.

## Risks
- The backend callback runs outside the zone lock, so pages must be isolated correctly and always drained on success or error.
- Watermark checks must preserve allocation progress; too aggressive reporting can contend with allocators.
- `PageReported` is valid only when the page was not merged into a different order while being returned.
- Only one backend can register; competing drivers get `-EBUSY`.
- Failure to cancel work or synchronize RCU on unregister would leave stale backend calls.

## Test Signals
- Register/unregister a virtio-balloon or test backend repeatedly while freeing pages.
- Verify page reporting starts only for frees at or above `page_reporting_order`.
- Inject backend report errors and ensure pages are returned without `PageReported`.
- Stress buddy allocation/free during reporting and confirm no isolated-page leaks or watermark regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_reporting.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_reporting.h -->
# sources/distributed-fs/ceph-client/mm/page_reporting.h

## Purpose
`page_reporting.h` is the internal hot-path interface between the buddy allocator and the free page reporting implementation. It provides compile-time stubs when page reporting is disabled and a static-key-gated notification helper when enabled.

## Important APIs, Types, And Functions
- `DECLARE_STATIC_KEY_FALSE(page_reporting_enabled)` exposes the runtime branch key.
- `extern unsigned int page_reporting_order` shares the reporting threshold.
- `__page_reporting_notify()` is the slow-path worker request function.
- `page_reported(page)` checks both the static key and `PageReported`.
- `page_reporting_notify_free(order)` screens `__free_one_page()` notifications by enable state and minimum order.

## Control Flow
In enabled builds, free-page code calls `page_reporting_notify_free(order)`. The helper returns immediately if the static key is disabled or the free order is below `page_reporting_order`; otherwise it calls the out-of-line notifier that schedules delayed work. In disabled builds, `page_reported()` is a constant false macro and notification is an empty inline.

## State And Persistence Behavior
The header itself owns no storage. It reads the static key, report order, and page flag state managed by `page_reporting.c` and the allocator.

## Dependencies And Integration Points
It includes MM zone, pageblock, page-isolation, jump-label, slab, page-table, and scatterlist headers because it is consumed in allocator internals and shares types with `page_reporting.c`.

## Risks
- This helper is on the allocator free hot path, so static-key and order checks must stay minimal.
- Incorrect stubbing would either add overhead in disabled builds or hide reported-page state from allocator logic.
- `page_reporting_order` must be initialized before the static key is enabled.

## Test Signals
- Build with `CONFIG_PAGE_REPORTING=y` and `n`, verifying identical callers compile.
- Confirm low-order frees do not schedule work and high-order frees do after backend registration.
- Check branch-key state with page reporting enabled and after backend unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_reporting.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_table_check.c -->
# sources/distributed-fs/ceph-client/mm/page_table_check.c

## Purpose
`page_table_check.c` implements a debug hardening feature that tracks user-accessible page-table mappings per physical page. It catches illegal double writable anonymous mappings, anon/file mapping type conflicts, stale mappings on free, and userfaultfd write-protect flag inconsistencies.

## Important APIs, Types, And Functions
- `struct page_table_check` stores atomic anon and file map counters in page extensions.
- `page_table_check_ops` registers page extension storage and static-key initialization.
- `page_table_check_clear()` and `page_table_check_set()` decrement/increment per-page counters and BUG on invalid states.
- `__page_table_check_zero()` verifies counters are zero when pages are freed or allocated.
- `__page_table_check_pte_clear()`, `__page_table_check_pmd_clear()`, and `__page_table_check_pud_clear()` remove mapping counts.
- `__page_table_check_ptes_set()`, `__page_table_check_pmds_set()`, and `__page_table_check_puds_set()` clear old entries and add new mapping counts.
- `__page_table_check_pte_clear_range()` clears all PTEs under a PMD table.

## Control Flow
An early parameter or enforced Kconfig setting decides whether page extension storage is needed. Initialization disables the `page_table_check_disabled` static key when enabled. Page-table set hooks ignore `init_mm`, validate write-protect flag combinations, clear the previous entry or entries, and if the new entry is user-accessible, increment the anon or file counter for every base page covered. Clear hooks decrement the appropriate counter. Anonymous pages BUG if they acquire file mappings or more than one writable mapping; file pages BUG if they acquire anon mappings or counters underflow. Free/alloc zero checks BUG if any counter remains.

## State And Persistence Behavior
State is runtime-only per-page extension counters and the static branch. Counters are atomic because page-table operations can touch the same page concurrently. There is no persistence beyond the current boot, and failures intentionally crash via `BUG_ON()` to expose corruption.

## Dependencies And Integration Points
The file integrates with architecture/generic page-table update hooks, `page_ext`, swap/softleaf encodings for migration and device-private entries, userfaultfd write-protect helpers, `leafops`, and exported symbols used by low-level page-table code.

## Risks
- This is fatal-debug logic: false positives panic the system.
- Correctness depends on every relevant page-table modification calling the check hooks in the right order.
- Large PMD/PUD mappings must account for every base page, so incorrect `pgcnt` or stride calculations skew counters.
- UFFD-WP and softleaf cached-writable checks are subtle across migration/device-private entries.

## Test Signals
- Boot with `page_table_check=on` and run fork/COW, mprotect, THP, hugetlb-adjacent, migration, swap, and device-private memory tests.
- Intentionally create conflicting writable anonymous aliases in a debug test to verify the BUG path.
- Exercise page free paths with mapped pages to ensure `__page_table_check_zero()` detects leaks.
- Run userfaultfd write-protect tests involving present, swap, migration, and device-private entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_table_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_vma_mapped.c -->
# sources/distributed-fs/ceph-client/mm/page_vma_mapped.c

## Purpose
`page_vma_mapped.c` implements `page_vma_mapped_walk()`, the reverse-map helper that finds all page-table entries in one VMA mapping a target page or folio range. It supports normal PTEs, PMD-mapped THP, hugetlb, migration entries, and device-private/exclusive softleaf entries.

## Important APIs, Types, And Functions
- `page_vma_mapped_walk()` is the exported iterator over matching mappings.
- `page_vma_mapped_walk_done()` is called through `not_found()` or by callers to release held locks and mappings.
- `map_pte()` maps and optionally locks a PTE page, handling strict sync mode and PMD-change retry.
- `check_pte()` verifies that a PTE or softleaf entry overlaps the requested PFN range.
- `check_pmd()` verifies PMD-sized PFN range overlap.
- `page_mapped_in_vma()` is a memory-failure helper that returns the mapped address for a single page in a VMA.

## Control Flow
The walker first finishes any prior PMD-only mapping, then handles hugetlb VMAs through `hugetlb_walk()` and `huge_pte_lock()`. For normal VMAs it computes the range of addresses where the page could appear, descends PGD/P4D/PUD/PMD levels, skips absent upper entries by stepping to the next boundary, and treats PMD THP or PMD migration entries as direct matches if PFN ranges overlap. Non-present PMDs can also trigger PMD zap synchronization in `PVMW_SYNC` mode. Otherwise it maps a PTE page, validates the PTE against the requested PFN range, and iterates forward through PTEs until the VMA end or PMD boundary, returning each match with the page-table lock held.

## State And Persistence Behavior
The persistent state is in caller-provided `struct page_vma_mapped_walk`: current address, PFN range, VMA, flags, PTE/PMD pointers, PTL, and page-table-crossed flag. The file mutates no long-lived global state. It temporarily locks PTE, PMD, or hugepage page-table locks and maps PTE pages.

## Dependencies And Integration Points
It is tightly integrated with rmap, page migration, memory failure, hugetlb, THP splitting, HMM/device-private memory, softleaf swap encodings, MMU synchronization, and VMA address calculation helpers. Page idle, reclaim, migration, and memory-failure code rely on this walker to find exact mappings.

## Risks
- Page tables can change concurrently; PMD lockless reads and retry checks must be exact to avoid stale PTE access.
- Callers must release locks with `page_vma_mapped_walk_done()` when stopping early.
- Migration and device-private entries are non-present but still count as mappings for some rmap operations.
- THP range overlap must account for subpages without overflowing PFN arithmetic.
- Hugetlb locking differs from normal PTE/PMD locking and assumes callers hold the mapping semaphore documented by rmap users.

## Test Signals
- Rmap operations over PTE-mapped THP, PMD THP, split THP races, hugetlb, migration entries, and device-private/exclusive entries.
- Memory-failure `page_mapped_in_vma()` on mapped and unmapped pages.
- Lockdep/KCSAN while unmapping or splitting PMDs concurrently with rmap walks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_vma_mapped.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/pagewalk.c -->
# sources/distributed-fs/ceph-client/mm/pagewalk.c

## Purpose
`pagewalk.c` is the generic page-table walking engine. It walks user, VMA-scoped, mapping-scoped, kernel, debug, and hugetlb ranges through callback tables, optionally installs missing PTEs for internal MM users, and provides `folio_walk_start()` for safely resolving one VMA address to a folio while holding the relevant page-table lock.

## Important APIs, Types, And Functions
- `walk_page_range()`, `walk_page_range_mm_unsafe()`, `walk_page_range_vma()`, `walk_page_range_vma_unsafe()`, and `walk_page_vma()` walk user VMAs.
- `walk_kernel_page_table_range()`, `walk_kernel_page_table_range_lockless()`, and `walk_page_range_debug()` walk page tables not necessarily backed by VMAs.
- `walk_page_mapping()` walks all VMAs that map an address-space index range.
- `walk_pgd_range()`, `walk_p4d_range()`, `walk_pud_range()`, `walk_pmd_range()`, and `walk_pte_range()` implement recursive descent.
- `walk_hugetlb_range()` handles hugetlb VMAs.
- `check_ops_safe()` rejects public callback sets that try to install PTEs.
- `folio_walk_start()` resolves one address to a normal or optional zero folio and leaves `fw->ptl` held until `folio_walk_end()`.

## Control Flow
Range walkers validate arguments and locking expectations, build an `mm_walk`, and iterate VMAs or raw page-table ranges. At each level the walker handles holes through `pte_hole`, invokes the level callback if present, respects `walk->action` values such as `ACTION_AGAIN`, `ACTION_CONTINUE`, and `ACTION_SUBTREE`, splits huge PMD/PUD entries when lower-level callbacks require PTE descent, and allocates missing lower tables only for unsafe internal callers with `install_pte`. Hugetlb VMAs use a separate hstate-sized loop and `hugetlb_walk()`. Kernel/debug walkers set `no_vma`, avoid normal user PTE locking, and rely on caller-provided synchronization. `folio_walk_start()` performs a single-address descent, locks PUD/PMD/PTE huge or table entries, filters through `vm_normal_page*()` and optional zeropage handling, and returns the folio while keeping enough state in `struct folio_walk` to unlock later.

## State And Persistence Behavior
State is transient in `struct mm_walk`, callback private data, and `struct folio_walk`. The file can allocate page-table pages only through internal unsafe `install_pte` use. Otherwise it does not persist data; it takes and releases mmap/VMA/page-table locks and may split huge page-table entries as a side effect when callbacks need lower-level traversal.

## Dependencies And Integration Points
It depends on generic page-table macros, mmap/VMA locking, optional per-VMA locks, hugetlb locking, THP split helpers, `update_mmu_cache()`, kernel TLB/cache expectations, VMA interval trees, address-space reverse mapping, and exported `include/linux/pagewalk.h` callback contracts. It underpins pagemap/smaps, clear_refs, NUMA/mempolicy tools, kernel page-table dumpers, and internal MM code that walks mappings.

## Risks
- Public walkers must not allow arbitrary PTE installation; `check_ops_safe()` is a security and correctness boundary.
- Locking requirements differ for user, VMA, mapping, kernel, and debug walkers; misuse can race page-table teardown.
- Huge entry splitting has side effects and must be avoided when callbacks only want higher-level entries.
- Positive callback returns are caller-defined but internal VMA test positive values mean skip; confusing these can prematurely abort or mask errors.
- `folio_walk_start()` returns a folio without a reference and with a lock held; callers must not use it after `folio_walk_end()` unless they acquired a short-term ref.

## Test Signals
- Walk ranges with holes, folded levels, THP PMD/PUD entries, hugetlb VMAs, PFNMAP VMAs, and kernel page tables.
- Exercise callback combinations: upper-level only, PTE-only, hole callbacks, pre/post VMA, `test_walk`, and internal `install_pte`.
- Verify required mmap/per-VMA locks with lockdep for safe, unsafe, debug, and mapping walkers.
- Use `folio_walk_start()` on normal pages, huge leaves, zeropages, and invalid addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/pagewalk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/percpu-internal.h -->
# sources/distributed-fs/ceph-client/mm/percpu-internal.h

## Purpose
`percpu-internal.h` defines the private data structures and helper interfaces shared by the generic per-CPU allocator and its VM/KM backends. It describes chunk metadata, allocation bitmaps, optional object accounting extensions, global allocator state, and debug statistics helpers.

## Important APIs, Types, And Functions
- `struct pcpu_block_md` stores scan and contiguous-free hints for bitmap blocks.
- `struct pcpuobj_ext` stores optional memcg object cgroup and allocation profiling codetag state.
- `struct pcpu_chunk` is the central allocator chunk with lists, free bytes, bitmap maps, metadata blocks, base address, population counters, object extensions, and populated bitmap.
- `need_pcpuobj_ext()` decides whether object extension storage is needed.
- `pcpu_chunk_nr_blocks()`, `pcpu_nr_pages_to_map_bits()`, `pcpu_chunk_map_bits()`, and `pcpu_obj_full_size()` convert between pages, bitmap bits, and accounting sizes.
- `struct percpu_stats` and inline `pcpu_stats_*()` helpers track allocation and chunk statistics under `CONFIG_PERCPU_STATS`.

## Control Flow
The header is mostly declarative. Allocator code updates chunk maps and metadata under `pcpu_lock`; stats helpers assert or take that lock depending on whether they update allocation or chunk-wide counters. Object extension sizing adds per-object overhead for memcg when kmem accounting is active. In non-stats builds, all stats helpers compile to empty inline functions.

## State And Persistence Behavior
State is volatile allocator metadata: global chunk lists, slots, reserved/first chunks, bitmap maps, populated-page bits, per-chunk counters, optional object extension arrays, and stats. Nothing is persisted outside memory. `pcpu_chunk::immutable` prevents depopulation for pre-mapped chunks, while `isolated` tracks reclaim-list membership.

## Dependencies And Integration Points
The header depends on `linux/percpu.h`, memcg, optional memory allocation profiling, spinlocks, and constants such as `PCPU_BITMAP_BLOCK_SIZE` and `PCPU_MIN_ALLOC_SIZE`. It is consumed by core percpu allocation code and backend files `percpu-vm.c`, `percpu-km.c`, and `percpu-stats.c`.

## Risks
- Bitmap and metadata unit conversions must stay aligned with `PCPU_MIN_ALLOC_SIZE`, page size, and unit sizing.
- `pcpu_block_md` hint invariants are relied on for allocation scanning efficiency and correctness.
- Optional object extension sizing affects accounting and allocation size; miscalculations can undercharge or overrun metadata.
- Stats helpers assume correct locking and can become misleading if chunk paths bypass them.

## Test Signals
- Percpu allocation/free stress with varying sizes and alignments.
- Config matrix with `CONFIG_PERCPU_STATS`, memcg kmem enabled/disabled, and memory allocation profiling.
- Validate chunk metadata with debug checks after fragmentation and reclaim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/percpu-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/percpu-km.c -->
# sources/distributed-fs/ceph-client/mm/percpu-km.c

## Purpose
`percpu-km.c` is the contiguous-kernel-memory backend for dynamic per-CPU chunks, intended for NOMMU-style architectures that select `CONFIG_NEED_PER_CPU_KM`. It allocates each chunk as one contiguous `alloc_pages()` block instead of using vmalloc mappings.

## Important APIs, Types, And Functions
- `pcpu_create_chunk()` allocates allocator metadata plus a contiguous backing allocation, assigns page-to-chunk reverse mappings, and marks the whole chunk populated.
- `pcpu_destroy_chunk()` frees contiguous backing pages and chunk metadata.
- `pcpu_addr_to_page()` translates addresses with `virt_to_page()`.
- `pcpu_verify_alloc_info()` enforces the backend's single-group constraint and warns about rounded-up page waste.
- `pcpu_populate_chunk()`, `pcpu_depopulate_chunk()`, and `pcpu_post_unmap_tlb_flush()` are no-op backend hooks because the chunk is fully and permanently mapped.
- `pcpu_should_reclaim_chunk()` always returns false.

## Control Flow
Creation allocates a `pcpu_chunk`, allocates a power-of-two contiguous page block sized from the only percpu group, records the chunk pointer in every backing page, sets `data` and `base_addr`, marks all pages populated under `pcpu_lock`, updates stats, and emits a tracepoint. Destruction reverses those steps. Verification rejects allocation layouts with more than one group and warns if the power-of-two allocation is larger than the exact chunk size.

## State And Persistence Behavior
Chunks are fully populated for their lifetime. Runtime state is the contiguous page allocation, page-to-chunk reverse map, `pcpu_chunk` metadata, stats, and trace events. No depopulation or reclaim state is used.

## Dependencies And Integration Points
It depends on the generic percpu allocator helpers included by the build unit, page allocator `alloc_pages()`/`__free_pages()`, page address translation, `pcpu_group_sizes`, `pcpu_set_page_chunk()`, and tracepoints. It is mutually incompatible with paged first-chunk SMP configurations.

## Risks
- Requires all units in a single group and no NUMA-aware grouping.
- Power-of-two contiguous allocation can waste memory and fail under fragmentation.
- No reclaim support means empty populated pages remain allocated until chunk destruction.
- Misuse on an architecture expecting vmalloc-style sparse population would break address translation and TLB assumptions.

## Test Signals
- Build NOMMU or `CONFIG_NEED_PER_CPU_KM` configurations and verify first-chunk compatibility.
- Allocate/free enough dynamic percpu areas to create and destroy chunks.
- Validate warnings for non-power-of-two chunk page counts and rejection of multi-group allocation info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/percpu-km.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/percpu-stats.c -->
# sources/distributed-fs/ceph-client/mm/percpu-stats.c

## Purpose
`percpu-stats.c` exposes debugfs statistics for the per-CPU allocator. It reports boot allocation parameters, global allocation/chunk counters, and per-chunk fragmentation and allocation-size distributions.

## Important APIs, Types, And Functions
- `pcpu_stats` and `pcpu_stats_ai` are the global stats structures filled by allocator code.
- `find_max_nr_alloc()` determines a safe temporary buffer size for per-chunk allocation/free fragment accounting.
- `chunk_map_stats()` scans one chunk's allocation and boundary bitmaps and prints fragmentation and current allocation size metrics.
- `percpu_stats_show()` formats the full debugfs output while holding `pcpu_lock` during list and bitmap inspection.
- `init_percpu_stats_debugfs()` creates the `percpu_stats` debugfs file.

## Control Flow
The show path first samples the maximum number of allocations under `pcpu_lock`, allocates a vmalloc buffer large enough for twice that many allocation/free fragments plus one, then reacquires the lock and retries if the maximum grew. It prints allocation info and global stats, then visits the reserved chunk and every slot list. `chunk_map_stats()` finds the last allocated bit, walks from `start_offset` to that point, records positive allocation spans and negative free fragments, sorts them, computes sum/max fragmentation and min/median/max live allocation sizes, and prints chunk metadata hints.

## State And Persistence Behavior
The file only reads runtime allocator state and publishes it through debugfs. It owns the global stats variables but updates happen through inline helpers in `percpu-internal.h`. The temporary buffer is freed after each read. No data persists across reboot.

## Dependencies And Integration Points
It depends on debugfs, seq_file, sort, vmalloc, `pcpu_lock`, chunk lists and slots, reserved/first chunks, allocator bitmaps, and stat helpers. It is compiled only when percpu stats support is enabled.

## Risks
- Debugfs reads can be expensive because they hold `pcpu_lock` while scanning chunks and printing.
- Fragmentation metrics rely on `alloc_map` and `bound_map` semantics; if boundary map maintenance changes, reporting can become misleading.
- The initial buffer sizing must retry on concurrent allocations to avoid overflow.
- Sorting signed sizes intentionally places free fragments first; changing comparison semantics would break metrics.

## Test Signals
- Read `/sys/kernel/debug/percpu_stats` under allocation/free stress and verify no lockdep or buffer retry failures.
- Compare reported global counters with allocation/deallocation activity.
- Create fragmentation patterns and validate sum/max fragment and allocation size metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/percpu-stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/percpu-vm.c -->
# sources/distributed-fs/ceph-client/mm/percpu-vm.c

## Purpose
`percpu-vm.c` is the default vmalloc-backed backend for dynamic per-CPU chunks. It reserves per-CPU virtual areas, populates pages per CPU on demand, maps and unmaps them, performs cache/TLB maintenance, and decides when sparsely used chunks should be reclaimed.

## Important APIs, Types, And Functions
- `pcpu_chunk_page()` resolves a populated virtual address back to its page.
- `pcpu_get_pages()` provides a serialized temporary page pointer array indexed by `pcpu_page_idx()`.
- `pcpu_alloc_pages()` and `pcpu_free_pages()` allocate/free backing pages for all possible CPUs in a page range.
- `pcpu_map_pages()` and `pcpu_unmap_pages()` map/unmap per-CPU backing pages into chunk virtual addresses and maintain page-to-chunk reverse mappings.
- `pcpu_pre_unmap_flush()`, `pcpu_post_unmap_tlb_flush()`, and `pcpu_post_map_flush()` perform architecture cache/TLB maintenance over the whole chunk range.
- `pcpu_populate_chunk()` and `pcpu_depopulate_chunk()` are the backend population hooks.
- `pcpu_create_chunk()` and `pcpu_destroy_chunk()` reserve/free vmalloc areas and chunk metadata.
- `pcpu_should_reclaim_chunk()` decides whether a chunk should move to depopulation/sidelined lists.

## Control Flow
Population obtains the shared pages array under `pcpu_alloc_mutex`, allocates one page per CPU per requested page index using CPU-local NUMA nodes, maps each CPU's pages into the reserved vmalloc address range, sets page-to-chunk links, and flushes caches after mapping. On map failure it unmaps any partial CPU ranges, flushes TLBs, and frees allocated pages. Depopulation gets the same temporary array, flushes caches before unmap, records current mapped pages into the array, unmaps each CPU range, and frees the pages; callers perform any required post-unmap TLB flush unless vmalloc lazy flushing suffices. Chunk creation allocates metadata, reserves one vmalloc area per group with atom-size constraints, computes the base address from group 0, updates stats, and traces creation. Reclaim excludes first/reserved chunks and selects isolated chunks with empty pages or chunks with at least 25 percent empty populated pages when the global empty-populated-page pool exceeds the high watermark.

## State And Persistence Behavior
Runtime state includes reserved `vm_struct` areas, backing pages, page-to-chunk reverse mappings, populated bitmaps/counters in `pcpu_chunk`, the shared temporary pages array, stats, and trace events. There is no disk persistence. Pages can be depopulated and later repopulated, unlike the KM backend.

## Dependencies And Integration Points
The backend depends on vmalloc/vmap APIs, page allocator, CPU/node topology, `pcpu_alloc_mutex`, `pcpu_lock`, per-CPU group offsets/sizes, cache/TLB flush APIs, page-to-chunk reverse mapping, stats, and tracepoints. It supplies backend hooks consumed by the generic percpu allocator.

## Risks
- The temporary pages array is single global state and must only be used under `pcpu_alloc_mutex`.
- Partial allocation/map failures require exact rollback to avoid leaked pages or stale mappings.
- Cache and TLB flush ranges span low to high unit CPUs; wrong bounds can leave stale aliases.
- Reclaim heuristics must not depopulate first or reserved chunks and must keep global empty populated page accounting consistent.
- Address-to-page reverse lookup must not be used on immutable pre-mapped chunks.

## Test Signals
- Dynamic percpu allocation/free stress across CPUs and NUMA nodes with forced allocation failures.
- Reclaim tests that create empty populated pages and verify chunks move through to-depopulate and sidelined lists.
- Validate map/unmap with DEBUG_VM, KASAN, and lockdep for `pcpu_alloc_mutex` usage.
- Inspect tracepoints and `percpu_stats` before and after chunk creation, population, depopulation, and destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/percpu-vm.c -->
