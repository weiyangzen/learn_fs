# sources/distributed-fs/ceph-client/net/bridge/br_multicast_eht.c

## Purpose

`br_multicast_eht.c` implements Explicit Host Tracking for bridge multicast fast leave. It augments a `net_bridge_port_group` with per-host and per-source trees so the bridge can tell which hosts on a shared port still need a source/group membership. When the last tracked host for a source disappears, it can delete the corresponding `S,G` source entry and, in some cases, delete the port group quickly.

## Important APIs, Types, and Functions

The public functions are `br_multicast_eht_clean_sets()`, `br_multicast_eht_handle()`, and `br_multicast_eht_set_hosts_limit()`. Inline helpers and data structures are declared in `br_private_mcast_eht.h`: `struct net_bridge_group_eht_host`, `struct net_bridge_group_eht_set_entry`, `struct net_bridge_group_eht_set`, `union net_bridge_eht_addr`, `br_multicast_eht_should_del_pg()`, and host count helpers.

Each port group owns two red-black trees: `pg->eht_host_tree`, keyed by host address, and `pg->eht_set_tree`, keyed by source address. Each EHT source set owns an `entry_tree` keyed by host address. Hosts also keep an hlist of their set entries so a host can be removed across all sources.

Core lookup/create/delete functions are `br_multicast_eht_host_lookup()`, `br_multicast_eht_set_lookup()`, `br_multicast_eht_set_entry_lookup()`, `__eht_lookup_create_host()`, `__eht_lookup_create_set()`, `__eht_lookup_create_set_entry()`, `br_multicast_del_eht_set_entry()`, `br_multicast_del_eht_host()`, and `br_multicast_del_eht_set()`.

Protocol update functions are `br_multicast_eht_allow()`, `br_multicast_eht_block()`, `br_multicast_eht_inc()`, `br_multicast_eht_exc()`, `__eht_ip4_handle()`, and `__eht_ip6_handle()`.

## Control Flow

`br_multicast_eht_handle()` is called from the IGMPv3/MLDv2 source-filter state-machine in `br_multicast.c`. EHT is enabled only when the bridge port has `BR_MULTICAST_FAST_LEAVE`; otherwise the function exits with no change.

On a report, the host address is copied into `union net_bridge_eht_addr` and the message type dispatches to IPv4 or IPv6 handlers. ALLOW adds source entries when the host is in INCLUDE mode and deletes entries when it is in EXCLUDE mode. BLOCK does the inverse. INCLUDE and EXCLUDE reports use `__eht_inc_exc()` to optionally flush a host's previous entries when the host changes mode or when a to-report transition requires replacement.

Creation links three objects: an EHT set for the source, an EHT host for the listener address and filter mode, and a set entry connecting both. Set and entry timers are refreshed to group membership interval (`br_multicast_gmi()`). Deletion removes the set entry from both the per-source RB tree and host hlist, destroys the host if it has no remaining entries, and destroys the set when its entry tree is empty.

Timers `br_multicast_eht_set_entry_expired()` and `br_multicast_eht_set_expired()` run under `br->multicast_lock` and delete stale entries/sets. `br_multicast_eht_clean_sets()` removes all EHT sets for a port group when the group itself is deleted.

## State and Persistence Behavior

EHT state is transient in-memory state rooted in the port group. It is deleted when port-group membership is deleted, source membership expires, host entries time out, or bridge/port cleanup runs. Memory reclamation uses the multicast GC list and `system_long_wq`, matching `br_multicast.c` object lifetime patterns.

Host count state lives in `net_bridge_port.multicast_eht_hosts_cnt` and `multicast_eht_hosts_limit`. `br_multicast_eht_set_hosts_limit()` updates the limit under `multicast_lock`; new hosts are refused when the count reaches the limit. The auto-created zero-source entry used for EXCLUDE host mode is intentionally not counted against per-host source entry limits.

## Dependencies and Integration Points

This file depends on `br_multicast.c` for group/source state, timers, and deletion functions. It calls `br_multicast_find_group_src()` and `br_multicast_del_group_src()` to remove bridge `S,G` source state when no EHT set remains for a source. Netlink integration is indirect: `br_netlink.c` exposes and sets EHT host limits and reports host counters. EHT behavior is also tied to the bridge port `BR_MULTICAST_FAST_LEAVE` flag.

## Risks and Edge Cases

The RB-tree and hlist relationships must stay consistent; deleting a set entry touches the source tree, the host list, host counters, GC list, and potentially parent host/set destruction. A bug in zero-address handling could incorrectly count or drop EXCLUDE-mode tracking. The helper `__eht_del_set_entries()` appears to copy source bytes into `src_ip` directly, so its correctness depends on the `struct br_ip` layout and should be reviewed carefully if that structure changes.

The EHT limit protects memory growth, but hitting it silently prevents new EHT host creation and can reduce fast-leave precision. Timer expiration and report processing both mutate the same trees under `multicast_lock`; missing lock coverage would be severe.

## Test Signals

Good tests use multiple hosts behind one bridge port with fast leave enabled, exercising IGMPv3 and MLDv2 INCLUDE/EXCLUDE transitions, ALLOW/BLOCK messages, host mode changes, zero-source EXCLUDE tracking, source expiration, and host-limit rejection. Observable signals are `bridge -d link` EHT counters, MDB/source entry changes after last host leaves, packet captures showing reduced query/leave behavior, and memory lifetime checks under KASAN/KCSAN/lockdep.
