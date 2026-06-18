# sources/distributed-fs/ceph-client/mm/compaction.c

Purpose: Implements Linux memory compaction: isolating movable pages and free pages, migrating data to coalesce higher-order free blocks, supporting direct allocation slow paths, CMA contiguous allocation, proactive background compaction, sysctl/sysfs triggers, and per-node `kcompactd`.

Important APIs, types, and functions: Public entry points include `try_to_compact_pages()`, `compaction_suitable()`, `compaction_zonelist_suitable()`, `isolate_freepages_range()`, `isolate_migratepages_range()`, `wakeup_kcompactd()`, `kcompactd_run()`, and `kcompactd_stop()`. Central internals are `compact_zone()`, `compact_zone_order()`, `isolate_migratepages_block()`, `isolate_freepages_block()`, `compaction_alloc()`, `compaction_free()`, defer/reset helpers, fragmentation scoring helpers, and sysctl handlers.

Control flow: Direct compaction checks GFP eligibility, iterates allocation zones, observes deferral, builds a `compact_control`, and runs `compact_zone()`. `compact_zone()` initializes scanners from zone cached PFNs, isolates migration pages from low PFNs, isolates destination free pages from high PFNs, migrates with `migrate_pages()`, drains LRU/pcp state where useful, and stops on success, contention, scanner meeting, or unsuitability. Background `kcompactd` sleeps on per-node wait queues, runs requested compaction for high-order allocation pressure, and periodically performs proactive compaction based on fragmentation score thresholds.

State and persistence: Per-zone compaction state includes cached migrate/free PFNs, defer counters, failed order, and skip hints in pageblocks. Per-node state includes `kcompactd` task, requested max order/highest zone, and proactive trigger. Sysctls configure proactiveness, external fragmentation threshold, compact-memory trigger, and unevictable isolation policy. State is runtime only.

Dependencies and integration: Relies on page migration, LRU isolation, buddy allocator free areas, pageblock migratetypes, NUMA node devices, cpusets, PSI, freezer/kthreads, tracepoints, and CMA paths. It is a core bridge between allocation failure handling and reclaim/migration machinery.

Risks: Race-prone lockless page checks are intentionally tolerated but require careful rechecks under locks. Incorrect skip-hint or cached-PFN updates can cause missed opportunities or excessive scanning. Migration under filesystem, unevictable, huge page, and RT constraints has many policy branches. Proactive compaction can burn CPU if thresholds are poorly tuned.

Test signals: Use high-order allocation stress, THP allocation behavior, CMA `alloc_contig_range()` paths, `/proc/sys/vm/compact_memory`, node sysfs `compact`, and vmstat/tracepoints such as `COMPACT*`, `KCOMPACTD_*`, and `trace/events/compaction`. Validate under NUMA, memory hotplug, sparsemem holes, hugetlb/THP, cpuset restrictions, and PREEMPT_RT sysctl warning behavior.
