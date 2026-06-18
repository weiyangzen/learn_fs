# sources/distributed-fs/ceph-client/net/openvswitch/flow_table.c

## Purpose
`flow_table.c` implements Open vSwitch kernel flow object allocation, masked flow lookup, UFID lookup, mask management, hash table resizing/rehashing, flow flushing, and mask-cache rebalancing. It is the datapath's fast path match engine.

## Important APIs, Types, and Functions
`ovs_flow_mask_key()` applies a `struct sw_flow_mask` to a `struct sw_flow_key`, optionally initializing only the active mask range. `ovs_flow_alloc()` and `ovs_flow_free()` allocate and release `struct sw_flow` objects, default stats, per-CPU stats pointers, action blobs, unmasked identifiers, and cpumasks.

The table is split into `struct table_instance` for masked-key lookup and another `table_instance` for UFID lookup. `ovs_flow_tbl_init()`, `ovs_flow_tbl_destroy()`, `ovs_flow_tbl_flush()`, `ovs_flow_tbl_insert()`, and `ovs_flow_tbl_remove()` manage the lifecycle. `ovs_flow_tbl_dump_next()` iterates RCU buckets for dumps.

Mask management is handled by `struct mask_array`, `tbl_mask_array_alloc()`, `tbl_mask_array_add_mask()`, `tbl_mask_array_del_mask()`, `flow_mask_find()`, `flow_mask_insert()`, and `flow_mask_remove()`. Masks are refcounted under the OVS mutex and freed by RCU when the last flow using the mask is removed. Per-mask usage counters are maintained per CPU and rebased with `masks_usage_zero_cntr`.

Lookup starts in `ovs_flow_tbl_lookup_stats()`. It optionally uses a per-CPU `struct mask_cache` keyed by skb hash and recirc id, then calls `flow_lookup()`, which tries a cached mask index first and falls back to all masks. `masked_flow_lookup()` hashes the masked key range, finds a bucket, and compares masked longs. `ovs_flow_tbl_lookup()` is the preemptible netlink-facing lookup wrapper; `ovs_flow_tbl_lookup_exact()` and `ovs_flow_tbl_lookup_ufid()` support command handlers.

`ovs_flow_masks_rebalance()` sorts masks by observed use and replaces the mask array under RCU so frequently hit masks are tried earlier. `ovs_flow_init()` and `ovs_flow_exit()` manage the `sw_flow` and `sw_flow_stats` slab caches.

## Control Flow
On flow insert, the caller provides a masked key and mask. `flow_mask_insert()` reuses an existing equivalent mask or adds a new one, `flow_key_insert()` computes the masked hash and inserts into the main table, and `flow_ufid_insert()` optionally inserts into the UFID table. Packet lookup reads the current table, mask array, and mask cache under RCU, masks the incoming key for candidate masks, and returns the first matching flow. Removal deletes the flow from both tables, decrements mask references, and leaves actual memory release to the caller and RCU.

## State and Persistence
All state is in memory. Hash table instances, mask arrays, and mask caches are replaced under RCU so readers can continue during rehash, resize, and rebalance. `table->count`, `ufid_count`, mask refcounts, and mask usage counters are protected by OVS mutex for writes or per-CPU synchronization for counters. The mask cache is deliberately approximate and can contain stale entries; misses trigger full lookup and stale entries are cleared.

## Dependencies and Integration Points
It depends on `flow.h`, `flow_netlink.h`, jhash, RCU, per-CPU allocation, kernel sort, and OVS locking helpers. `datapath.c` uses it for packet lookup, flow command lookup, inserts, deletes, dumps, and periodic mask rebalancing.

## Risks
The fast path depends on strict RCU, bottom-half, and OVS mutex discipline. `flow_lookup()` must run with BH disabled because it updates this-CPU mask counters. Mask range alignment and key layout must remain valid. Rehash and node version toggling must not lose flows. Mask cache staleness is expected, but stale indexes must not return incorrect matches. Flow free must release UFID/key ownership and nested action resources.

## Test Signals
Signals include flow insert/remove/flush/dump tests, exact-match and wildcard lookup tests, UFID lookup tests, concurrent packet lookup with flow updates, mask cache resize/rebalance tests, RCU stall/leak checks, and high-mask-count performance counters showing reduced `n_mask_hit` after rebalance.
