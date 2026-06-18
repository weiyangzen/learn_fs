# sources/distributed-fs/ceph-client/net/shaper/shaper.c

## Purpose
Implements the generic net shaper netlink API backend for network devices. It manages per-device shaper hierarchies, validates user attributes against driver capabilities, handles get/dump/set/delete/group/capability operations, and coordinates tentative software state with driver callbacks.

## Important APIs, Types, And Functions
Externally used functions include netlink callbacks declared in `shaper_nl_gen.h`, `net_shaper_flush_netdev`, and `net_shaper_set_real_num_tx_queues`. Core types are `struct net_shaper_hierarchy` with an xarray, `struct net_shaper_nl_ctx`, `struct net_shaper_binding`, `struct net_shaper`, and `struct net_shaper_ops`. Key helpers include handle/index conversion, context setup/cleanup, `net_shaper_lookup`, `net_shaper_hierarchy_setup`, `net_shaper_pre_insert`, `net_shaper_commit`, `net_shaper_rollback`, parsers, validators, `__net_shaper_delete`, and `__net_shaper_group`.

## Control Flow
Pre-doit hooks resolve and reference a netdev, and write operations take the netdev instance lock. Handles encode scope and id into xarray indexes; entries are inserted tentatively without `NET_SHAPER_VALID`, configured in the driver, then committed with a memory barrier and VALID mark. Gets and dumps run under RCU and expose only valid entries. Set parses incremental attributes, validates capability flags and queue ids, disallows creating new node shapers, pre-inserts, calls `ops->set`, and commits or rolls back. Delete reparents child leaves when deleting a node, invokes driver delete, erases xarray entries, and recursively removes empty parents. Group parses a node plus leaves, allocates ids for new nodes, validates nesting and duplicate leaves, calls `ops->group`, commits node/leaves, cleans old empty nodes best-effort, and replies with the node handle. Capability commands report driver-supported flags by scope. Flush and queue-count shrink remove per-device hierarchy state.

## State And Persistence
State is per-netdevice, in-memory, and pointed to by `dev->net_shaper_hierarchy`. The xarray stores `struct net_shaper` entries and uses `NET_SHAPER_VALID` to separate tentative from visible state. No durable persistence exists.

## Dependencies And Integration Points
Depends on generic netlink, generated YNL ops, netdevice lifetime/ref tracking, netdev locks, RCU, xarray allocation, driver-provided `net_shaper_ops`, and UAPI attributes from `linux/net_shaper.h`.

## Risks
High-risk areas are tentative insertion rollback, parent/leaf count consistency, reparenting on node delete, RCU visibility and memory barriers, netdev unregister races, generated policy drift, and best-effort cleanup after successful grouping leaving stale empty nodes if driver delete fails.

## Test Signals
Netlink tests should cover get before set, set unsupported attrs/metrics, queue id bounds, dump while deleting, node id auto-allocation, group with duplicate leaves, reparenting and empty-node cleanup, driver callback failures and rollback, netdev unregister flush, and `real_num_tx_queues` shrink.
