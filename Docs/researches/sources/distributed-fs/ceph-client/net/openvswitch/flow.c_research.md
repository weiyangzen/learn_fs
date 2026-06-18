# sources/distributed-fs/ceph-client/net/openvswitch/flow.c

## Purpose
`flow.c` extracts kernel `sk_buff` packets into `struct sw_flow_key`, and maintains per-flow packet, byte, last-used, and TCP flag statistics. It is the parser between raw ingress packets or userspace-supplied packets and the datapath's flow table key representation.

## Important APIs, Types, and Functions
`ovs_flow_used_time()` converts a stored jiffies timestamp into an approximate millisecond wall-clock used time. `ovs_flow_stats_update()`, `ovs_flow_stats_get()`, and `ovs_flow_stats_clear()` manage per-CPU `struct sw_flow_stats` entries allocated by `flow_table.c`.

The packet parsing core is `key_extract()`, which prepares skb header offsets, handles Ethernet or L3-only packets through `mac_proto`, parses outer and inner VLAN tags, determines EtherType or 802.2 framing, and delegates to `key_extract_l3l4()`. `key_extract_l3l4()` fills IPv4, IPv6, ARP/RARP, MPLS, NSH, and transport fields. It treats later IP fragments as having no transport key, records first fragments, handles UDP GSO as first fragments, extracts TCP flags with `TCP_FLAGS_BE16()`, and maps ICMP/ICMPv6 type/code into the transport source/destination fields.

IPv6 parsing is split across `get_ipv6_ext_hdrs()` and `parse_ipv6hdr()`. The former records OpenFlow IPv6 extension header pseudo-field bits, including repeated or unexpected sequence flags. The latter uses `ipv6_find_hdr()` to locate the transport header and handles fragment state. `parse_icmpv6()` additionally extracts neighbor discovery target and link-layer options, with duplicate option detection that clears invalid ND fields. `parse_nsh()` validates NSH version and metadata type and copies MD type 1 context.

Public extraction entry points are `ovs_flow_key_update_l3l4()`, `ovs_flow_key_update()`, `ovs_flow_key_extract()`, and `ovs_flow_key_extract_userspace()`. `ovs_flow_key_extract()` adds tunnel metadata, ingress port, skb priority, mark, optional TC skb extension recirc and post-conntrack state, then fills conntrack fields via `ovs_ct_fill_key()`. `ovs_flow_key_extract_userspace()` parses key metadata from netlink before parsing the packet payload and validates conntrack original-tuple placement.

## Control Flow
Ingress vports call `ovs_vport_receive()`, which stores the input vport in `OVS_CB(skb)` and calls `ovs_flow_key_extract()`. Extraction first initializes tunnel and physical metadata, derives `mac_proto` from `skb->dev->type`, then parses L2/L3/L4. On success, conntrack metadata is appended and datapath lookup can proceed. For userspace packet execute, netlink key attributes provide metadata first, then `key_extract()` reads packet headers.

## State and Persistence
The file does not own persistent datapath objects, but it mutates skbs while parsing: it pulls/pushes Ethernet/VLAN bytes, sets mac/network/transport header offsets, updates `skb->protocol`, may pop non-accelerated VLAN tags into hw-accelerated skb tags, and may linearize ICMPv6 ND packets. Flow stats are per-flow persistent counters protected by spinlocks and RCU pointers; CPU-specific stats are allocated lazily after contention on the preallocated CPU 0 stats slot.

## Dependencies and Integration Points
It depends on kernel network header helpers, VLAN, MPLS, IPv6, NSH, tunnel metadata, TC skb extensions, and OVS `conntrack.h`, `datapath.h`, `flow_netlink.h`, and `vport.h`. Its output layout must match `flow.h`, `flow_table.c`, and `flow_netlink.c`, because masked lookup and netlink serialization compare and encode byte ranges of `struct sw_flow_key`.

## Risks
Parser correctness is security-sensitive because malformed packets can drive skb pulls, header offset changes, and key fields used for matching. Important risks include incomplete header handling, VLAN double-tag corner cases, truncated headers producing wildcard-like zero fields, IPv6 extension sequencing compatibility, NSH length validation, and userspace metadata that overlaps with packet-derived fields. Stats paths must maintain lock/RCU discipline and avoid allocation in hot paths except the intended best-effort per-CPU allocation.

## Test Signals
Good coverage includes packet-in tests for Ethernet, L3-only, VLAN and QinQ, 802.2, IPv4 and IPv6 fragments, TCP/UDP/SCTP/ICMP, ARP/RARP, MPLS stacks, NSH MD1/MD2 rejection, tunnel metadata extraction, TC recirc/post-CT metadata, userspace packet execute keys, and flow stat aggregation/clear under multiple CPUs.
