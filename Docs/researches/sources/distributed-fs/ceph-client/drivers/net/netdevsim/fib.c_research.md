# sources/distributed-fs/ceph-client/drivers/net/netdevsim/fib.c

Purpose: implements netdevsim's simulated FIB, rule, and nexthop offload engine. It lets tests exercise devlink resource accounting, route offload flags, nexthop notifier behavior, resilient nexthop bucket updates, and route/nexthop failure injection without real hardware.

Important APIs/types/functions: `struct nsim_fib_data` owns notifier blocks, route and nexthop rhashtables, workqueues, debugfs controls, and devlink resource callbacks. `nsim_fib_create()`/`nsim_fib_destroy()` manage lifetime. `nsim_fib_event_nb()` receives FIB/rule events, `nsim_fib_event_work()` applies queued route changes, and `nsim_nexthop_event_nb()` handles nexthop changes synchronously under `nh_lock`. `nsim_fib_get_val()` exposes current/max resource values to the rest of netdevsim.

Control flow: create initializes debugfs, rhashtables, locks, work items, resource maxima from devlink, nexthop notifier, FIB notifier, and occupancy getters. Route replace/delete notifications account resources in notifier context, hold referenced route objects, enqueue events, and later update rhashtables and route hardware flags from workqueue context. IPv4 tracks `fib_info`; IPv6 groups sibling `fib6_info` entries into one simulated route and can append/delete subsets. Dump inconsistency flushes queued work and clears programmed state. Destroy unregisters callbacks, cancels work, drains rhashtables, and removes debugfs.

State and persistence: all state is in memory: atomic counters for IPv4/IPv6 FIB and rule occupancy, a nexthop occupancy counter, route/nexthop hash tables, a queued event list, and debugfs booleans. Route and nexthop objects hold kernel references until destroyed. No disk persistence exists.

Dependencies and integration: integrates with `fib_notifier`, `nexthop` notifiers, `devlink` resources, `debugfs`, IPv4/IPv6 route hardware flag helpers, `rhashtable`, workqueues, and the enclosing `nsim_dev`. Debugfs files inject failures for route offload, route deletion, resilient nexthop-group replace, nexthop bucket replace, and bucket activity.

Risks: accounting must stay consistent when queued work later fails; several paths intentionally decrement counts after replace detection. The event queue uses GFP_ATOMIC allocation and schedules a flush on failed delete preparation. `nsim_crypto` is not involved, but RCU/reference lifetimes of `fib_info` and `fib6_info` are critical. Failure injection can leave the kernel FIB with offload-failed flags by design.

Test signals: useful tests create/delete IPv4/IPv6 routes and rules with tight devlink resource sizes, verify trap/offload_failed flags, exercise multipath IPv6 append/delete, resilient nexthop bucket activity, debugfs failure knobs, notifier unregister teardown, and inconsistent dump recovery.
