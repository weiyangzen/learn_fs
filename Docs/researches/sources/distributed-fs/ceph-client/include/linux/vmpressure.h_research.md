# sources/distributed-fs/ceph-client/include/linux/vmpressure.h

## Purpose
`vmpressure.h` declares the memory-pressure notification interface used primarily by memory cgroups. It tracks scanned and reclaimed pages and exposes eventfd notifications so userspace can react to reclaim pressure levels.

## Important APIs, Types, and Functions
`struct vmpressure` stores direct and tree-level scanned/reclaimed counters, `sr_lock` for counter synchronization, an event list guarded by `events_lock`, and a `work_struct` for deferred event processing. Under `CONFIG_MEMCG`, declared APIs include `vmpressure()`, `vmpressure_prio()`, `vmpressure_init()`, `vmpressure_cleanup()`, `memcg_to_vmpressure()`, `vmpressure_to_memcg()`, `vmpressure_register_event()`, and `vmpressure_unregister_event()`. Without memcg support, reporting functions compile to no-ops.

## Control Flow
Reclaim paths report scanned and reclaimed counts with a gfp mask, target memcg, and tree flag. The implementation aggregates counters under `sr_lock`, schedules work, evaluates pressure, and signals registered eventfds. Priority-based reporting maps reclaim priority to pressure events. Registration attaches eventfd-backed listeners to a memcg's pressure object, and cleanup removes them.

## State and Persistence
State is volatile per-memcg accounting and event subscription state. Counters are reset/rolled by the implementation as events are emitted. Event registrations live until unregistered or the memcg/vmpressure object is cleaned up. There is no durable persistence.

## Dependencies and Integration Points
The header depends on mutexes, lists, workqueues, GFP flags, cgroups, and eventfd. It integrates with memcg reclaim, userspace cgroup event notification, pressure-level policy, and memory-management workqueue execution.

## Risks
Counter updates must keep scanned and reclaimed values synchronized. Event traversal and modification require `events_lock`. Workqueue callbacks must not outlive the memcg/vmpressure object. Build-time no-op behavior means callers must not rely on notifications when `CONFIG_MEMCG` is off.

## Test Signals
Test signals include memcg reclaim stress, eventfd notification delivery at expected thresholds, registration/unregistration races, memcg teardown with pending work, tree versus local pressure reporting, and builds with `CONFIG_MEMCG` disabled.
