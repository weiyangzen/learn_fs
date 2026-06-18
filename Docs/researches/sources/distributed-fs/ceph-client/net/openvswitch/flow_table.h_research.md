# sources/distributed-fs/ceph-client/net/openvswitch/flow_table.h

## Purpose
`flow_table.h` declares the in-memory flow table structures and public table operations used by the Open vSwitch datapath. It exposes enough structure layout for datapath code to hold a table while keeping lookup, mask, and allocation algorithms in `flow_table.c`.

## Important APIs and Types
`struct mask_cache_entry` and `struct mask_cache` define the per-CPU skb-hash to mask-index cache. `struct mask_array_stats`, `struct mask_array`, and `struct mask_count` support ordered mask arrays and per-mask usage accounting. `struct table_instance` is an RCU-replaceable hash bucket array with a node version bit and random hash seed. `struct flow_table` owns the main key table, UFID table, mask cache, mask array, rehash timestamp, and counts.

Public APIs include module slab lifecycle (`ovs_flow_init()`, `ovs_flow_exit()`), flow object lifecycle (`ovs_flow_alloc()`, `ovs_flow_free()`), table lifecycle (`ovs_flow_tbl_init()`, `ovs_flow_tbl_destroy()`, `ovs_flow_tbl_flush()`), insertion/removal, count and mask-cache sizing, dump iteration, packet/stat lookup, exact key lookup, UFID lookup, comparison, key masking, mask rebalance, and flush helper `table_instance_flow_flush()`.

## Control Flow and Integration
`datapath.c` initializes a `struct flow_table` per datapath, calls lookup from the packet processing fast path, and uses insert/remove/flush from generic-netlink flow commands. The action and flow netlink layers rely on `ovs_flow_mask_key()` to derive stored masked keys from user-provided masks.

## State and Persistence
Every field is runtime memory only. RCU pointer annotations on table instances, mask cache, and mask array establish reader/writer replacement semantics. Counts are maintained by writers under OVS locking.

## Dependencies
The header depends on Linux netlink, Open vSwitch UAPI, RCU, time/jiffies, tunnel headers, and `flow.h`.

## Risks
Callers must respect locking comments from the implementation: insert/remove/flush under OVS mutex, lookup under RCU or explicit BH-disabled wrappers as required, and deferred flow free after deletion. Direct manipulation of the structures outside `flow_table.c` risks RCU and refcount bugs.

## Test Signals
Build coverage, datapath flow command tests, packet lookup selftests, UFID dump/get/delete tests, and lockdep/KCSAN runs are useful signals.
