# sources/distributed-fs/ceph-client/net/batman-adv/originator.c

## Purpose
Owns originator and neighbor state for batman-adv routing. It allocates the originator hash table, creates and looks up originator, neighbor, hard-interface-neighbor, VLAN, and per-interface info objects, exposes route/neighbor lookup helpers, purges stale topology state, and delegates originator/neighbor netlink dumps to the selected routing algorithm.

## APIs, Types, and Functions
Public entry points include `batadv_orig_hash_find()`, `batadv_compare_orig()`, `batadv_orig_node_vlan_get/new/release()`, `batadv_originator_init/free()`, `batadv_hardif_neigh_get()`, `batadv_neigh_node_get_or_create()`, `batadv_neigh_ifinfo_get/new/release()`, `batadv_orig_ifinfo_get/new/release()`, `batadv_orig_router_get()`, `batadv_orig_to_router()`, `batadv_hardif_neigh_dump()`, `batadv_orig_node_new/release()`, `batadv_purge_orig_ref()`, and `batadv_orig_dump()`.

## Control Flow
`batadv_originator_init()` creates a 1024-bucket hash table, assigns lockdep classing, and starts the periodic purge worker. New originator-related objects follow a get-or-create pattern: first look up under RCU without expensive locking, then lock the relevant list, recheck, allocate with `GFP_ATOMIC`, initialize krefs/list nodes/locks/timestamps, take references to hard interfaces or hardif-neighbor objects, and add to RCU hlist.

Routing lookup starts from `batadv_orig_hash_find()` by originator MAC, then `batadv_orig_to_router()` calls the algorithm's router selection through `batadv_find_router()`. `batadv_orig_router_get()` directly reads an `orig_ifinfo->router` RCU pointer for a specific outgoing interface. Netlink originator and neighbor dumps validate mesh and primary interface state, optionally resolve a hardif filter, then call `algo_ops->orig.dump` or `algo_ops->neigh.dump`.

The purge worker calls `batadv_purge_orig_ref()` periodically. It scans the hash table under bucket locks, removes originators timed out for twice the purge timeout, deletes gateway and TT global state for them, purges fragment queues, removes stale neighbor/per-interface info for down or removed hard interfaces, recomputes best neighbors for default and active outgoing interfaces, updates routes, and finally triggers gateway election.

## State and Persistence
Persistent state is the RCU-protected `bat_priv->orig_hash` and each `struct batadv_orig_node` subtree: neighbor list, VLAN list, orig-ifinfo list, TT buffer, broadcast sequence state, fragment queues, multicast flags/list nodes, last-seen timestamps, route candidates, and per-algorithm private state initialized through algorithm hooks. Objects are kref-managed and mostly RCU-freed. The delayed purge work persists until `batadv_originator_free()` cancels it and tears down all buckets.

## Dependencies and Integration
Depends on hash helpers, routing algorithm ops, hard-interface lifetime, routing updates, gateways, TT, DAT, fragmentation, multicast purge hooks, netlink lookup helpers, workqueues, RCU, krefs, and jiffies timeout helpers. It is a central integration point for BATMAN_IV/BATMAN_V algorithm-specific metrics while keeping generic object lifetime and purge behavior common.

## Risks
This file has dense lifetime rules: hash buckets, nested hlists, RCU readers, krefs, hardif refs, and delayed free callbacks all interact. Purge removes objects while algorithms may be reading route state, so route pointers and last bonding candidates must be cleared with matching puts. Timeout thresholds influence route stability and stale forwarding. `batadv_orig_hash_find()` uses `batadv_compare_eth(orig_node, data)`, relying on the originator MAC being the first field in `struct batadv_orig_node`. Multicast purge runs from the RCU free callback, so it must tolerate originator teardown ordering.

## Test Signals
Coverage should include creating originators, duplicate get-or-create races, VLAN VID validation, neighbor creation on multiple hard interfaces, ifinfo creation for default and concrete outgoing interfaces, route lookup before/after router updates, originator and neighbor netlink dumps with and without hardif filters, purging stale neighbors due to timeout and interface status, full originator timeout cleanup including TT/gateway deletion, fragment purge, gateway election after purge, and RCU/kref leak detection on mesh teardown.
