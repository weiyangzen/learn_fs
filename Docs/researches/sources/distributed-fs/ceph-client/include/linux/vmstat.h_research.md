# sources/distributed-fs/ceph-client/include/linux/vmstat.h

## Purpose
`vmstat.h` defines the kernel memory-statistics API: VM event counters, zone/node/NUMA page state accounting, folio/page stat helpers, reclaim statistics, lruvec stat integration, and text-name accessors. It is a central memory-management accounting header.

## Important APIs, Types, and Functions
`struct reclaim_stat` summarizes reclaim scan/writeback/congestion/activation outcomes. `enum vm_stat_item` adds global dirty-threshold and memmap counters. `struct vm_event_state` holds per-CPU VM event counters when `CONFIG_VM_EVENT_COUNTERS` is enabled. Event APIs include `count_vm_event()`, `__count_vm_event()`, `count_vm_events()`, `all_vm_events()`, and `vm_events_fold_cpu()`, with conditional wrappers for NUMA, TLB flush, and VMA lock counters. Page-state APIs include global arrays `vm_zone_stat`, `vm_node_stat`, `vm_numa_event`, accessors `global_zone_page_state()`, `global_node_page_state()`, `zone_page_state()`, snapshot helpers, NUMA sum/fold helpers, `__mod_*`, `mod_*`, `inc_*`, `dec_*`, threshold refresh, drain, and `vmstat_flush_workqueue()`. Folio helpers update zone/node/lruvec counts by `folio_nr_pages()`. Name helpers index `vmstat_text[]`.

## Control Flow
Fast paths increment per-CPU event counters using raw or this-CPU operations. Zone/node stats either use per-CPU differentials on SMP or direct atomic updates on UP. Readers obtain global atomic values and clamp negative transient values to zero under SMP. Folding drains CPU-local differentials into global counters during CPU hotplug, idle, or explicit flush. Folio helpers translate a folio to its zone, node, or lruvec and apply page-count deltas.

## State and Persistence
Statistics are in-memory counters. Per-CPU event counters and per-zone/node atomics persist for the boot lifetime and are exposed through proc/debug interfaces elsewhere. They are deliberately approximate in hot paths; snapshots may race and are not exact synchronization points.

## Dependencies and Integration Points
The header depends on percpu, atomics, static keys, `mmzone`, `vm_event_item`, page/folio helpers, NUMA configuration, memcg/lruvec definitions, and CPU iteration. It integrates with the allocator, reclaim, compaction, migration, writeback pressure accounting, `/proc/vmstat`, memcg statistics, and CPU hotplug.

## Risks
VM stats are allowed to be racy; callers must not make critical correctness decisions from approximate event counters. Byte-accounted node items require page-size alignment at the global level. Missing folds can skew visible stats. Enum/text-table ordering must remain exact. Conditional no-op wrappers can hide missing accounting in builds without the relevant feature.

## Test Signals
Signals include allocation/reclaim/migration/compaction tests that change expected counters, `/proc/vmstat` sanity, CPU hotplug folding, lockless stat reads under stress, memcg lruvec accounting tests, NUMA balancing counters, and builds with SMP/UP and feature combinations.
