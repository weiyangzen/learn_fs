# sources/distributed-fs/ceph-client/net/openvswitch/datapath.h

## Purpose

This header defines the core Open vSwitch datapath data structures, per-skb control block, per-net state, per-CPU action scratch state, locking helpers, vport lookup helpers, and exported datapath/action interfaces used across OVS source files.

## Important APIs, Types, and Functions

Important structures include `dp_stats_percpu`, `dp_nlsk_pids`, `datapath`, `ovs_skb_cb`, `dp_upcall_info`, `ovs_net`, `ovs_frag_data`, `deferred_action`, `action_fifo`, `action_flow_keys`, and `ovs_pcpu_storage`. Constants include datapath port/hash limits, mask rebalance interval, deferred action FIFO size, recursion limit, and supported packet hash flags.

The header declares `ovs_lock()`, `ovs_unlock()`, `ovs_lookup_vport()`, `ovs_dp_process_packet()`, `ovs_dp_detach_port()`, `ovs_dp_upcall()`, `ovs_dp_get_upcall_portid()`, `ovs_dp_name()`, `ovs_vport_cmd_build_info()`, `ovs_execute_actions()`, and `ovs_dp_notify_wq()`. It also provides `OVS_CB()`, `ASSERT_OVSL()`, RCU dereference helpers, datapath net getters/setters, vport lookup wrappers, `get_dp_rcu()`, and `get_dp()`.

## Control Flow

The header has inline lookup/control helpers. `get_dp_rcu()` maps a datapath ifindex to the internal vport and datapath under RCU. `get_dp()` wraps that lookup while accepting either RCU or `ovs_mutex`. Vport accessors encode locking expectations: plain RCU, OVS lock plus RCU, or OVS lock only.

## State and Persistence

The declared state is runtime-only. `datapath` holds flow table, ports, stats, namespace, user features, max headroom, meters, and upcall pids. `ovs_net` holds per-net datapath list and maintenance work. `ovs_pcpu_storage` holds action recursion/defer state and fragmentation scratch used by `actions.c`.

## Dependencies and Integration Points

It includes conntrack, flow, flow table, meter, internal dev, skb, netdevice, and tunnel headers. It is included by most OVS implementation files and by notifier/action paths.

## Risks and Edge Cases

`OVS_CB()` overlays skb control buffer, so `datapath.c` enforces size at module init. Locking annotations must match call sites to avoid RCU misuse. The `OVS_MASKED` macro assumes the supplied key has no bits outside the mask. Per-CPU storage is shared by action recursion and fragmentation, so callers must respect execution context locking.

## Test Signals

Compile-time and lockdep coverage are important. Runtime tests should stress vport lookup during concurrent deletion, datapath namespace teardown, skb control block usage with GSO, action recursion, and per-CPU upcall PID access.
