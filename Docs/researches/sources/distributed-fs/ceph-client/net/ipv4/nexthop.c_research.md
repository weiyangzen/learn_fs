# sources/distributed-fs/ceph-client/net/ipv4/nexthop.c

## Purpose
Generic nexthop object implementation for IPv4 and IPv6 routing. It provides netlink CRUD/dump, shared nexthop lifetime, nexthop groups, resilient bucket groups, hardware offload notifications/statistics, FIB compatibility checks, route update notifications, device event cleanup, and per-network-namespace storage.

## Important APIs, types, and functions
Exported APIs include `nexthop_find_by_id()`, `nexthop_select_path()`, `fib_check_nexthop()`, `fib6_check_nexthop()`, `nexthop_for_each_fib6_nh()`, notifier register/unregister functions, `nexthop_set_hw_flags()`, `nexthop_bucket_set_hw_flags()`, and `nexthop_res_grp_activity_update()`. Major structures are `struct nexthop`, `struct nh_info`, `struct nh_group`, `struct nh_grp_entry`, `struct nh_res_table`, and `struct nh_res_bucket`. Netlink handlers cover new/delete/get/dump nexthops and resilient buckets.

## Control flow
Creation parses netlink attributes into `struct nh_config`, validates group or single constraints, validates devices under RTNL, allocates single or group objects, initializes IPv4/IPv6 FIB nexthop data, and inserts into the per-net rb-tree. Replacement validates all existing IPv4/IPv6 routes and parent groups, then swaps group or single internals under RCU, sends notifiers, flushes route caches, and destroys the temporary new object. Deletion sends delete notifiers, removes the rb-tree node, flushes linked routes, removes group memberships, cancels resilient upkeep, removes device-hash entries, increments the sequence, and drops the reference.

Path selection returns single nexthops directly, selects hash-threshold groups by weighted upper bounds, selects FDB groups without neighbor-good filtering, and selects resilient groups by hash bucket. Resilient upkeep migrates buckets from overweight entries to underweight entries when buckets are idle or forced by the unbalanced timer, with hardware notifier veto support and bucket netlink notifications.

## State and persistence
All state is in memory and scoped to `struct net`: `rb_root` by id, `devhash` by device, `seq` for dump consistency, and `last_id_allocated` for auto ids. Nexthops are RCU-freed. Groups hold member references and per-cpu stats. Resilient tables hold delayed work, bucket mappings, timers, underweight lists, hardware flags, and activity timestamps.

## Dependencies and integration points
Integrates with rtnetlink, netdevice notifier events, IPv4 FIB, IPv6 FIB, lwtunnel encapsulation, neighbor reachability, l3mdev/VRF, hardware offload notifier chains, and pernet init/exit. Emits `RTM_NEWNEXTHOP`, `RTM_DELNEXTHOP`, and `RTM_NEWNEXTHOPBUCKET`.

## Risks
Concurrency and rollback dominate: RTNL, RCU readers, delayed work, per-cpu stats, notifier callbacks, and route lists interact. Replacement failures must restore pointers, parent links, protocol/flag fields, and hardware notifications. Resilient bucket migration can be vetoed unless forced. Validation must prevent nested groups, mixed FDB semantics, invalid weights, blackhole misuse, scope mismatches, and IPv4/IPv6 route incompatibility.

## Test signals
Test single IPv4/IPv6 add/replace/delete/get/dump, auto ids, blackhole, lwt encap, FDB nexthops, weighted groups, resilient buckets/timers/migration, dump continuation, bucket filters, notifier veto/rollback, hardware stats, route cache invalidation, route scope checks, device down/unregister/MTU change, netns teardown, and concurrent path selection during replacement.
