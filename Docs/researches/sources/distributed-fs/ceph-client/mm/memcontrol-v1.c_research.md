# sources/distributed-fs/ceph-client/mm/memcontrol-v1.c

## Purpose

This file contains cgroup v1-specific memory controller behavior that is split away from the shared memcg implementation. It implements legacy soft-limit reclaim, cgroup-v1 threshold and eventfd notification plumbing, legacy memory+swap accounting transitions, OOM notification and userspace OOM wait behavior, v1 cgroup file handlers, stats formatting, kmem/tcp accounting compatibility, and per-memcg event-counter allocation.

## Important APIs, types, and functions

Soft-limit state is represented by `struct mem_cgroup_tree_per_node`, `struct mem_cgroup_tree`, and the global `soft_limit_tree`, which keeps per-node rbtrees of `struct mem_cgroup_per_node` ordered by `usage_in_excess`. The key functions are `memcg1_update_tree()`, `memcg1_remove_from_trees()`, `memcg1_soft_limit_reclaim()`, `mem_cgroup_largest_soft_limit_node()`, and `mem_cgroup_soft_reclaim()`.

Legacy event plumbing uses `struct mem_cgroup_eventfd_list` for OOM notifiers and `struct mem_cgroup_event` for `cgroup.event_control` registrations. Registration helpers include `__mem_cgroup_usage_register_event()`, `mem_cgroup_usage_register_event()`, `memsw_cgroup_usage_register_event()`, `__mem_cgroup_usage_unregister_event()`, `mem_cgroup_oom_register_event()`, `mem_cgroup_oom_unregister_event()`, `memcg_write_event_control()`, `memcg_event_wake()`, and `memcg_event_remove()`.

Charge and swap hooks include `memcg1_commit_charge()`, `memcg1_swapout()`, `memcg1_swapin()`, and `memcg1_uncharge_batch()`. Per-cpu event state is `struct memcg1_events_percpu`, driven by `memcg1_charge_statistics()`, `memcg1_event_ratelimit()`, and `memcg1_check_events()`.

OOM handling uses `memcg_oom_lock`, `memcg_oom_waitq`, `struct oom_wait_info`, `mem_cgroup_oom_trylock()`, `mem_cgroup_oom_unlock()`, `mem_cgroup_mark_under_oom()`, `mem_cgroup_unmark_under_oom()`, `memcg_oom_wake_function()`, `memcg1_oom_recover()`, `mem_cgroup_oom_synchronize()`, `memcg1_oom_prepare()`, and `memcg1_oom_finish()`.

The v1 control-file layer is expressed by `MEMFILE_PRIVATE()`, `MEMFILE_TYPE()`, `MEMFILE_ATTR()`, `enum res_type`, the resource attribute enum, `mem_cgroup_read_u64()`, `mem_cgroup_write()`, `mem_cgroup_reset()`, `mem_cgroup_resize_max()`, `mem_cgroup_force_empty()`, `mem_cgroup_hierarchy_*()`, `mem_cgroup_swappiness_*()`, `mem_cgroup_oom_control_*()`, and the exported cftype arrays `mem_cgroup_legacy_files[]` and `memsw_files[]`. Stats helpers include `memcg_numa_stat_show()`, `reparent_memcg1_state_local()`, `reparent_memcg1_lruvec_state_local()`, and `memcg1_stat_format()`. Kmem/socket compatibility hooks are `memcg1_account_kmem()`, `memcg1_charge_skmem()`, `memcg1_alloc_events()`, `memcg1_free_events()`, and `memcg1_init()`.

## Control flow

Soft-limit tracking begins when charge or uncharge paths call `memcg1_commit_charge()` or `memcg1_uncharge_batch()`. Those update v1 PGPGIN/PGPGOUT and per-cpu page-event counters with interrupts disabled, then `memcg1_check_events()` periodically fires threshold checks and soft-limit tree updates. `memcg1_update_tree()` walks the charged memcg and ancestors, computes `soft_limit_excess()`, removes any existing rbnode, and reinserts it by excess if needed. On PREEMPT_RT, the event/soft-limit path is disabled; with multigenerational LRU enabled, excess cgroups call `lru_gen_soft_reclaim()` instead of maintaining the rbtrees.

Reclaim enters through `memcg1_soft_limit_reclaim()`, which ignores high-order requests and the LRU-gen case. It takes the per-node largest-excess rbnode, pins the memcg css, reclaims descendants with `mem_cgroup_soft_reclaim()`, reinserts the node if it remains over its soft limit, and advances to other nodes if no pages were reclaimed. The reclaim loops are bounded by `MEM_CGROUP_MAX_RECLAIM_LOOPS` and `MEM_CGROUP_MAX_SOFT_LIMIT_RECLAIM_LOOPS` because soft limits are best-effort.

Threshold notifications are registered through the legacy `cgroup.event_control` write path. `memcg_write_event_control()` parses eventfd/control-fd/args, validates that the control file belongs to the same memory cgroup, maps known file names to register/unregister callbacks, registers the event, polls the eventfd to attach a wake handler, and stores the event on `memcg->event_list`. Usage thresholds are stored as sorted RCU-protected arrays with a spare buffer for unregister; threshold checks signal eventfds when usage crosses entries in either direction. OOM and pressure events are separate callback types, with OOM events stored on `memcg->oom_notify`.

When an eventfd is closed, `memcg_event_wake()` sees `EPOLLHUP`, removes the event from the memcg list under `event_list_lock`, and schedules `memcg_event_remove()` to sleepably unregister callbacks, signal final notification, drop eventfd and css references, and free memory. `memcg1_css_offline()` removes remaining registered events asynchronously during cgroup offline.

Swapout for cgroup v1 transfers a page's memory+swap charge to a swap entry only when legacy memsw accounting is active. `memcg1_swapout()` finds an online ancestor if the original memcg was offlined, records the swap cgroup id, clears the folio's memcg data, adjusts memory and memsw page counters, updates stats, and drops the object cgroup reference. `memcg1_swapin()` removes duplicate swap-entry accounting after a charged page enters swapcache.

OOM control supports both kernel OOM killing and legacy userspace OOM handling. `memcg1_oom_prepare()` either records `current->memcg_in_oom` for user-fault completion when `oom_kill_disable` is set, or marks the hierarchy under OOM, tries to lock the subtree, and notifies eventfd listeners. `mem_cgroup_oom_synchronize()` runs at page-fault exit, waits on `memcg_oom_waitq` for userspace recovery, and cleans up task/css state. `memcg1_oom_recover()` wakes waiters when limits are raised or OOM killing is re-enabled.

Control-file writes parse byte values into pages and dispatch by encoded resource type and attribute. Limit writes call `mem_cgroup_resize_max()` for memory or memsw, which preserves the invariant `memory.max <= memsw.max`, drains stocks once, and attempts reclaim before failing busy. Kmem limit writes are accepted as deprecated no-ops, while TCP kmem limits update `tcpmem` and enable the socket-accounting static key in the right order. Soft-limit writes update `memcg->soft_limit` except on PREEMPT_RT. Reset writes clear watermarks or failcnts. Stats output flushes rstat-style memcg stats, prints v1-compatible local and hierarchical counters, LRU bytes, limits, events, and optional debug VM costs.

## State and persistence behavior

The file maintains per-node soft-limit rbtrees allocated at `subsys_initcall()` time, per-memcg event lists, per-memcg OOM notifier lists, per-memcg threshold arrays protected by mutex plus RCU, global `memcg_oom_lock`, a global OOM waitqueue, per-cpu v1 event counters allocated per memcg, and cgroup file state encoded in `cftype.private`.

All state is runtime kernel memory. It persists for the lifetime of the memory cgroup or boot, not across reboot. Threshold arrays and event registrations persist until eventfd close or css offline; unregister uses RCU grace periods before old arrays can be reused or freed. Soft-limit rbnode membership persists until usage falls below soft limit, the memcg is removed from trees, or reclaim temporarily removes/reinserts it. OOM `under_oom` and `oom_lock` markers are transient but hierarchy-wide. TCP memcg activation persists once enabled for a memcg because static-key activation is not undone here.

## Dependencies and integration points

The file depends on the shared memcg implementation and interfaces from `linux/memcontrol.h`, swap and swap cgroup code, pagewalk/backing-dev infrastructure, eventfd and poll APIs, sorting, file permission checks, `seq_buf`, `internal.h`, `swap.h`, and `memcontrol-v1.h`. It integrates with the cgroup core through `struct cftype`, kernfs open files, `css_tryget_online_from_dir()`, cgroup v1 file names, and cgroup offline callbacks.

It also integrates with reclaim (`mem_cgroup_shrink_node()`, `try_to_free_mem_cgroup_pages()`), LRU generation (`lru_gen_enabled()`, `lru_gen_soft_reclaim()`), page counters, memcg stats and events, swap slot ownership (`swap_cgroup_record()`, `mem_cgroup_uncharge_swap()`), object cgroups, vmpressure, socket memory accounting (`memcg_sockets_enabled_key`), global swappiness, and cgroup-v1 memory+swap file registration through `memsw_files[]`.

## Risks

This is compatibility-heavy code with several deprecated interfaces. Event-control parsing is intentionally tied to cgroup-v1 filenames and regular cgroupfs dentries; mistakes can leave css/eventfd references leaked or callbacks attached to the wrong memcg. Threshold arrays rely on a primary/spare RCU protocol; allocation, unregister, and current-threshold bookkeeping must stay synchronized with usage checks. OOM handling is sensitive to hierarchy locking and waitqueue wake matching, and bugs can strand page-faulting tasks when userspace OOM handling is enabled.

Soft-limit reclaim is best-effort and race-tolerant, so stale rbnode ordering is acceptable but tree corruption is not. PREEMPT_RT disables event-control and soft-limit behavior, so tests must account for `-EOPNOTSUPP`. Memory/memsw limit updates must preserve their invariant or accounting can become inconsistent. Swapout handles offlined memcgs by charging an online ancestor, and bugs there can leak memsw counts or record unusable private IDs. Socket memory activation requires static-key ordering before `tcpmem_active`; reordering can silently lose socket accounting.

## Test signals

Useful tests include cgroup-v1 memory controller boot and mount tests, reads/writes for `memory.limit_in_bytes`, `memory.memsw.limit_in_bytes`, `memory.soft_limit_in_bytes`, `memory.failcnt`, `memory.max_usage_in_bytes`, `memory.force_empty`, `memory.swappiness`, `memory.oom_control`, kmem/tcp compatibility files, and `memory.stat`. Functional coverage should trigger threshold eventfds on usage and memsw crossings, close eventfds and remove cgroups to verify async cleanup, exercise OOM notification and userspace OOM wait/recover paths, and run soft-limit reclaim under memory pressure on non-RT kernels without LRU-gen taking over.

Additional signals are correct `memory.numa_stat` output on NUMA builds, no leaked eventfd/css references after cgroup deletion, stable page counters through swapout/swapin and offlined memcgs, successful limit resize with stock draining and reclaim, and warnings only once for deprecated interfaces. Regression tests should include cgroup v2/default hierarchy builds where these v1 paths are either inactive or guarded by `do_memsw_account()` and cgroup mode checks.
