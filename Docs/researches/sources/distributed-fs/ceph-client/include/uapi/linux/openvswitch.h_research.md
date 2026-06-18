# sources/distributed-fs/ceph-client/include/uapi/linux/openvswitch.h

Purpose: Defines the Generic Netlink ABI for the in-kernel Open vSwitch datapath, including datapaths, packets, vports, flows, flow keys, actions, meters, and conntrack limits.

Important APIs/types/functions: Exports family names and versions for datapath, packet, vport, flow, meter, and conntrack-limit operations. Core layouts include `struct ovs_header`, `ovs_dp_stats`, `ovs_dp_megaflow_stats`, `ovs_vport_stats`, `ovs_flow_stats`, flow key structs for Ethernet, VLAN/MPLS, IPv4/IPv6, TCP/UDP/SCTP/ICMP/ARP/ND, conntrack tuples/labels, tunnel metadata, NSH keys, and action payloads such as VLAN/MPLS push, hash, truncation, CT/NAT, clone/sample/check-packet-length, decrement TTL, and psample.

Control flow: Userspace creates a datapath, adds vports, receives packet miss/action upcalls, installs or deletes flows with nested key/mask/action attributes, and queries stats/meters/limits. Packet execution applies nested `OVS_ACTION_ATTR_*` lists. Conntrack and NAT actions alter tracking state, recirculation restarts matching with a new ID, and meters enforce configured rate bands.

State and persistence behavior: Runtime state lives in the kernel datapath: flow tables, mask caches, megaflow stats, vport stats, upcall PID arrays, meters, conntrack limits, and per-flow actions. The header defines the wire format for creating, querying, and mutating that state; nothing is durable across module unload or datapath deletion unless userspace reconstructs it.

Dependencies and integration points: Depends on `<linux/types.h>` and `<linux/if_ether.h>`. Integrates with Open vSwitch userspace daemons, Generic Netlink policy parsing, tunnel drivers, conntrack/netfilter, tc offload, psample, and network namespaces.

Risks: This ABI is deeply nested and backward compatibility is critical. Attribute type squatting, in-kernel-only enum members under `__KERNEL__`, alignment, mask/value pairing, endian-marked fields, tunnel option lengths, NAT/CT semantics, and upcall PID routing all create compatibility and security risk. Malformed netlink attributes must not lead to out-of-bounds parsing or unintended packet mutation.

Test signals: Run OVS datapath selftests, create/delete datapaths and vports, install flows with masks and all major key families, exercise tunnel metadata, CT/NAT, clone/sample/meter/psample/dec-ttl actions, fuzz malformed netlink attributes, and verify old userspace continues to work with new kernels.
