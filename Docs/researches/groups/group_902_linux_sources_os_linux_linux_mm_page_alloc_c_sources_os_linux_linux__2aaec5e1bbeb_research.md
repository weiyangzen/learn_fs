# Group Research: group_902_linux_sources_os_linux_linux_mm_page_alloc_c_sources_os_linux_linux__2aaec5e1bbeb

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/page_alloc.c -->
# File Research: sources/os/linux/linux/mm/page_alloc.c

Linux zoned buddy page allocator. This file owns the core physical page allocation and free paths, per-CPU page caches, zone watermarks, NUMA zonelists, allocation slowpath policy, contiguous page allocation, memory hotplug interactions, and allocator-facing debugging/accounting hooks.

Key responsibilities:
- Maintains global allocator state: node states, zone names, migratetype names, `gfp_allowed_mask`, lowmem reserve ratios, watermarks, defrag mode, movable zone metadata, and NUMA node counts.
- Encodes and updates pageblock state, including migratetype, isolation bits, compaction skip bits, and sparse/flatmem pageblock bitmaps.
- Implements buddy free-list manipulation: add, move, delete, merge, split, expand, account free pages, and choose tail/head placement.
- Prepares pages for free and allocation, integrating page owner, page table checks, KASAN/KMSAN, debug pagealloc, init-on-free/init-on-alloc, memory allocation profiling tags, memcg kmem charging, page poisoning, and architecture hooks.
- Manages per-CPU page lists (`pcp`) for low-order pages and THP-sized PCP orders where enabled, including locking, batching, high/low tuning, draining, decay, CPU hotplug, and cache-slice-aware high-order free batching.
- Allocates from zones through fast paths and slow paths, including cpuset restrictions, dirty throttling placement, watermark checks, node reclaim, deferred struct page initialization, unaccepted memory acceptance, per-migratetype fallback, CMA fallback, and highatomic reserves.
- Implements reclaim/compaction/OOM retry policy for `__alloc_pages_slowpath()`.
- Exports public allocator APIs: `__alloc_pages_noprof()`, `__folio_alloc_noprof()`, `get_free_pages_noprof()`, `get_zeroed_page_noprof()`, `__free_pages()`, `free_pages()`, `alloc_pages_exact_noprof()`, `free_pages_exact()`, `alloc_pages_bulk_noprof()`, contiguous allocation helpers, and no-lock allocation helpers.
- Builds zonelists for UMA and NUMA, including fallback node ordering, memoryless-node local-memory mapping, and hotplug-safe rebuild sequencing.
- Computes and updates zone watermarks, lowmem reserves, total reserve pages, `min_free_kbytes`, per-zone PCP batch/high limits, and related `vm` sysctls.
- Supports memory hotremove/offline by disabling PCPs, draining isolated pages, removing isolated buddy pages, and reporting managed page counts.
- Supports optional unaccepted memory by lazily tracking unaccepted MAX_ORDER pages and accepting them on allocation pressure.
- Supports memory failure by taking poisoned pages off the buddy allocator and putting them back safely.

Important behavior:
- Freeing normal pages flows through `__free_pages_prepare()`, then either PCP lists or direct buddy insertion via `free_one_page()` / `__free_one_page()`.
- `__free_one_page()` merges buddies upward while respecting pageblock migratetype boundaries, isolate/CMA/highatomic accounting, compaction capture, guard pages, page reporting, and shuffled/tail placement.
- Allocation first tries PCP lists for eligible orders; failing that, it locks the zone and uses the buddy allocator through `rmqueue_buddy()`.
- Migratetype fallback is staged: preferred freelist, CMA fallback for movable allocations, whole-pageblock claiming to reduce fragmentation, and finally single-page stealing if allowed.
- Watermark checks subtract unusable free pages such as highatomic reserves and CMA pages unavailable to the allocation.
- High-priority and nonblocking allocations can dip into reserves; OOM victims and `__GFP_MEMALLOC` get special reserve handling.
- Slowpath allocation wakes kswapd, retries adjusted allocation flags, performs direct reclaim, performs direct compaction, handles cpuset/zonelist races, may invoke OOM, and treats `__GFP_NOFAIL` as a retrying special case.
- `alloc_pages_bulk_noprof()` is order-0 only, avoids memcg accounting and page-owner recursion, and uses PCP batching when a local allowed zone satisfies low watermarks.
- Exact-size allocation overallocates to a power-of-two order, splits the allocation, and frees unused tail pages.
- Contiguous allocation isolates pageblocks, migrates movable pages, grabs isolated free pages, optionally splits them to order-0, and undoes isolation afterward.
- PCP disabling sets per-zone PCP high limits to zero and forces all CPUs to drain; this is used for hotplug and page isolation-sensitive paths.
- `alloc_pages_nolock_noprof()` is a best-effort reentrant allocator for arbitrary contexts. It only tries PCP/trylock paths, avoids reclaim and kswapd wakeups, and is expected to fail easily.

Dependencies:
- Core MM: zones, nodes, zonelists, GFP flags, folios, page flags, pageblocks, compaction, reclaim, OOM, migration, memory hotplug, page isolation, hugetlb, CMA, memcg, KSM/THP watermarks, vmstat, and page reporting.
- Debug/accounting systems: KASAN, KMSAN, page owner, page table check, debug pagealloc, kernel page poisoning, lockdep, PSI, delay accounting, fault injection, allocation profiling tags, and tracepoints.
- Concurrency primitives: zone spinlocks, PCP spinlocks with CPU pinning/migration disabling, seqlocks for zonelist updates, mutexes for PCP draining and PCP batch/high updates, CPU hotplug callbacks, RCU-adjacent hotplug assumptions, and IRQ-safe locking.
- Architecture and platform hooks: memory acceptance, highmem clearing, arch page allocation/free hooks, NUMA distance, cacheinfo, and optional memoryless-node support.

Notable risks:
- Correctness depends on tight invariants around page refcounts, PageBuddy, page private order, pageblock migratetypes, zone accounting, PCP counts, and free-area lists.
- PCP locking is deliberately subtle: a PCP lookup must be paired with CPU pinning, and trylock failure can redirect pages to direct buddy free paths or per-zone lockless lists.
- Migratetype fallback and pageblock claiming trade locality, fragmentation, CMA usability, highatomic reserves, and future compaction success.
- Watermark and reserve checks are performance-sensitive and intentionally approximate in places; changes can alter allocation latency or premature reclaim behavior.
- Slowpath retry policy coordinates reclaim, compaction, OOM, cpuset races, zonelist rebuilds, and nofail semantics; small logic changes can cause livelocks or premature failures.
- Memory hotplug/offline and contiguous allocation depend on pageblock isolation and full PCP draining to prevent isolated pages from being reallocated.
- KASAN/page poisoning/init ordering is intentional: poisoning/unpoisoning and memory initialization must remain synchronized to avoid false reports or stale tags.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/page_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/page_counter.c -->
# File Research: sources/os/linux/linux/mm/page_counter.c

Lockless hierarchical page accounting and limiting support, primarily for memory cgroups and device-memory cgroup counters.

Key responsibilities:
- Provides hierarchical charge, try-charge, uncharge, and local cancel operations for `struct page_counter`.
- Tracks current usage, max limit, failure count, global/local watermarks, and optional protection usage.
- Parses user memory limits into page counts with support for a caller-provided “max” token.
- Computes effective `memory.min` and `memory.low` protection for cgroup reclaim decisions when memcg or cgroup device memory support is enabled.

Important behavior:
- `page_counter_charge()` walks from a counter to its ancestors and atomically adds pages without checking limits.
- `page_counter_try_charge()` speculatively charges each level, checks `max`, rolls back already-charged ancestors on failure, and reports the first counter that exceeded its limit.
- `page_counter_cancel()` subtracts local usage and clamps underflow to zero with a warning.
- Watermarks are intentionally racy statistics; local and global watermarks are updated with `READ_ONCE`/`WRITE_ONCE`.
- Protection propagation stores each child’s protected usage as `min(usage, min)` and `min(usage, low)`, then updates parent aggregate protected usage deltas.
- `page_counter_set_max()` uses an exchange-and-retry sequence so concurrent chargers cannot hide usage above a newly lowered limit.
- `page_counter_set_min()` and `page_counter_set_low()` update settings and refresh protection propagation up the hierarchy.
- Effective protection calculation distributes parent protection according to usage, overcommit, undercommit, and optional recursive protection semantics.

Dependencies:
- Uses `struct page_counter` from `linux/page_counter.h`, atomic long operations, `memparse()`, scheduler rescheduling, and page-size conversion.
- Protection calculation is compiled for `CONFIG_MEMCG` or `CONFIG_CGROUP_DMEM` and is tied to cgroup reclaim semantics.

Notable risks:
- Several statistics are intentionally approximate under races; callers must not treat watermarks or fail counts as strict synchronization.
- `page_counter_try_charge()` speculatively overcharges before rollback, so transient usage can exceed limits.
- Effective protection is stateful and intended for top-down tree iteration; isolated calls can observe stale parent effective values.
- Limit updates require caller-side serialization for the same counter.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/page_counter.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/page_ext.c -->
# File Research: sources/os/linux/linux/mm/page_ext.c

Infrastructure for optional per-page extension storage outside `struct page`. It allows debug/accounting features to attach per-page metadata without permanently enlarging the base page structure.

Key responsibilities:
- Collects `page_ext_operations` users such as page owner, page idle flags on 32-bit, allocation profiling tags, page table checks, and IOMMU debug page allocation.
- Determines at boot whether page extension storage is needed through each client’s `need()` callback.
- Computes `page_ext_size`, assigns client offsets, and invokes optional init callbacks once storage exists.
- Allocates and looks up page extension arrays for flatmem and sparsemem configurations.
- Handles sparsemem memory hotplug by allocating page extension storage on memory online and invalidating/freeing it on offline.
- Exposes lookup APIs: `page_ext_lookup()`, `page_ext_get()`, `page_ext_from_phys()`, and `page_ext_put()`.

Important behavior:
- `early_page_ext` can be forced by the `early_page_ext` boot parameter and defaults on for allocation-profiling debug builds.
- If any client requires shared flags, the base `struct page_ext` is included before client-specific offset storage.
- Flatmem allocates one table per node through memblock during boot; misaligned node ranges get extra space so buddy checks around node boundaries are safe.
- Sparsemem stores a section-relative base pointer in `mem_section->page_ext`, computed as `base - page_ext_size * section_start_pfn`.
- Sparsemem offline invalidates section `page_ext` pointers first, waits for an RCU grace period, then frees the underlying storage to avoid use-after-free.
- `page_ext_get()` enters an RCU read-side critical section and returns a pointer that remains valid until `page_ext_put()`.
- `page_ext_from_phys()` rejects MMIO, zone-device, holes, and offline memory by requiring `pfn_to_online_page()`.

Dependencies:
- Uses memory model APIs, memblock, sparsemem sections, memory hotplug notifiers, RCU, vmalloc, exact-page allocation, kmemleak, page owner, page idle, page table check, allocation profiling, and IOMMU debug page allocation.
- Lookup callers must hold RCU directly or use `page_ext_get()`/`page_ext_put()`.

Notable risks:
- Sparsemem stores tagged invalid pointers using `PAGE_EXT_INVALID`; users must route through the helpers instead of dereferencing section state directly.
- Page allocator sanity checks can run before page_ext arrays exist during boot or hotplug, so lookup can legitimately return NULL.
- Hotplug teardown correctness depends on invalidation before `synchronize_rcu()` and only freeing after readers finish.
- `page_ext_get()` callers must not sleep until `page_ext_put()` releases the RCU read lock.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/page_ext.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/page_frag_cache.c -->
# File Research: sources/os/linux/linux/mm/page_frag_cache.c

Page fragment cache allocator for networking and drivers. It provides fast allocation of arbitrary-sized fragments from cached order-0 or higher-order pages, with fragment lifetime tracked through the backing page reference count.

Key responsibilities:
- Encodes a cached page’s virtual address, allocation order, and pfmemalloc state into `page_frag_cache->encoded_page`.
- Refills a page fragment cache from the page allocator, preferring `PAGE_FRAG_CACHE_MAX_ORDER` when supported and falling back to order-0.
- Allocates aligned fragments from the cached page while maintaining `offset` and `pagecnt_bias`.
- Drains page fragment caches and frees backing pages when references drop to zero.
- Exports fragment allocation and free helpers for external users.

Important behavior:
- Higher-order refill avoids direct reclaim, adds `__GFP_COMP`, suppresses warnings, avoids retrying, and avoids emergency reserves; order-0 fallback uses the original GFP mask.
- `__page_frag_alloc_align()` initializes a new page by adding a large reference bias and then decrements that bias for each fragment allocated.
- If the current cached page lacks enough space, the allocator either refills or, if the page is solely owned by the cache, resets its refcount and offset for reuse.
- Requests larger than a page fail when the cache only has an order-0 page, and the existing cache page is retained to avoid worsening memory pressure.
- Pfmemalloc cached pages are freed instead of recycled when exhausted, then the cache refills.
- `page_frag_free()` converts an arbitrary fragment address to the head page and frees the compound allocation when the last fragment reference is dropped.

Dependencies:
- Uses low-level page allocation APIs, page reference counters, compound order, pfmemalloc markers, virtual-to-page conversion, and constants from `linux/page_frag_cache.h`.
- Intended users include networking paths that need fast skb head/frags backing memory.

Notable risks:
- Correctness relies on the encoded-page bit layout matching page alignment and `PAGE_FRAG_CACHE_*` masks.
- The refcount bias scheme must remain compatible with `get_page_unless_zero()` users, so the code deliberately avoids raw `atomic_set()` on freshly refilled pages.
- Callers must free fragments with the matching page-frag free path so backing page references drain correctly.
- Pfmemalloc fragments require care by consumers because such pages come from emergency memory reserves.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/page_frag_cache.c -->