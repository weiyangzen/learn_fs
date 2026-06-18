# sources/distributed-fs/ceph-client/net/openvswitch/flow.h

## Purpose
`flow.h` defines the in-kernel Open vSwitch flow key, mask, identifier, action, statistics, and flow object contracts. It is the shared ABI inside the OVS kernel module between packet parsing, netlink conversion, flow table lookup, action execution, conntrack, and vport receive paths.

## Important APIs, Types, and Functions
`enum sw_flow_mac_proto` distinguishes L3-only packets from Ethernet-framed packets and reserves `SW_FLOW_KEY_INVALID` as a high-bit validity marker. `enum ofp12_ipv6exthdr_flags` mirrors OpenFlow IPv6 extension header bits.

`struct sw_flow_key` is the central match key. It includes tunnel metadata and variable tunnel options, physical metadata (`priority`, `skb_mark`, `in_port`), `mac_proto`, tunnel address family, datapath hash, recirculation id, Ethernet addresses and two VLAN headers, conntrack state, IP common fields, L4 ports and TCP flags, IPv4/IPv6/ARP/ND/MPLS/NSH unions, and conntrack original tuple fields. Alignment is enforced so masked comparisons can operate on longs. `TUN_METADATA_OFFSET()` and `TUN_METADATA_OPTS()` store short tunnel options at the end of the fixed array so variable-length options can be matched efficiently.

`struct sw_flow_mask`, `struct sw_flow_match`, and `struct sw_flow_key_range` describe byte ranges of the key that are significant for lookup. `struct sw_flow_id` is either a UFID or an allocated unmasked key pointer. `struct sw_flow_actions` holds an RCU-freed netlink action blob. `struct sw_flow_stats` and `struct sw_flow` define flow counters, per-CPU stats pointers, mask pointer, action pointer, flow-table hash nodes, and optional UFID hash nodes.

Inline helpers include `sw_flow_key_is_nd()`, `ovs_key_mac_proto()`, `ovs_mac_header_len()`, `ovs_identifier_is_ufid()`, and `ovs_identifier_is_key()`. Public functions declare stats operations and packet/user key extraction.

## Control Flow and Integration
Most OVS modules include this header. `flow.c` fills `sw_flow_key`, `flow_netlink.c` parses and emits it, `flow_table.c` masks and hashes it, `datapath.c` stores flows and actions, and action/conntrack code updates or consumes fields during recirculation.

## State and Persistence
The structures in this header are runtime state, not disk persistence. However, their binary layout is crucial inside the module: mask ranges, hashing, and comparisons assume stable offsets and long alignment. The UFID/key choice changes ownership: key identifiers allocate and free an unmasked key, while UFIDs store bytes inline.

## Dependencies
It depends on Linux netlink, Open vSwitch UAPI, tunnel metadata, destination metadata, NSH, cpumasks, RCU, and common network protocol headers.

## Risks
Changing `struct sw_flow_key` layout affects hashing, mask range generation, netlink conversion, and action validation. Overlapping union fields, especially ND versus conntrack original IPv6 tuple, require strict validation. Tunnel option length and placement must remain synchronized with tunnel netlink parsing.

## Test Signals
Build-time `BUILD_BUG_ON()` checks in `flow_table.c`, flow insertion/lookup tests with masks over every key family, netlink round-trip tests, and packet extraction tests are the main signals that this contract remains correct.
