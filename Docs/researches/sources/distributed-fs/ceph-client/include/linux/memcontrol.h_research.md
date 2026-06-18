<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memcontrol.h -->
# sources/distributed-fs/ceph-client/include/linux/memcontrol.h

## Purpose
This header defines the memory cgroup public and internal interfaces for charging pages and kernel objects, tracking per-cgroup VM statistics/events, lruvec selection, writeback attribution, socket memory pressure, shrinker metadata, zswap accounting, and cgroup v1 compatibility.

## Important APIs, types, and functions
It defines `enum memcg_stat_item`, `enum memcg_memory_event`, `struct mem_cgroup_reclaim_cookie`, and under `CONFIG_MEMCG` the main `struct mem_cgroup`, `struct mem_cgroup_per_node`, `struct obj_cgroup`, threshold structures, reclaim iterators, and writeback foreign-dirty tracking. Important APIs include `mem_cgroup_charge`, `mem_cgroup_uncharge`, swapin and hugetlb charging, folio memcg/object-cgroup accessors, `mem_cgroup_lruvec`, lruvec lock helpers, cgroup ID/private-ID lookup, reclaim iteration, protection helpers, stats and event counters, OOM printing/group selection, high-limit handling, socket charge helpers, kmem/object charge helpers, zswap charge helpers, and cgroup v1 OOM/swap hooks. Large sections provide no-op or node-level fallbacks when memory cgroups are disabled.

## Control flow
Allocation paths charge folios or kernel objects to the active/task memcg, update page counters and folio `memcg_data`, and later uncharge on free or migration. Reclaim obtains the correct `lruvec` for a memcg/node pair, applies min/low protection unless reclaim targets the same memcg, and records events/statistics. Writeback compares dirtying memcg with writeback ownership to track foreign dirtying. Socket and kmem paths use static keys to avoid overhead when disabled. Disabled builds collapse charges/events to success/no-op and use node lruvecs directly.

## State and persistence
Memcg state persists with cgroup lifetime: page counters, memory/swap/zswap limits and events, VM stats, per-node lruvecs, shrinker info, object-cgroup references, ID mappings, writeback domains, deferred split queues, socket pressure, v1 thresholds, OOM flags, and eventfd lists. Folio `memcg_data` carries runtime binding and flags. Reparenting handles objects that outlive a cgroup.

## Dependencies and integration points
It depends on cgroups, page counters, VM events/stats, folios/pages, LRU/reclaim, writeback, eventfd, vmpressure, shrinkers, zswap, sockets, slab object extensions, BPF static keys, and cgroup v1/v2 policy files. It is a central integration point between mm, filesystem writeback, networking, slab, swap, and userspace cgroup controls.

## Risks and test signals
Risks include folio/object binding instability without the documented locks or RCU, refcount leaks during objcg reparenting, inaccurate low/min protection under parallel reclaim, stale lruvec locks after reparenting, disabled-config behavior hiding accounting bugs, writeback attribution races, high-limit throttling latency, and NMI-safe stat configuration differences. Test page and kmem charge/uncharge, folio migration/split, memcg deletion with live objects, reclaim protection, lruvec relock batching, OOM group reporting, events/stat flushing, socket pressure on 32-bit and 64-bit, cgroup writeback foreign dirtying, zswap limits, and CONFIG_MEMCG=n builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memcontrol.h -->
