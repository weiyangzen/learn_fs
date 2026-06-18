# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_router.h

## Purpose

`spectrum_router.h` is the internal router subsystem interface for the mlxsw Spectrum driver. It exposes the in-memory router object, route interface (RIF), neighbor, nexthop, IP-in-IP, bridge/router replay, and counter entry points used by switchdev, tunnel, trap, and port code. The header does not implement behavior, but it defines the shared contracts that let other mlxsw files interact with the L3 hardware offload layer without depending on private router implementation details.

## Important APIs, Types, And Functions

`struct mlxsw_sp_router` is the central state holder. It contains hash tables for router interfaces, neighbors, nexthop groups, and nexthops; a `gen_pool` and RIF array for RIF index allocation; IDR and atomic counters for RIF MAC profiles; virtual-router and LPM tree state for IPv4/IPv6; delayed works for neighbor refresh, unresolved nexthop probing, and nexthop group activity; notifier blocks for FIB, nexthop, netevent, address, and netdevice changes; arrays of RIF and IPIP operation tables; NVE decap configuration; a mutex for shared router resources; and adjacency-related capabilities.

`struct mlxsw_sp_router_nve_decap` records the configured underlay table, tunnel index, underlay protocol, source address, and valid bit for NVE decapsulation. `struct mlxsw_sp_rif_ipip_lb_config` describes loopback IPIP RIF type, key, underlay protocol, and source address. `enum mlxsw_sp_rif_counter_dir` distinguishes ingress and egress RIF counters.

The exported function declarations cover RIF lookup and device association (`mlxsw_sp_rif_by_index()`, `mlxsw_sp_rif_dev_ifindex()`, `mlxsw_sp_rif_dev_is()`), RIF counters, neighbor iteration and counters, IPIP tunnel update/demotion, nexthop iteration and adjacency/counter updates, ECN initialization, bridge VLAN-to-router replay, LAG router replay, and netdevice enslavement/deslavement replay.

## Control Flow

The header describes a router subsystem driven by kernel notifiers and explicit replay helpers. Address/FIB/nexthop/netdevice events update the router's hash tables and delayed work queues. Other subsystems ask the router for RIF, neighbor, and nexthop state when programming FDB entries, SPAN tunnel paths, bridge VLANs, or LAG changes. IPIP tunnel changes go through update and demotion helpers that can recreate loopback RIFs, preserve encapsulation state, and update nexthops.

## State And Persistence

All persistence is runtime driver state and hardware programming. `struct mlxsw_sp_router` owns allocator state, hash tables, delayed work, notifier registrations, reference/counter fields, and hardware index values such as `adj_trap_index`. There is no disk persistence. The mutex documents that shared router resources require serialization, while several counters use atomics and refcounts to coordinate concurrent notification paths.

## Dependencies And Integration Points

The header depends on `spectrum.h`, `reg.h`, Linux networking device types, rhashtable, IDR, gen_pool, delayed work, notifiers, and mlxsw L3 address/protocol definitions. It integrates with switchdev bridge code via `mlxsw_sp_router_bridge_vlan_add()` and bridge/LAG replay helpers, with SPAN GRE resolution through `mlxsw_sp_l3addr` and router underlay helpers, and with tunnel/NVE code through IPIP and NVE decap structures.

## Risks And Edge Cases

The router state spans asynchronous notifier callbacks and delayed workers, so lifetime and lock ordering are critical. RIF index allocation deliberately offsets gen_pool allocations because `gen_pool_alloc()` returns zero on failure; code that bypasses the offset can confuse index zero with allocation failure. IPIP demotion by source address can affect multiple tunnels and must preserve the `except` tunnel. LPM trees, nexthop groups, and neighbor counters are shared resources whose reference counts must remain balanced through replay and rollback paths.

## Test Signals

Useful signals include bridge VLAN RIF creation/removal, LAG join/leave with existing router interfaces, IPv4/IPv6 neighbor add/delete and counter updates, nexthop group activity, IPIP tunnel creation and demotion, NVE decap programming, FIB notifier replay after device enslave/deslave, and cleanup of delayed works/notifier registrations. No local executable tests were run for this research item.
