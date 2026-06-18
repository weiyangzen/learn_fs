# sources/distributed-fs/ceph-client/net/openvswitch/actions.c

## Purpose

This file is the Open vSwitch datapath action executor. It applies validated netlink action lists to skbs, including output, userspace upcalls, packet header mutation, tunnel metadata, VLAN/MPLS/Ethernet/NSH encapsulation, conntrack, metering, sampling, cloning, recirculation, packet length branching, TTL decrement, drop, and psample.

## Important APIs, Types, and Functions

The exported entry point is `ovs_execute_actions()`. It manages recursion depth in per-CPU `ovs_pcpu_storage`, calls `do_execute_actions()`, and drains deferred actions at top level. `do_execute_actions()` is the central action switch. Header mutation helpers include `push_mpls()`, `pop_mpls()`, `set_mpls()`, `push_vlan()`, `pop_vlan()`, `set_eth_addr()`, `push_eth()`, `pop_eth()`, `push_nsh()`, `pop_nsh()`, `set_ipv4()`, `set_ipv6()`, `set_udp()`, `set_tcp()`, and `set_sctp()`.

Action composition helpers include `clone_execute()`, `sample()`, `clone()`, `execute_recirc()`, `execute_check_pkt_len()`, and `process_deferred_actions()`. Output helpers include `do_output()`, `ovs_fragment()`, `prepare_frag()`, `ovs_vport_output()`, and `output_userspace()`.

## Control Flow

`ovs_execute_actions()` increments execution level, rejects excessive recursion, records original action length, and dispatches each action. Last output-like actions consume the skb directly; non-last output actions clone it. Packet mutations update checksums, skb hash, conntrack state, and the cached `sw_flow_key` when possible. Encapsulation changes invalidate the cached flow key so later recirculation recomputes it.

Recirculation and nested clone/sample/check-packet-length actions either execute immediately using cloned per-CPU flow keys or enqueue a `deferred_action` when nesting exceeds available key slots. Top-level execution drains the FIFO afterward. Conntrack actions ensure the flow key is current, call `ovs_ct_execute()`, and hide stolen fragments by mapping `-EINPROGRESS` to success.

## State and Persistence

State is per packet (`skb`, `OVS_CB`, `sw_flow_key`) and per CPU (`exec_level`, deferred action FIFO, cloned keys, fragmentation scratch). There is no durable storage. Packet output can change device state only through vport send paths outside this file.

## Dependencies and Integration Points

The executor depends on `datapath.h`, flow key helpers, vports, meters, conntrack, NSH, MPLS, GSO/fragmentation, checksum helpers, psample, and OVS tracepoints. It is called from datapath packet hits and userspace packet execute commands.

## Risks and Edge Cases

Action ordering and skb ownership are critical: many actions consume or free the skb on last action or error. Header mutations must keep checksums and cached keys consistent. Deferred action FIFO and recursion limits prevent unbounded nested clone/recirc but can drop packets. Fragmentation reconstructs L2 state from per-CPU scratch and must not exceed `MAX_L2_LEN`. Conntrack clearing on address/port changes avoids stale `_nfct`.

## Test Signals

High-value tests cover every action type, nested clone/sample/recirc limits, key invalidation and recomputation, checksum correctness after masked sets, conntrack interactions after NAT or address mutation, output truncation/cutlen, MRU fragmentation paths, TTL exception actions, psample metadata, and packet ownership on error paths.
