# sources/distributed-fs/ceph-client/mm/vmstat.c

## Purpose
`mm/vmstat.c` is the kernel VM statistics aggregation and reporting hub. It keeps zone, node, NUMA, and VM event counters cheap on hot allocation/reclaim paths by batching updates in per-CPU differentials, folding them periodically into global atomics, and exposing snapshots through `/proc`, sysctl, and debugfs. It also owns fragmentation diagnostics used by compaction tooling and initializes the shared `mm_percpu_wq` used by VM per-CPU maintenance.

## Important APIs, types, and functions
The exported counter APIs are `__mod_zone_page_state()`, `mod_zone_page_state()`, `inc_zone_page_state()`, `dec_zone_page_state()`, `__mod_node_page_state()`, `mod_node_page_state()`, `inc_node_page_state()`, and `dec_node_page_state()`. They update `vm_zone_stat[]`, `vm_node_stat[]`, and per-zone/per-node per-CPU `s8` diff buckets. `all_vm_events()` and `vm_events_fold_cpu()` aggregate `vm_event_states`. NUMA helpers include `fold_vm_numa_events()`, `sum_zone_node_page_state()`, and `sum_zone_numa_event_state()`. Fragmentation helpers include `extfrag_for_order()` and `fragmentation_index()`. Initialization runs through `init_mm_internals()`, `vmstat_late_init()`, CPU hotplug callbacks, and optional `extfrag_debug_init()`.

## Control flow
Fast-path accounting adds deltas to per-CPU diff arrays until a threshold is crossed, then flushes the diff into zone/node atomics. SMP builds prefer `this_cpu_try_cmpxchg()` when available; otherwise updates are serialized with interrupt disabling and the `__mod_*` helpers. `refresh_cpu_vm_stats()` drains current-CPU differentials, optionally decays/drains per-CPU page lists, and folds global deltas. Per-CPU delayed work (`vmstat_update`) reschedules only while counters keep changing; the shepherd worker scans quiet CPUs and queues flushes where needed, skipping isolated CPUs. CPU hotplug disables work before down, folds dead CPU diffs, refreshes thresholds, and tracks `N_CPU` node state.

Reporting flows create snapshot arrays in `vmstat_start()`, populate zone, NUMA, node, dirty-limit, memmap, and event counters, then emit one `vmstat_text[]` line per counter. `/proc/buddyinfo`, `/proc/pagetypeinfo`, and `/proc/zoneinfo` iterate online nodes/zones via seq operations and print allocator state while taking zone locks where needed. Debugfs `extfrag` files compute unusable/free fragmentation indexes per order.

## State and persistence
State is in memory only: global atomic counters, per-zone/per-node atomics, per-CPU differentials, `vm_event_states`, NUMA event arrays, `nr_memmap_*` atomics, delayed work items, and sysctl values. No persistent storage is written. Userspace-visible state is synthesized through procfs/sysctl/debugfs on demand. NUMA stats can be disabled through sysctl, which also clears NUMA counters and toggles `vm_numa_stat_key`.

## Dependencies and integration points
This file integrates with the page allocator, reclaim, compaction, writeback, memcg-facing stat naming, CPU hotplug, NOHZ isolation, procfs, sysctl, and debugfs. The `NR_ZSPAGES` name is present when zsmalloc is enabled, and zswap event counters (`ZSWPIN`, `ZSWPOUT`, `ZSWPWB`) are exported through `/proc/vmstat` when configured.

## Risks and invariants
The main invariant is that per-CPU drift remains bounded by thresholds so global snapshots are acceptably approximate without breaching allocator watermarks. Byte-valued node stats are stored as pages in global counters and must be page-aligned. Locking must preserve hot-path performance and PREEMPT_RT correctness; the comments around `preempt_disable_nested()`, cmpxchg loops, and IRQ-safe zone walking are important. Diagnostic proc files intentionally trade precision for bounded lock hold time, for example capping free-list walks.

## Test signals
Useful checks are boot/init without CPU hotplug warnings, stable `/proc/vmstat` counter names/counts, `echo` or `cat` of `/proc/sys/vm/stat_refresh` with no unexpected negative-counter warnings, CPU online/offline cycles, NUMA stat toggling, and reading `/proc/buddyinfo`, `/proc/pagetypeinfo`, `/proc/zoneinfo`, plus debugfs `extfrag/*` when `CONFIG_COMPACTION` and `CONFIG_DEBUG_FS` are enabled.
