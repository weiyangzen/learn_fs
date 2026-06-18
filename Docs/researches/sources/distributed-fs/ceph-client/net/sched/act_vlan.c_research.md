# sources/distributed-fs/ceph-client/net/sched/act_vlan.c

## Purpose

`act_vlan.c` implements tc VLAN and Ethernet header manipulation actions: pop VLAN, push VLAN, modify VLAN tag, pop Ethernet header, and push Ethernet header.

## Important APIs, types, and functions

`tcf_vlan_init()` parses `TCA_VLAN_*`, validates action-specific required attributes, creates an RCU `tcf_vlan_params`, and installs control action state. `tcf_vlan_act()` executes skb VLAN/Ethernet helpers. `tcf_vlan_dump()` reports current parameters. `tcf_vlan_offload_act_setup()` maps actions to `FLOW_ACTION_VLAN_*` entries, including push/pop Ethernet.

## Control flow

Init accepts pop without extra fields; push/modify require VLAN ID, validate VID range, default protocol to 802.1Q, and allow only 802.1Q or 802.1AD protocols; push_eth requires source and destination MAC addresses. Runtime pushes the MAC header for ingress before using VLAN helpers. Modify is a no-op if no VLAN tag exists; otherwise it extracts an accelerated or in-payload tag, changes VID and optionally priority, then stores the tag as hardware-accelerated metadata. It restores ingress data position, resets MAC length, and returns the configured action.

## State and persistence

Persistent state is an RCU params block containing VLAN action, VID, priority, priority-exists flag, protocol, optional push_eth MACs, and control action. Stats are common tc action counters. Old params are RCU-freed on replace or cleanup.

## Dependencies and integration points

It depends on Linux VLAN skb helpers, Ethernet push/pop helpers, tc action infrastructure, and flow offload. The action is commonly paired with flower filters and hardware offload drivers.

## Risks and edge cases

Ingress header push/pull must be balanced. Modify behavior differs for accelerated versus in-payload tags and silently no-ops on untagged packets. VLAN ID range and protocol validation protect UAPI misuse. Offload must preserve priority existence semantics, especially for modify.

## Test signals

Test pop, push, modify with and without existing tags, hardware-accelerated tags, push_eth/pop_eth, ingress and egress paths, invalid VID/protocol/missing MACs, dump round trips, qstats on helper failure, and offload action mapping.
