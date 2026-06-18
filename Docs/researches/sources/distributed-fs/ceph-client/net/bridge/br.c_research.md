<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br.c -->
# sources/distributed-fs/ceph-client/net/bridge/br.c

Purpose: provides generic bridge module lifecycle, netdevice and switchdev notifiers, per-net cleanup, STP protocol registration, boolean option routing, and bridge module init/exit.

Important APIs, types, and functions: notifier callbacks are `br_device_event`, `br_switchdev_event`, and `br_switchdev_blocking_event`. User-facing option helpers are `br_boolopt_toggle`, `br_boolopt_get`, `br_boolopt_multi_toggle`, and `br_boolopt_multi_get`; internal options are updated by `br_opt_toggle`. Module lifecycle is handled by `br_init` and `br_deinit`, and per-net namespace cleanup by `br_net_exit_rtnl`.

Control flow: netdevice events for bridge masters and ports update VLAN state, sysfs, FDB entries, STP bridge IDs, carrier state, MTU, features, and port deletion. Switchdev events add, delete, flush, and mark externally learned or offloaded FDB entries; blocking switchdev events handle port offload, unoffload, and replay. Boolean options dispatch to feature-specific code for multicast VLAN snooping, MST, MDB offload failure notification, local VLAN 0 FDB behavior, and no-link-local learning. `br_init` registers STP, FDB, pernet ops, netfilter core, netdevice notifier, switchdev notifiers, netlink, and ioctl hooks with reverse-order cleanup on failure.

State and persistence: maintains module-level notifier registrations and per-net bridge devices. Bridge option bits live in `br->options`. FDB, VLAN, STP, and switchdev changes persist in each `struct net_bridge` until device deletion or namespace teardown.

Dependencies and integration points: depends on LLC/STP, netdevice notifier API, switchdev, bridge netlink/ioctl/sysfs, FDB, VLAN, multicast, MST, and netfilter core. `MODULE_ALIAS_RTNL_LINK("bridge")` links rtnetlink bridge creation to the module.

Risks: notifier ordering and locking matter. `br_device_event` mixes RTNL, spinlock, and VLAN/FDB/STP side effects; missed notifications can leave stale FDB entries or wrong bridge MAC. Option multi-toggle can partially apply options before an error. Init error paths must unwind exactly. Switchdev offload replay has hardware integration risk.

Test signals: bridge module load/unload, creating/deleting bridges in namespaces, adding/removing ports, changing port MAC/MTU/name/carrier, VLAN events, switchdev FDB offload tests, boolean option netlink tests, and failure-injection tests around init registration paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br.c -->
