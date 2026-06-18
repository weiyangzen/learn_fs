# sources/distributed-fs/ceph-client/Documentation/netlink/specs/ovs_flow.yaml

Purpose: specifies the legacy Generic Netlink schema for Open vSwitch flow lookup and creation within an OVS datapath.

Important APIs/types/functions: protocol is `genetlink-legacy`, UAPI header `linux/openvswitch.h`, operation prefix `ovs-flow-cmd-`, fixed header `ovs-header`. Definitions model OVS flow stats, packet key structs for Ethernet/MPLS/IPv4/IPv6/TCP/UDP/SCTP/ICMP/ARP/ND/conntrack tuples, fragment enum, UFID flags, VLAN/MPLS/hash action structs, hash algorithm enum, and conntrack state flags. Attribute sets include `flow-attrs`, `key-attrs`, `action-attrs`, tunnel key attrs, packet-length check attrs, sample/userspace attrs, NSH attrs, conntrack/NAT attrs, TTL decrement attrs, VXLAN extensions, and psample attrs.

Control flow: `get` supports do and dump. Requests can identify flows by parsed key, UFID, and UFID flags; replies include key, UFID, mask, stats, and actions. `new` installs a flow using key, UFID, mask, and actions. The schema models recursive/nested action and key structures: encapsulation nests keys, actions can set keys, sample nested actions, perform conntrack/NAT, output/userspace, VLAN/MPLS/ETH push/pop, tunnel operations, packet length branching, TTL decrement, and psample.

State and persistence: flow entries, masks, actions, stats, and last-used timestamps live in the OVS kernel datapath. They are runtime forwarding state and are usually controlled by OVS userspace; they do not persist across datapath deletion, module unload, or reboot unless recreated.

Dependencies and integration points: integrates with OVS datapath netlink, flow miss/upcall handling, tunnel metadata, conntrack, NAT, NSH, VXLAN, psample, and userspace daemons that program datapath flows. It shares `ovs-header` with the datapath family.

Risks: recursive keys and actions are complex and easy to encode incorrectly. Binary structs must match `linux/openvswitch.h` layout and endian expectations. Flow masks must align with keys; bad masks can cause incorrect matching or kernel rejection. Action lists can contain nested actions and side effects such as conntrack commit and NAT. Only `get` and `new` are modeled here, so modify/delete behavior is outside this partial spec.

Test signals: generate and parse representative L2/L3/L4 keys, UFID lookup, masked flow creation, action-list nesting, tunnel and conntrack/NAT attrs, stats decoding after traffic, dump behavior, and rejection of malformed recursive nests.
