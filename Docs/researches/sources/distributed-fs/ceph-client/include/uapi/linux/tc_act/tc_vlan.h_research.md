# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_vlan.h

## Purpose
Defines the TC VLAN action ABI for popping, pushing, modifying, and Ethernet push/pop variants.

## Important APIs, Types, and Constants
Actions include `TCA_VLAN_ACT_POP`, `TCA_VLAN_ACT_PUSH`, `TCA_VLAN_ACT_MODIFY`, `TCA_VLAN_ACT_POP_ETH`, and `TCA_VLAN_ACT_PUSH_ETH`. `struct tc_vlan` embeds `tc_gen` and `v_action`. Attributes include VLAN ID, protocol, priority, Ethernet destination/source for push-eth, timing, parameters, and padding.

## Control Flow, State, and Persistence
Runtime action mutates VLAN/Ethernet headers according to configured action and records counters. Configuration persists as TC action state.

## Dependencies and Integration Points
Depends on `<linux/pkt_cls.h>`. Integrates with VLAN-aware TC pipelines and hardware offload.

## Risks and Test Signals
Risks include invalid VLAN ID/priority, protocol mismatch, and push/pop on packets without expected headers. Test all actions, boundary IDs, QinQ-like protocols, packet capture, and offload dump behavior.
