# sources/distributed-fs/ceph-client/mm/vmpressure.c

## Purpose

`vmpressure.c` implements memory-pressure accounting and notification for memory cgroups. It converts reclaim activity into pressure levels by comparing scanned pages against reclaimed pages, smooths those signals over a page-scan window, raises critical pressure directly from deep vmscan priority, notifies userspace listeners through eventfd registrations, and informs in-kernel consumers such as socket memory control when reclaim efficiency for a non-root cgroup becomes poor.

The file primarily serves the reclaim path and memcg event infrastructure. In legacy tree-reporting mode it accumulates subtree reclaim efficiency and sends `low`, `medium`, or `critical` notifications up the memcg hierarchy according to listener mode. In default cgroup-v2-oriented local mode it records reclaim efficiency for the target memcg and, for medium/critical pressure, asserts socket pressure so networking allocations can react.

## Important APIs, Types, and Functions

Constants and threshold policy:

- `vmpressure_win` is the accounting window, `SWAP_CLUSTER_MAX * 16` pages. Reclaim events below this window are accumulated before ratio-based notification.
- `vmpressure_level_med` is 60 percent pressure.
- `vmpressure_level_critical` is 95 percent pressure.
- `vmpressure_level_critical_prio` is derived from `ilog2(100 / 10)` and treats sufficiently deep scan priority as critical even if a normal window was not reached.

Enums and strings:

- `enum vmpressure_levels` defines `VMPRESSURE_LOW`, `VMPRESSURE_MEDIUM`, and `VMPRESSURE_CRITICAL`.
- `enum vmpressure_modes` defines default no-passthrough behavior, hierarchy passthrough, and local-only behavior.
- `vmpressure_str_levels[]` and `vmpressure_str_modes[]` parse memcg event arguments such as `medium,hierarchy` or `critical,local`.

Core helpers:

- `work_to_vmpressure()` maps delayed work back to its owning `struct vmpressure`.
- `vmpressure_parent()` walks from a `struct vmpressure` to its parent memcg's vmpressure object.
- `vmpressure_level()` maps a numeric pressure percentage to a level.
- `vmpressure_calc_level()` computes pressure from scanned and reclaimed pages. It explicitly handles `reclaimed >= scanned` as no pressure because slab reclaim can increase reclaimed without matching scanned LRU pages.
- `vmpressure_event()` iterates registered listeners, applies threshold and mode filters, signals matching eventfds, and returns whether anything was signalled.
- `vmpressure_work_fn()` drains accumulated tree counters, computes the pressure level, and propagates notification up the memcg hierarchy.

Public/memcg-facing APIs:

- `vmpressure()` is called from reclaim with GFP mask, target memcg, tree/local mode, scanned pages, and reclaimed pages. It filters irrelevant reclaim, accumulates counters, schedules work for tree mode, or updates socket pressure for local mode.
- `vmpressure_prio()` is called when vmscan priority changes. When the priority indicates deep scanning, it synthesizes a critical tree-mode event by calling `vmpressure()` with a full window and zero reclaimed pages.
- `vmpressure_register_event()` parses eventfd arguments, allocates a `struct vmpressure_event`, and links it into the memcg's vmpressure event list.
- `vmpressure_unregister_event()` removes the event registration for a given eventfd and frees the event object.
- `vmpressure_init()` initializes locks, list head, and work item for an embedded `struct vmpressure`.
- `vmpressure_cleanup()` flushes pending work before the containing memcg object is torn down.

Internal type:

- `struct vmpressure_event` stores the eventfd context, minimum pressure level, notification mode, and list node.

## Control Flow and Lifecycle

The normal ratio-based path begins in the reclaim code calling `vmpressure(gfp, memcg, tree, scanned, reclaimed)`. The function exits early when the memory controller is disabled. For cgroup-v1 legacy configurations, it ignores non-tree accounting because in-kernel local users are intended for the default hierarchy. It then filters GFP masks to pressures that userland can plausibly help with: highmem, movable, IO, FS, or the GFP_KERNEL-style indirect reclaim path. Calls with zero scanned pages are ignored because lack of scanable LRUs is not enough by itself to report critical pressure; priority-based reporting handles that case.

In tree mode, `vmpressure()` locks `sr_lock`, adds scanned/reclaimed pages to `tree_scanned` and `tree_reclaimed`, and returns until the accumulated scanned count reaches `vmpressure_win`. Once the window is reached, it schedules `vmpr->work`. `vmpressure_work_fn()` later locks the same counter state, copies and clears the tree counters, computes the pressure level, then starts with the original memcg and repeatedly calls `vmpressure_event()` while walking parents with `vmpressure_parent()`. Two booleans control propagation semantics: `ancestor` suppresses `local` listeners on ancestors, and `signalled` suppresses default no-passthrough listeners above a cgroup where a listener was already signalled. Hierarchy-mode listeners can still receive ancestor notifications.

In local mode, `vmpressure()` first ignores root-level efficiency because no current user consumes it. It accumulates `scanned` and `reclaimed` in local counters until the same window is reached, then clears them synchronously and computes the pressure level in the reclaim caller context. If the level is above low, it calls `mem_cgroup_set_socket_pressure(memcg)`, keeping socket pressure asserted with external hysteresis for networking allocation behavior. Local mode does not signal eventfd listeners in this file.

The priority-based path is `vmpressure_prio()`. It ignores priorities above the critical threshold. At or below the threshold it calls `vmpressure()` in tree mode with `scanned = vmpressure_win` and `reclaimed = 0`, which produces a critical pressure ratio after normal filtering and scheduling. This catches cases where very little remains to scan, so normal window accounting might not produce a timely critical event.

Event lifecycle is controlled by memcg event registration. `vmpressure_register_event()` duplicates the argument string up to `MAX_VMPRESSURE_ARGS_LEN`, parses the required level and optional mode with `strsep()` and `match_string()`, allocates a zeroed event object, fills its eventfd/level/mode, and appends it under `events_lock`. `vmpressure_unregister_event()` locks the same list, finds the matching eventfd, unlinks the node, frees it, and stops after the first match. `vmpressure_cleanup()` flushes work so eventfd infrastructure is not accessed after teardown.

## State and Persistence Behavior

All state is volatile kernel memory embedded in each memcg's `struct vmpressure`; nothing is persisted to disk. The state model includes:

- `sr_lock`, a spinlock protecting scanned/reclaimed counters.
- `tree_scanned` and `tree_reclaimed`, accumulated for userspace tree notifications and consumed by the workqueue path.
- `scanned` and `reclaimed`, accumulated for local in-kernel pressure accounting and consumed synchronously.
- `events_lock`, a mutex protecting the event registration list.
- `events`, the list of `struct vmpressure_event` objects associated with eventfds.
- `work`, the scheduled work item that drains tree counters and signals eventfds.

Counter clearing is intentionally lossy-windowed. Multiple reclaim contexts can schedule work before a previous work item clears counters; `vmpressure_work_fn()` handles this by checking for zero `tree_scanned` and returning. Tree notifications are asynchronous, while local socket pressure updates happen directly in `vmpressure()`.

## Dependencies and Integration Points

This file depends on memcg and cgroup helpers: `mem_cgroup_disabled()`, `cgroup_subsys_on_dfl()`, `memory_cgrp_subsys`, `memcg_to_vmpressure()`, `vmpressure_to_memcg()`, `parent_mem_cgroup()`, `mem_cgroup_is_root()`, and `mem_cgroup_set_socket_pressure()`. It integrates with reclaim/vmscan through calls to `vmpressure()` and `vmpressure_prio()` and with userspace cgroup event notification through `eventfd_signal()`.

The GFP mask filter ties pressure reporting to reclaim contexts where userspace action can help or where kswapd-style indirect reclaim should be counted. `SWAP_CLUSTER_MAX` couples the accounting window to the reclaim scanner's natural batch size. Workqueues decouple userspace event notification from direct reclaim. List and lock primitives provide registration safety around eventfd lists.

## Risks and Edge Cases

The pressure calculation is intentionally heuristic. A fixed `vmpressure_win` can delay notifications on small systems or increase false positives on larger/atypical systems; the source comment notes that machine-size-dependent thresholds would be better. The medium and critical percentages are empirical, so workloads with unusual reclaim behavior may see misleading levels.

`reclaimed >= scanned` is treated as zero pressure to account for slab reclaim paths that add reclaimed pages without corresponding scanned LRU pages. This avoids false pressure but can hide mixed reclaim situations where slab reclaim dominates while LRU reclaim is still struggling.

GFP filtering can suppress real low-zone pressure that userspace cannot solve, such as DMA-zone pressure. That is deliberate, but it means vmpressure is not a full OOM predictor. Calls with `scanned == 0` are also ignored unless priority reporting reaches the critical path.

Event propagation mode is subtle. Default listeners do not receive passthrough once a descendant has been signalled; hierarchy listeners can receive ancestor notifications; local listeners are skipped for ancestor events. Changes to `vmpressure_event()` can easily alter userspace ABI expectations for cgroup event behavior.

Registration parsing accepts a bounded copy of the argument string. Invalid level or mode returns `-EINVAL`; allocation failures return `-ENOMEM`. Eventfd lifetime itself is external: unregister frees only the vmpressure wrapper, not the eventfd context. Cleanup must flush work before memcg/eventfd teardown to avoid use-after-free.

Local mode updates socket pressure only for non-root memcgs and only above low pressure. If future in-kernel consumers rely on root or low-level efficiency, the current early returns and threshold check would need revisiting.

## Test Signals and Validation Hooks

Useful signals include:

- Memcg reclaim tests that register `memory.pressure_level` eventfds for `low`, `medium`, and `critical`, then trigger reclaim workloads and verify level/mode-specific event delivery.
- Hierarchy tests covering default, `hierarchy`, and `local` modes across parent/child cgroups to confirm passthrough suppression and ancestor filtering.
- Reclaim instrumentation that checks `vmpressure()` ignores disabled memcg, legacy non-tree local mode, irrelevant GFP masks, root local mode, and zero-scanned events.
- Synthetic scanned/reclaimed ratios around 60 percent and 95 percent to validate `vmpressure_calc_level()` thresholds, including the `reclaimed >= scanned` case.
- Vmscan-priority tests or trace-driven checks confirming `vmpressure_prio()` emits critical tree pressure only at or below `vmpressure_level_critical_prio`.
- Concurrency tests where multiple reclaim contexts update counters while work is pending, validating that zero-scanned work exits cleanly and counters are not used after `vmpressure_cleanup()`.
- Socket-pressure observation for cgroup-v2 local reclaim where medium/critical pressure should call `mem_cgroup_set_socket_pressure()`.
