# subset-b-006141 Research

Grouped source research for the Ceph-client copy of Linux MM page allocation, hierarchical page counters, page extension storage, and page fragment cache helpers. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_alloc.c -->
# sources/distributed-fs/ceph-client/mm/page_alloc.c

## Purpose

`sources/distributed-fs/ceph-client/mm/page_alloc.c` is the core zoned buddy page allocator. It manages physical free pages by NUMA node, zone, order, migratetype, and per-CPU page caches; implements the main `alloc_pages*()` and `free_pages*()` families; maintains watermarks, reserves, zonelists, and pageblock migration metadata; and provides support paths for compaction, CMA/contiguous allocation, memory hotplug, memory failure, page poisoning/debugging, unaccepted memory, and allocator tracing/profiling.

Although located under a distributed-fs/ceph-client source tree, the code is generic kernel MM infrastructure. Ceph, networking, filesystems, slab, page cache, block I/O, and BPF paths consume it through the normal page allocator API rather than Ceph-specific hooks. This copy also contains explicit `*_nolock` allocation/free entry points intended for opportunistic allocations or frees from contexts where normal locking/reclaim is unsafe.

## Important APIs, Types, and Functions

Important public or cross-subsystem entry points include `__alloc_frozen_pages_noprof()`, `__alloc_pages_noprof()`, `__folio_alloc_noprof()`, `alloc_pages_bulk_noprof()`, `get_free_pages_noprof()`, `get_zeroed_page_noprof()`, `__free_pages()`, `free_pages()`, `free_pages_nolock()`, `free_frozen_pages()`, `free_frozen_pages_nolock()`, `free_unref_folios()`, `split_page()`, `alloc_pages_exact_noprof()`, `alloc_pages_exact_nid_noprof()`, `free_pages_exact()`, `nr_free_buffer_pages()`, `build_all_zonelists()`, `setup_per_cpu_pageset()`, `zone_pcp_disable()`, `zone_pcp_enable()`, `zone_pcp_reset()`, `adjust_managed_page_count()`, `free_reserved_page()`, `page_alloc_init_cpuhp()`, `setup_per_zone_wmarks()`, `calculate_min_free_kbytes()`, `page_alloc_sysctl_init()`, and `has_managed_zone()`.

Core allocator internals are organized around `struct zone`, `struct free_area`, `struct per_cpu_pages`, `struct alloc_context`, pageblock bitmaps, and migratetypes such as `MIGRATE_UNMOVABLE`, `MIGRATE_MOVABLE`, `MIGRATE_RECLAIMABLE`, `MIGRATE_HIGHATOMIC`, `MIGRATE_CMA`, and `MIGRATE_ISOLATE`. The local `fpi_t` flags control free behavior: `FPI_SKIP_REPORT_NOTIFY`, `FPI_TO_TAIL`, and `FPI_TRYLOCK`. The file also defines and exports global state such as `node_states`, `movable_zone`, optional NUMA per-CPU node variables, `min_free_kbytes`, `defrag_mode`, `page_group_by_mobility_disabled`, and pageblock/migratetype name tables.

The hottest allocator helpers are `get_page_from_freelist()`, `rmqueue()`, `rmqueue_pcplist()`, `rmqueue_buddy()`, `__rmqueue()`, `__rmqueue_smallest()`, `__rmqueue_claim()`, `__rmqueue_steal()`, `rmqueue_bulk()`, `prep_new_page()`, `post_alloc_hook()`, `__free_frozen_pages()`, `__free_pages_prepare()`, `free_frozen_page_commit()`, `free_pcppages_bulk()`, `free_one_page()`, and `__free_one_page()`. Slow-path helpers include `__alloc_pages_slowpath()`, `__alloc_pages_direct_reclaim()`, `__alloc_pages_direct_compact()`, `should_reclaim_retry()`, `should_compact_retry()`, `__alloc_pages_may_oom()`, and `warn_alloc()`.

## Control Flow

The allocation fast path starts in `__alloc_frozen_pages_noprof()`. GFP flags are masked and contextualized, `prepare_alloc_pages()` derives the zonelist, highest zone, nodemask, migratetype, cpuset behavior, dirty-spread flag, and starting zoneref, then `get_page_from_freelist()` scans zones. The scan checks cpuset eligibility, dirty throttling, NUMA/locality fallback, watermarks, deferred-page growth, unaccepted memory, and node reclaim before calling `rmqueue()`. `rmqueue()` prefers per-CPU page lists for supported orders, falls back to the buddy allocator, and finally `prep_new_page()` unpoisons, initializes, tags, accounts, and marks compound or pfmemalloc state before returning.

The slow path, `__alloc_pages_slowpath()`, recalculates precise allocation flags, wakes kswapd, retries the freelist with reserve allowances where legal, optionally performs direct reclaim, performs direct compaction for high-order allocations, drains PCP/highatomic reserves after reclaim, retries around cpuset and zonelist updates, invokes OOM handling when appropriate, and honors `__GFP_NOFAIL` by looping only for direct-reclaim-capable requests. Failure reporting flows through `warn_alloc()` unless suppressed.

Freeing starts in `__free_pages()` or `free_pages()`, which drop references through `___free_pages()`. Once the last reference is gone, `__free_frozen_pages()` validates and prepares the page with `__free_pages_prepare()`, routes small eligible orders to the current CPU's PCP lists, and sends unsupported orders or isolated migratetypes directly to the buddy. PCP frees are batched by `free_frozen_page_commit()` and drained by `free_pcppages_bulk()`. Buddy insertion uses `free_one_page()` and `__free_one_page()`, which coalesces with free buddies, respects pageblock isolation/CMA/highatomic boundaries, updates free counters, optionally tails newly freed pages, and notifies free page reporting.

Pageblock fallback flow attempts to reduce fragmentation. `__rmqueue_smallest()` first allocates from the requested migratetype. If empty, `__rmqueue_claim()` may claim whole pageblocks from fallback migratetypes using `try_to_claim_block()`, and `__rmqueue_steal()` can steal a single fallback block when fragmentation avoidance is disabled or exhausted. High-order atomic allocations reserve pageblocks through `reserve_highatomic_pageblock()`; severe pressure releases them with `unreserve_highatomic_pageblock()`.

Boot and hotplug flow builds zonelists with `build_all_zonelists()`, initializes boot and real per-CPU pagesets, computes watermarks and lowmem reserves, registers CPU hotplug callbacks, and recalculates PCP batch/high limits when CPUs or zone sizes change. Contiguous allocation under `CONFIG_CONTIG_ALLOC` isolates pageblocks, migrates movable pages, extracts isolated free pages, optionally splits them into order-0 pages, and undoes isolation. Memory hotremove uses `__offline_isolated_pages()` to remove isolated buddy pages from accounting.

The `*_nolock` flow is intentionally narrower. `alloc_frozen_pages_nolock_noprof()` constructs non-reclaiming, non-warning, zeroing allocation flags with `ALLOC_TRYLOCK`, rejects contexts unsafe for PREEMPT_RT/NMI or deferred page initialization, only supports PCP-eligible orders, and has no slow path. `free_pages_nolock()` uses `FPI_TRYLOCK`; if locks cannot be obtained, pages can be queued on `zone->trylock_free_pages` and later processed by a normal free path.

## State and Persistence Behavior

All state is kernel-resident runtime state. Persistent storage is not written. State is represented by zone free lists, PCP lists, VM counters, watermarks, lowmem reserve arrays, highatomic reserve counters, pageblock migratetype/isolation bitmaps, node masks, zonelists, per-CPU statistics, page owner/allocation tags, memcg page charges, KASAN/KMSAN/page-table-check metadata, and optional unaccepted-memory lists.

Page state transitions are strict: allocation removes a page from PCP or buddy lists, clears buddy metadata, validates flags/refcounts/mapcounts, applies debug and sanitizer allocation hooks, and sets refcounts for normal allocations. Freeing tears down memcg/page-owner/page-table-check/tag state, poisons or initializes memory where configured, clears compound/tail metadata, returns pages to PCP or buddy lists, and updates zone/pageblock counters. Watermarks and reserve values are recalculated at boot, sysctl writes, memory hotplug, and CPU hotplug; they are not durable across reboot.

## Dependencies and Integration Points

This file integrates with nearly every MM subsystem: memblock and early boot, NUMA topology, cpusets and mempolicy, reclaim/kswapd/OOM, compaction/migration, CMA and page isolation, memory hotplug/offlining, vmstat, memcg, page owner, page table check, page reporting, debug pagealloc, KASAN/KMSAN, allocation profiling, folios, hugetlb replacement during contiguous allocation, page poisoning, memory failure, lockdep fs reclaim annotations, PSI and delay accounting.

External callers include slab, page cache, filesystems, networking, block drivers, BPF and tracing paths, page fragment users, and architecture-specific memory setup. Sysctl integration exposes `/proc/sys/vm` knobs such as `min_free_kbytes`, `watermark_boost_factor`, `watermark_scale_factor`, `defrag_mode`, `percpu_pagelist_high_fraction`, `lowmem_reserve_ratio`, and NUMA ratios when enabled.

## Risks and Edge Cases

Concurrency is the dominant risk. Zone locks, PCP locks, IRQ disabling, task CPU pinning, cpuset sequence checks, zonelist seqlocks, and trylock paths must remain aligned or pages can be lost, double-freed, accounted to the wrong zone, or returned from the wrong CPU cache. `FPI_TRYLOCK` and `ALLOC_TRYLOCK` are especially sensitive because they intentionally trade completeness for reentrancy and can defer work.

Fragmentation policy is subtle. Migratetype fallback, pageblock claiming, CMA isolation, highatomic reserves, movable-zone handling, and compaction capture all share the same free lists and counters. Incorrect pageblock transitions can corrupt `NR_FREE_PAGES`, `NR_FREE_CMA_PAGES`, `NR_FREE_PAGES_BLOCKS`, or highatomic reserve accounting. Watermark changes can also create premature reclaim or reserve depletion.

Debug and hardening hooks are ordering-sensitive. KASAN/KMSAN, page poisoning, page table checks, page owner, allocation tags, memcg uncharge, hardware-poison pages, and compound-tail cleanup all run before a page becomes visible to the allocator. Reordering can hide use-after-free bugs, trigger false positives, or expose inaccessible pages.

Memory hotplug, deferred struct page initialization, and unaccepted memory create pages whose metadata or physical acceptance state may not be complete. Paths that bypass locks or slow-path acceptance must reject these cases. Contiguous allocation and offlining are also exposed to races with compaction, hugetlb, page isolation, and PCP draining.

## Test Signals

Useful signals include kernel MM selftests, high-order allocation stress, memory hotplug/offline tests, CMA and `alloc_contig_range()` tests, compaction/reclaim pressure tests, cpuset and NUMA policy allocation tests, `GFP_ATOMIC` and highatomic reserve stress, memcg accounting tests, KASAN/KMSAN/page-owner/page-table-check boot tests, page poisoning/debug-pagealloc tests, and vmstat counter consistency checks. Runtime observability should monitor tracepoints such as page allocation/free, extfrag, reclaim/compact retry, and totalreserve/watermark setup, plus `/proc/zoneinfo`, `/proc/pagetypeinfo`, `/proc/vmstat`, sysctl changes, and allocation failure warnings. For the local nolock APIs, tests should exercise NMI/IRQ/raw-spinlock-like callers, PREEMPT_RT rejection paths, PCP-empty failure, trylock-free deferral, and memcg-charge failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_counter.c -->
# sources/distributed-fs/ceph-client/mm/page_counter.c

## Purpose

`sources/distributed-fs/ceph-client/mm/page_counter.c` implements lockless hierarchical page accounting and limiting. It is the generic counter primitive used by memory cgroups and related resource controllers to charge pages up a parent chain, enforce maximum page limits, track high-water marks and fail counts, parse user-provided memory limits, and compute effective `memory.min`/`memory.low` protection for reclaim decisions.

## Important APIs, Types, and Functions

The central type is `struct page_counter`, declared in `linux/page_counter.h`. This file operates on fields such as `usage`, `max`, `failcnt`, `watermark`, `local_watermark`, `min`, `low`, `min_usage`, `low_usage`, `children_min_usage`, `children_low_usage`, `emin`, `elow`, `parent`, `protection_support`, and `track_failcnt`.

Public functions are `page_counter_cancel()`, `page_counter_charge()`, `page_counter_try_charge()`, `page_counter_uncharge()`, `page_counter_set_max()`, `page_counter_set_min()`, `page_counter_set_low()`, `page_counter_memparse()`, and, when `CONFIG_MEMCG` or `CONFIG_CGROUP_DMEM` is enabled, `page_counter_calculate_protection()`. Internal helpers are `track_protection()`, `propagate_protected_usage()`, and `effective_protection()`.

## Control Flow

Charging without a limit check uses `page_counter_charge()`: it walks from the target counter to the root, atomically adds `nr_pages` to each `usage`, optionally propagates protected usage to parents, and updates local/global watermarks with intentionally racy but acceptable stores.

Limit-aware charging uses `page_counter_try_charge()`. It speculatively increments each counter in the hierarchy, then compares the new value to that counter's `max`. If a limit is exceeded, it subtracts the speculative charge from the failing counter, optionally increments `failcnt`, records the first failing counter through `fail`, and cancels charges already applied to descendants below the failing ancestor. The speculative add avoids a compare-and-swap loop and relies on full-barrier atomic operations to coordinate with concurrent `page_counter_set_max()`.

Uncharging uses `page_counter_uncharge()` to walk the same hierarchy and call `page_counter_cancel()` on each counter. `page_counter_cancel()` subtracts locally, warns and clamps on underflow, and updates protected usage propagation when enabled.

Limit updates use `page_counter_set_max()`. The caller must serialize updates on the same counter. The function reads usage, rejects a limit below current usage with `-EBUSY`, swaps in the new max, then rereads usage to detect races with concurrent try-charge. If a concurrent charge could have observed the old limit while pushing usage above the new one, it restores the old max and retries after `cond_resched()`.

Protection configuration uses `page_counter_set_min()` and `page_counter_set_low()` to store the configured protection and propagate current effective protected usage through ancestors. Reclaim-facing protection calculation uses `page_counter_calculate_protection()` during top-down tree walks. Immediate children of the root get their declared `min`/`low`; deeper descendants call `effective_protection()` to cap, proportionally distribute overcommitted protection, and optionally distribute unclaimed recursive protection by usage.

## State and Persistence Behavior

The state is in-memory resource accounting only. `usage`, limits, protected usage, child aggregates, fail counts, and watermarks live in `struct page_counter` instances owned by cgroups or similar controllers. There is no file-backed persistence here, although controller state may be exposed through cgroup files elsewhere.

Updates are lockless and mostly atomic. Some values, especially `watermark`, `local_watermark`, and `failcnt`, are explicitly allowed to be approximate under races because they are used for reporting rather than correctness. Protection aggregates are maintained in parent counters using atomic deltas whenever a child usage crosses its configured `min` or `low` boundary.

## Dependencies and Integration Points

Dependencies are small: `linux/page_counter.h`, atomics, scheduler rescheduling, string parsing, `memparse()`, page size definitions, and configuration gates for memcg or cgroup device memory. Integration is primarily with memory cgroup charging/un charging, cgroup v2 memory limit files, reclaim protection in `memory.min` and `memory.low`, and any controller that wants hierarchical page-count limits.

The parser `page_counter_memparse()` connects user-facing byte strings to page counts. It accepts a controller-provided max keyword and otherwise parses bytes with `memparse()`, converting to pages and clamping to `PAGE_COUNTER_MAX`.

## Risks and Edge Cases

The main correctness risk is charge/uncharge imbalance. Underflow in `page_counter_cancel()` indicates a serious caller bug and is clamped only after warning. Hierarchical rollback in `page_counter_try_charge()` must cancel exactly the counters already charged before the first failing ancestor.

Races are intentional but bounded. Watermarks and fail counts can be inaccurate, and protection propagation can observe non-atomic combinations of usage and settings. The effective protection math guards divisions by checking parent and child usage/protection relationships, but callers must still perform top-down traversal as documented; isolated calls can use stale parent effective values.

`page_counter_set_max()` depends on serialized limit writers and the ordering between atomic charge and max reads. Removing that serialization or weakening atomic ordering would allow limits below current usage or false failures. `page_counter_memparse()` truncates sub-page byte values to zero pages, which is expected but can surprise callers that do not validate minimums elsewhere.

## Test Signals

Useful validation includes memcg charge/uncharge stress under concurrency, cgroup memory.max updates racing with allocations, hierarchical limit failure tests that check `fail` points at the first limiting ancestor, underflow warning tests for negative accounting, watermark reset/read tests, `memory.min` and `memory.low` reclaim-protection scenarios with overcommitted and undercommitted siblings, recursive protection behavior, and parser tests for numeric values, suffixes, invalid trailing characters, and the controller's max keyword.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_counter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_ext.c -->
# sources/distributed-fs/ceph-client/mm/page_ext.c

## Purpose

`sources/distributed-fs/ceph-client/mm/page_ext.c` implements the generic `struct page_ext` facility: optional per-page extension storage allocated outside `struct page`. It lets debug and instrumentation features attach metadata to each physical page without enlarging the core `struct page` for every kernel build. The file decides whether extensions are needed at boot, lays out per-client extension areas, allocates flatmem or sparsemem backing arrays, handles memory hotplug, and exposes RCU-protected lookup/get/put helpers.

## Important APIs, Types, and Functions

The main public state is `page_ext_size`, the computed bytes per page extension entry, and `early_page_ext`, controlled by the `early_page_ext` boot parameter or forced by memory allocation profiling debug. Clients register through `struct page_ext_operations` objects in the local `page_ext_ops[]` array. Supported clients in this copy include page owner, page idle flags on 32-bit, memory allocation profiling tags, page table check, and IOMMU debug page allocation.

Important helpers include `invoke_need_callbacks()`, `invoke_init_callbacks()`, `get_entry()`, `page_ext_lookup()`, `page_ext_get()`, `page_ext_from_phys()`, and `page_ext_put()`. Flatmem builds use `page_ext_init_flatmem()`, `page_ext_init_flatmem_late()`, `pgdat_page_ext_init()`, `lookup_page_ext()`, and `alloc_node_page_ext()`. Sparsemem builds use `page_ext_init()`, `alloc_page_ext()`, `init_section_page_ext()`, `online_page_ext()`, `offline_page_ext()`, `page_ext_callback()`, `__invalidate_page_ext()`, and `__free_page_ext()`.

## Control Flow

Initialization begins by calling `invoke_need_callbacks()`. The first pass checks whether any client needs shared flags and reserves the base `struct page_ext` size when needed. The second pass assigns each active client an offset in the extension entry, adds its requested size, and returns whether any extension storage is required. If no client needs extensions, allocation is skipped entirely.

On flatmem, `page_ext_init_flatmem()` allocates one node-sized extension table per online node using memblock. It accounts the table as memmap boot pages and stores the base pointer in `NODE_DATA(nid)->node_page_ext`. `lookup_page_ext()` computes an index by subtracting a rounded-down node start PFN so buddy checks near node boundaries can safely address the extra alignment space. Late initialization invokes client init callbacks.

On sparsemem, `page_ext_init()` iterates memory nodes and valid sections, allocating one extension table per section through `alloc_pages_exact_nid()` or `vzalloc_node()`. `init_section_page_ext()` stores a biased pointer in `section->page_ext`, so `lookup_page_ext()` can compute an entry directly from PFN via `get_entry(section->page_ext, pfn)`. A memory notifier allocates extension storage on `MEM_GOING_ONLINE` and invalidates/frees it on `MEM_OFFLINE` or cancelled online.

Sparsemem offlining is deliberately three-phase. `offline_page_ext()` first marks each section's pointer invalid by setting a low-bit sentinel, then calls `synchronize_rcu()`, then frees the backing storage. This allows existing `page_ext_get()` users that started before invalidation to finish without use-after-free.

Runtime access uses RCU. `page_ext_lookup()` requires the caller already holds the RCU read lock. `page_ext_get()` takes the RCU read lock, performs lookup, and returns NULL while dropping RCU if no extension exists. Successful callers must later call `page_ext_put()`. `page_ext_from_phys()` validates a physical address with `pfn_to_online_page()` before delegating to `page_ext_get()`.

## State and Persistence Behavior

Page extension state is volatile kernel memory. It is allocated at boot or memory hotplug time and freed on sparsemem offlining. `total_usage` tracks allocated bytes for logging, while memmap page accounting is adjusted through `memmap_boot_pages_add()` or `memmap_pages_add()`.

Client offsets in `struct page_ext_operations` are assigned during initialization and remain the ABI for clients during the boot lifetime. Extension contents are owned by clients such as page owner, allocation tagging, page idle, page table check, and IOMMU debug code. This file only owns allocation, lifetime, and lookup.

## Dependencies and Integration Points

Dependencies include MM core headers, memblock, memory hotplug notifiers, vmalloc, kmemleak, RCU, sparsemem/flatmem topology, page owner, page idle, page table check, allocation profiling tags, and IOMMU debug page allocation. Boot parameter integration is through `early_param("early_page_ext", ...)`.

The allocator integration is important: page allocator sanity checks can call into `lookup_page_ext()` before extension arrays are allocated during early boot or hotplug, so lookup must tolerate NULL bases. Allocation profiling can require page extensions before the first page allocation to avoid missing early allocation tags.

## Risks and Edge Cases

The highest risk is lifetime during memory hotplug. Sparsemem section pointers can be valid, invalid-sentinel, or NULL; callers must hold RCU across use, and offlining must wait for a grace period before freeing. Incorrect pointer biasing or invalid-bit handling would produce wrong entries or free the wrong base address.

Allocation failure policy differs by phase. Boot-time extension allocation panics on failure once any client requires page extensions; hotplug returns notifier errors. Large systems can allocate significant memory because `page_ext_size` is multiplied by every present PFN or section, so client `need()` callbacks must be accurate.

Flatmem node-boundary padding is subtle. The table may include an extra `MAX_ORDER_NR_PAGES` span when node PFNs are not aligned, because buddy checks can inspect nearby PFNs. Removing that padding can break allocator boundary checks.

## Test Signals

Useful tests include booting with and without clients such as `CONFIG_PAGE_OWNER`, `CONFIG_PAGE_TABLE_CHECK`, `CONFIG_MEM_ALLOC_PROFILING`, and `CONFIG_PAGE_IDLE_FLAG`; booting with `early_page_ext`; memory hotplug online/offline cycles under concurrent page owner or page table check lookups; kmemleak noise checks around biased section pointers; sparsemem and flatmem build coverage; physical-address lookup tests for MMIO, holes, ZONE_DEVICE, offline memory, and normal RAM; and allocation failure injection for hotplug extension allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_ext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_frag_cache.c -->
# sources/distributed-fs/ceph-client/mm/page_frag_cache.c

## Purpose

`sources/distributed-fs/ceph-client/mm/page_frag_cache.c` implements the page fragment cache allocator. It provides a small framework for carving arbitrary-sized aligned fragments out of an order-0 or higher-order page while using the underlying page refcount to track outstanding fragments. The primary consumers are the network stack and network drivers, where fragments back `sk_buff` heads or skb fragment data.

## Important APIs, Types, and Functions

The central caller-owned type is `struct page_frag_cache`, declared in `linux/page_frag_cache.h`. This file maintains its `encoded_page`, `offset`, and `pagecnt_bias` fields. Public functions are `page_frag_cache_drain()`, `__page_frag_cache_drain()`, `__page_frag_alloc_align()`, and `page_frag_free()`.

Internal helpers are `encoded_page_create()`, `encoded_page_decode_order()`, `encoded_page_decode_virt()`, and `encoded_page_decode_page()`. `encoded_page_create()` packs the page virtual address, allocation order, and pfmemalloc bit into one unsigned long. The companion `encoded_page_decode_pfmemalloc()` is provided by the header.

## Control Flow

Allocation enters `__page_frag_alloc_align()`. If the cache has no encoded page, `__page_frag_cache_refill()` first tries to allocate `PAGE_FRAG_CACHE_MAX_ORDER` when page size is smaller than the maximum fragment-cache size, using flags that avoid direct reclaim and warn/retry behavior. If that fails, it falls back to an order-0 page. The encoded page records order and pfmemalloc state.

After refill, the allocator adds a large reference-count bias to the page instead of incrementing the refcount for every fragment. `nc->pagecnt_bias` starts at `PAGE_FRAG_CACHE_MAX_SIZE + 1`, `nc->offset` starts at zero, and each fragment allocation decrements the bias while advancing an aligned offset. If the requested fragment would exceed the page size, the code either returns NULL for requests larger than one base page when the cache is only order-0, or subtracts the remaining bias from the page. If the page refcount reaches zero and the cached page is not pfmemalloc, the same page is recycled by resetting its page count and offset; otherwise it is freed and the cache refills.

Draining uses `page_frag_cache_drain()` for a full cache and `__page_frag_cache_drain()` for a caller-supplied page/count pair. The drain subtracts the unused bias from the page refcount and frees the underlying allocation with `free_frozen_pages()` if the count reaches zero. Individual fragments are released with `page_frag_free()`, which finds the head page for the virtual address and frees the compound allocation when the last reference drops.

## State and Persistence Behavior

All state is transient and caller-owned. A `struct page_frag_cache` keeps one current page, a byte offset into that page, and a bias representing references pre-acquired by the cache but not yet handed out as fragments. Fragment lifetime is represented in the page's refcount. There is no persistence outside RAM.

Pfmemalloc state is preserved in the encoded page. When a pfmemalloc cached page is exhausted, it is returned to the page allocator instead of being recycled, preventing emergency-reserve pages from silently backing normal network buffers beyond their intended use.

## Dependencies and Integration Points

Dependencies include page allocation/free APIs from `mm/internal.h`, GFP flag definitions, NUMA memory node selection through `numa_mem_id()`, page refcount helpers, compound page order, virtual-to-page translation, and exported symbols for network and driver modules. Integration is primarily with skb allocation paths and drivers that cache page fragments for RX/TX buffers.

## Risks and Edge Cases

The encoded pointer relies on page alignment and bit masks. `BUILD_BUG_ON()` checks ensure the order and pfmemalloc bits fit below `PAGE_SIZE`; changing constants without preserving those invariants would corrupt decoded addresses. Refcount biasing is also delicate: failing to drain the cache leaks references and pages, while subtracting the wrong count can prematurely free a page still referenced by fragments.

Low-memory behavior intentionally falls back to order-0 pages. Large fragment requests can then fail even though the cache exists, and the code avoids freeing that cache page immediately to avoid worsening pressure. Callers must handle NULL returns. Pfmemalloc fragments require downstream networking code to respect emergency memory restrictions.

## Test Signals

Useful tests include network stack fragment allocation/free stress, fragment sizes around alignment and page-size boundaries, high-order refill failure forcing order-0 fallback, large-fragment NULL behavior, cache drain after partial use, last-fragment free of compound and order-0 pages, pfmemalloc page handling under memory pressure, KASAN/page-ref debug checks for use-after-free or refcount leaks, and module build coverage for exported APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page_frag_cache.c -->
