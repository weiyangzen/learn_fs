# sources/distributed-fs/ceph-client/net/sched/sch_api.c

## Purpose
`sch_api.c` is the packet scheduler API front end for Linux traffic control. It owns qdisc registration, qdisc lookup by handle/name, root and class grafting, netlink create/change/delete/get/dump handlers for qdiscs and traffic classes, common size/rate table support, qdisc watchdog timers, class hash helpers, and hardware offload helper calls. The file deliberately keeps algorithm-specific scheduling out of this layer; concrete qdisc modules provide `Qdisc_ops` and optional `Qdisc_class_ops`.

## Important APIs, Types, and Functions
The exported qdisc registry entry points are `register_qdisc()`, `unregister_qdisc()`, `qdisc_get_default()`, and `qdisc_set_default()`. Lookup and topology helpers include `qdisc_lookup()`, `qdisc_lookup_rcu()`, `qdisc_hash_add()`, `qdisc_hash_del()`, `qdisc_leaf()`, `qdisc_alloc_handle()`, and `qdisc_tree_reduce_backlog()`.

Common resource helpers include `qdisc_get_rtab()` / `qdisc_put_rtab()` for legacy rate tables, `qdisc_get_stab()` / `qdisc_put_stab()` plus `__qdisc_calculate_pkt_len()` for size tables, `qdisc_watchdog_init*()`, `qdisc_watchdog_schedule_range_ns()`, and `qdisc_watchdog_cancel()`. Class hash helpers are `qdisc_class_hash_init()`, `qdisc_class_hash_insert()`, `qdisc_class_hash_grow()`, `qdisc_class_hash_remove()`, and `qdisc_class_hash_destroy()`.

The central netlink paths are `tc_modify_qdisc()`, `__tc_modify_qdisc()`, `tc_get_qdisc()`, `__tc_get_qdisc()`, `tc_dump_qdisc()`, `tc_ctl_tclass()`, `__tc_ctl_tclass()`, and `tc_dump_tclass()`. Serialization helpers are `tc_fill_qdisc()` and `tc_fill_tclass()`. Offload helpers are `qdisc_offload_dump_helper()`, `qdisc_offload_graft_helper()`, `qdisc_offload_query_caps()`, and the root-specific `qdisc_offload_graft_root()`.

## Control Flow
Module initialization in `pktsched_init()` registers per-netns `/proc/net/psched` support, built-in qdiscs (`pfifo_fast`, `pfifo`, `bfifo`, head-drop pfifo, `mq`, `noqueue`), rtnetlink handlers for qdisc and class messages, and the tc wrapper layer. Individual modules later call `register_qdisc()` to add their `Qdisc_ops` to the global registry guarded by `qdisc_mod_lock`.

For qdisc creation/change, `tc_modify_qdisc()` parses `rtm_tca_policy`, optionally requests a qdisc module, resolves the target net device, takes the device ops lock, and delegates to `__tc_modify_qdisc()`. That function interprets `tcm_parent`, `tcm_handle`, and netlink flags to choose one of three paths: change an existing qdisc, create a new qdisc and graft it, or graft an existing handle. It rejects ingress children, handle minor bits on qdisc handles, parent loops via `check_loop()`, and moves between parents. `qdisc_create()` resolves `TCA_KIND`, allocates the qdisc, validates ingress/root handle rules, assigns automatic handles, applies shared block indexes and STABs, invokes `ops->init()`, installs rate estimators, hashes the qdisc, and emits tracepoints. `qdisc_graft()` then attaches the qdisc to either a root/ingress device queue or a classful parent, handling device deactivate/activate, offload notifications, refcounts, and rtnetlink notifications.

For qdisc get/delete, `tc_get_qdisc()` resolves the qdisc by parent/class leaf or explicit handle. Delete requires a nonzero class id and nonzero qdisc handle, then calls `qdisc_graft()` with `new == NULL`; get sends a `RTM_NEWQDISC` reply through `qdisc_get_notify()`. Dump walks all devices and their root plus ingress qdiscs, skipping built-in and invisible qdiscs unless requested.

Traffic class operations follow the same netlink pattern. `__tc_ctl_tclass()` normalizes parent/handle major IDs, locates a classful qdisc, uses the qdisc's `Qdisc_class_ops` to find/delete/get/change a class, rejects shared block attrs on classes, and rebinds classifier references when a class is created or removed. Class dump iterates root and hashed child qdiscs, calling each qdisc's class walker.

## State and Persistence
All state is in kernel memory. Global process-wide scheduler state includes `qdisc_base`, `default_qdisc_ops`, `qdisc_rtab_list`, and `qdisc_stab_list`. Per-device state is stored in `net_device`, `netdev_queue`, qdisc hash tables, root qdisc pointers, and optional ingress queue pointers. Per-qdisc state includes handles, parent IDs, refcounts, stats, STAB pointers, rate estimators, optional class operations, and module ownership.

There is no disk persistence. Netlink requests mutate in-memory qdisc trees; dumps reconstruct user-visible state from current kernel structures. RCU is used for qdisc hashes and size tables, RTNL/device operation locks serialize configuration, `sch_tree_lock()` protects qdisc tree changes, and qdisc watchdogs use hrtimers to reschedule roots when packets become eligible.

## Dependencies and Integration Points
This file sits between rtnetlink (`RTM_*QDISC`, `RTM_*TCLASS`) and qdisc modules. It depends on `net/pkt_sched.h`, `net/pkt_cls.h`, gnet stats, BPF module ownership helpers, RCU, hrtimer, netdevice queue management, rate estimators, and optional `CONFIG_PROC_FS`, `CONFIG_NET_CLS`, and retpoline mitigation static keys. Hardware offload integrates through `net_device_ops->ndo_setup_tc()` using `TC_SETUP_ROOT_QDISC`, qdisc-specific setup types, and `TC_QUERY_CAPS`.

## Risks
The highest-risk areas are tree mutation, refcounting, and lock/RCU ordering. Root grafting must not leave device queues pointing at freed qdiscs, ingress/clsact replacement must avoid concurrent miniqdisc access, and module refs must be released on all create/change errors. Handle normalization is subtle: wrong major/minor interpretation can target the wrong class or allow invalid topology. STAB/rate table sharing uses manual refcounts, so error paths must put old references exactly once. Netlink dump paths must preserve cursor state without skipping or duplicating qdiscs under partial skb output.

## Test Signals
Useful tests are `tc qdisc add/change/replace/del/show` across root, ingress, clsact, and classful children; automatic handle allocation; duplicate qdisc registration failure; unknown qdisc module autoload; class create/delete/get/dump with filters bound to classes; STAB and rate estimator configuration; invisible qdisc dump filtering; qdisc tree loop rejection; root graft on multiqueue devices; ingress replacement under active filters returning busy; and offload-capable drivers returning success, `-EOPNOTSUPP`, and hard errors.
