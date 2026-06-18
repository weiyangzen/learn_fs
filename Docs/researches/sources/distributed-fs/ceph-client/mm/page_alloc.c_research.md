# Research: sources/distributed-fs/ceph-client/mm/page_alloc.c

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
