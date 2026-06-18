# sources/distributed-fs/ceph-client/include/net/ip_tunnels.h

Purpose: Provides generic IP tunnel types and helpers for IPv4-based tunnels and metadata/lwtunnel users, shared by GRE, SIT, VTI, ERSPAN, FOU/GUE, and tunnel offload paths.

Important APIs/types/functions: `ip_tunnel_key` stores tunnel id, IPv4/IPv6 endpoints, bitmap flags, label, nhid, TOS/TTL, transport ports, and flow flags. `ip_tunnel_info` wraps key, encapsulation, optional dst cache, mode, and options. `ip_tunnel`, `ip_tunnel_net`, `tnl_ptk_info`, and `ip_tunnel_parm_kern` define netdev tunnel state, per-net tunnel tables, parsed packet info, and kernel-side config. Helpers convert flags to/from legacy `__be16`, initialize keys/flows, test metadata/dst-cache usability, and copy options.

Control flow: Transmit code initializes `flowi4`, optionally builds an encapsulation header via RCU registered `iptun_encaps`, handles offloads, pulls headers, checks PMTU, and updates per-cpu tx stats. Receive helpers validate/pull IP headers, prepare VLAN/inner protocol offsets, and feed generic tunnel receive.

State and persistence: Runtime state includes tunnel hash tables, fallback and collect-metadata devices, dst caches, PRL entries, error timestamps/counts, sequence counters, ERSPAN fields, 6rd parameters, GRO cells, fwmark, collect-md, and ignore-DF. Static key `ip_tunnel_metadata_cnt` tracks metadata users.

Dependencies/integration: Uses netdevice, sk_buff, flow, DSCP/ECN, lwtunnel, dst cache, rtnetlink, gro cells, L3 master devices, optional IPv6 route helpers, page/offload APIs, and netns generic IDs.

Risks: Tunnel recursion is deliberately lower than generic xmit recursion due to stack usage; option flag bitmap/legacy conversion must preserve UAPI behavior; headroom is capped to avoid skb offset overflow; GSO encapsulation bits must be cleared correctly. Test signals include netlink create/change/delete, collect metadata, encap operation registration, PMTU replies, VLAN inner protocol pull, stats for success/error/drop, IPv4/IPv6 inner DS field inheritance, and offload/GSO paths.
