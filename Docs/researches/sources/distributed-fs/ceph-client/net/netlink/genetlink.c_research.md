# sources/distributed-fs/ceph-client/net/netlink/genetlink.c

## Purpose

`genetlink.c` implements Generic Netlink on top of the core netlink socket layer. It registers generic netlink families, validates and dispatches family operations, manages multicast group IDs, exposes the `nlctrl` controller family, supports policy dumping, per-socket family-private storage, per-network-namespace generic netlink sockets, and all-namespace multicast helpers.

## Important APIs, Types, and Functions

Family registry state is held in `genl_fam_idr`; multicast group allocation is tracked in `mc_groups`. Synchronization uses `genl_mutex` for serialized processing and `cb_lock` to coordinate callbacks/unregistration.

Public APIs include `genl_register_family()`, `genl_unregister_family()`, `genlmsg_put()`, `genl_sk_priv_get()`, `__genl_sk_priv_get()`, `genlmsg_multicast_allns()`, and `genl_notify()`. Operation lookup and normalization use `genl_get_cmd()`, `genl_get_cmd_full()`, `genl_get_cmd_small()`, `genl_get_cmd_split()`, `genl_cmd_full_to_split()`, and `genl_op_iter`.

Message processing flows through `genl_rcv()`, `genl_rcv_msg()`, `genl_family_rcv_msg()`, `genl_family_rcv_msg_doit()`, and `genl_family_rcv_msg_dumpit()`. Controller commands are implemented by `ctrl_getfamily()`, `ctrl_dumpfamily()`, `ctrl_dumppolicy_start()`, `ctrl_dumppolicy()`, and `ctrl_dumppolicy_done()`.

## Control Flow

`genl_init()` first registers the controller family, then registers pernet generic netlink sockets. Each namespace gets `net->genl_sock` via `netlink_kernel_create()` with `genl_rcv`, bind, unbind, and release hooks.

Family registration validates operation arrays, reserves or allocates a family ID, validates multicast groups, expands netlink group bitmaps, unlocks, and broadcasts controller notifications. Unregistration removes multicast users from all namespaces, clears group IDs, removes the family from the IDR, waits for generic netlink sockets currently destructing, frees per-socket private xarrays, and emits a delete event.

Receive dispatch runs under `cb_lock`; non-parallel families also take `genl_mutex`. The generic netlink header is checked, the requested command is resolved to either a `doit` or `dumpit` operation based on `NLM_F_DUMP`, permissions are enforced, attributes are parsed against the selected policy, and the family callback is called. Dumps wrap family callbacks in core netlink dump control callbacks so operation-specific `start`, `dumpit`, and `done` get consistent `genl_info`.

The controller family reports family metadata, command capabilities, multicast groups, and policies. Policy dumps first build a policy index map using `policy.c`, then emit per-command policy index references followed by policy attribute descriptions.

## State and Persistence Behavior

Registered families persist in `genl_fam_idr` until unregistered. Each family stores assigned `id` and `mcgrp_offset`. Optional per-socket private data persists in an xarray keyed by socket pointer and is freed from the generic netlink release hook. Multicast group bitmaps persist globally and drive `af_netlink.c` group counts.

Dump state persists in allocated `struct genl_dumpit_info` and controller policy context stored in `netlink_callback`. Command validation defaults reserved future operations without explicit policy to a reject-all policy, which is a persistent safety behavior for families that set `resv_start_op`.

## Dependencies and Integration Points

Generic netlink depends on `af_netlink.c` for kernel sockets, multicast delivery, dump lifecycle, group resizing, and socket release callbacks. It depends on `policy.c` for `CTRL_CMD_GETPOLICY`. It exposes family metadata to userspace through `nlctrl` and to modules through exported Generic Netlink APIs. Family callbacks integrate with capability helpers in `af_netlink.c` and with net namespace state through `genl_info_net_set()`.

## Risks and Edge Cases

Family unregistration must not race with live callbacks or destructing sockets. Split operation arrays must be sorted and have exactly one DO or DUMP capability per entry. Legacy validation flags can disable strict parsing, so new operations should use explicit policy and reserved operation boundaries. Multicast group allocation has historical reserved IDs and must resize group maps across namespaces without assuming rollback is complete on allocation failure. Controller policy dumping can return partial skbs and must keep cursor state consistent.

## Test Signals

Useful signals include `genl ctrl list`, `genl ctrl get name nlctrl`, `CTRL_CMD_GETPOLICY` userspace queries, module load/unload for a generic netlink family, namespace multicast tests, capability-gated multicast binding, family private socket storage tests, and build coverage for families using full, small, and split operation tables.
