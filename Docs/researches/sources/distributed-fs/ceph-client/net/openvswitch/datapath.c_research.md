# sources/distributed-fs/ceph-client/net/openvswitch/datapath.c

## Purpose

This file is the main Open vSwitch kernel datapath implementation. It registers OVS generic-netlink families, owns datapath/vport/flow/packet command handlers, processes packets through flow lookup and action execution, sends upcalls to userspace, manages per-net datapath lifecycle, and initializes/cleans up the module.

## Important APIs, Types, and Functions

Global exports include `ovs_lock()`, `ovs_unlock()`, `lockdep_ovsl_is_held()`, `ovs_dp_name()`, `ovs_lookup_vport()`, `ovs_dp_detach_port()`, `ovs_dp_process_packet()`, `ovs_dp_upcall()`, `ovs_dp_get_upcall_portid()`, and `ovs_vport_cmd_build_info()`. Generic-netlink families cover datapaths (`OVS_DATAPATH_FAMILY`), vports (`OVS_VPORT_FAMILY`), flows (`OVS_FLOW_FAMILY`), packets (`OVS_PACKET_FAMILY`), meters, and optional CT limits.

Major command handlers include `ovs_packet_cmd_execute()`, `ovs_flow_cmd_new/set/get/del/dump()`, `ovs_dp_cmd_new/set/get/del/dump()`, and `ovs_vport_cmd_new/set/get/del/dump()`. Lifecycle functions include `ovs_init_net()`, `ovs_exit_net()`, `dp_init()`, and `dp_cleanup()`.

## Control Flow

Packet receive enters `ovs_dp_process_packet()` with an extracted key and input vport. It looks up the flow table with stats, sends a miss upcall if no flow exists, or updates flow stats and executes actions on hit. Upcalls use `queue_userspace_packet()` or `queue_gso_packets()` to build `OVS_PACKET_ATTR_*` netlink messages, include key, userdata, actions, MRU, hash, and packet bytes, then unicast to the selected handler port.

Control-plane netlink commands run under `ovs_mutex` for mutations and RCU for dumps/lookups. Flow commands parse keys/masks/actions, update the flow table, support UFIDs, optionally clear stats, and notify listeners. Datapath commands create/destroy datapaths with local vports, stats, flow tables, meters, user features, and per-CPU upcall portids. Vport commands add/remove/configure ports, update datapath headroom, and report vport stats/options.

Module init allocates per-CPU storage, registers internal device links, flow/vport subsystems, per-net ops, netdevice notifier, netdev vports, generic-netlink families, and drop reasons. Cleanup unregisters in reverse and waits for RCU callbacks.

## State and Persistence

Runtime state includes per-net `struct ovs_net`, each `struct datapath`, flow tables, vport hash buckets, meters, per-CPU stats, RCU-protected per-CPU upcall pid arrays, mask rebalance delayed work, and per-CPU action storage. There is no durable persistence; userspace recreates datapaths and flows.

## Dependencies and Integration Points

This file integrates generic netlink, net namespaces, vport providers, flow parsing/table code, action execution, meters, conntrack init/exit, netdevice notifiers, tc skb extensions, and drop reason infrastructure. Userspace `ovs-vswitchd` controls it through the registered netlink families.

## Risks and Edge Cases

Locking is central: writes use `ovs_mutex`, reads use RCU, and RT packet recursion uses local locks. Upcall loss increments `n_lost`; handler portid zero drops. VLAN accelerated packets are cloned and pushed inside for userspace visibility. Feature negotiation can reset unsupported user features for old userspace. Datapath destruction must remove non-local vports before local port and flush flows before RCU free.

## Test Signals

Tests should cover packet miss/hit stats, upcall message contents, GSO segmentation upcalls, packet execute, flow add/update/delete/dump with UFID flags, datapath create/set/delete/dump, vport create/set/delete/dump, per-CPU upcall PID dispatch, mask cache resizing, namespace teardown, module init cleanup failures, and concurrent flow/vport mutations under traffic.
