# sources/distributed-fs/ceph-client/net/tipc/net.c

## Purpose
`net.c` manages TIPC network identity and network-mode lifecycle for a namespace. It initializes node identity or legacy node address, finalizes the node address, reinitializes dependent subsystems after address assignment, stops bearers/nodes on exit from network mode, and implements modern netlink get/set operations for network id, node id, legacy address, and legacy-address status.

## Important APIs, Types, And Functions
The exported functions are `tipc_net_init()`, `tipc_net_finalize_work()`, `tipc_net_stop()`, `tipc_nl_net_dump()`, `__tipc_nl_net_set()`, `tipc_nl_net_set()`, and `tipc_nl_net_addr_legacy_get()`. Internal helpers are `tipc_net_finalize()`, `__tipc_nl_add_net()`, and `__tipc_nl_addr_legacy_get()`.

## Control Flow
Initialization rejects a second configured node identity, logs entry into network mode, stores a supplied 128-bit node id, and optionally finalizes a supplied 32-bit legacy address. Finalization uses `cmpxchg()` to set `tipc_net.node_addr` only once, updates the node address, reinitializes local name publications, sockets, and self-monitor state, then publishes the node-state service for the new address. Deferred finalization runs under RTNL from work queued by address trial/discovery code.

Stopping checks whether an identity exists, then under RTNL stops bearers and all nodes before logging that network mode was left. Netlink dump emits the namespace `net_id` and two 64-bit halves of the 128-bit node id. Netlink set requires a nested `TIPC_NLA_NET`, rejects changes after a node address exists, validates net id range 1..9999, supports legacy address assignment through `TIPC_NLA_NET_ADDR`, and supports node-id assignment only when both halves are present.

## State And Persistence
State lives in `struct tipc_net`: node id, node address, trial address, net id, legacy address flag, broadcast link pointer, work item, and subsystem state reinitialized by finalization. The code publishes a `TIPC_NODE_STATE` service binding as persistent visible state once an address is finalized.

## Dependencies And Integration Points
The file depends on name distribution/table reinitialization, socket reinitialization, node and bearer shutdown, broadcast/link state, monitor self state, and generic netlink helpers. It is called by netlink configuration, discovery/address trial logic, namespace lifecycle, and the legacy netlink compatibility layer.

## Risks And Edge Cases
Identity and address are intended to be one-time configuration values; allowing changes after joining a network would invalidate publications, sockets, links, monitors, and peer state. `tipc_net_finalize()` is guarded with `cmpxchg()` to avoid double finalization from concurrent work paths. The netlink dump treats the node id as two `u64` words, so alignment and endian expectations matter for user space. Legacy address mode changes lookup semantics elsewhere in the name table.

## Test Signals
Tests should cover setting net id before and after join, invalid net ids, legacy address assignment, 128-bit node-id assignment with missing second half, duplicate initialization rejection, deferred finalization under RTNL, publication of `TIPC_NODE_STATE`, network stop teardown order, netlink dump/reply fields, and legacy-address get behavior.
