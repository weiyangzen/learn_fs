<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mpls/mpls_iptunnel.c -->
# sources/distributed-fs/ceph-client/net/mpls/mpls_iptunnel.c

## Purpose
Implements MPLS lightweight tunnel encapsulation for IP routes. It parses MPLS tunnel netlink attributes, builds `lwtunnel_state`, pushes MPLS labels during route transmit, handles TTL propagation/default TTL policy, emits tunnel state back to netlink, and registers the MPLS lwtunnel ops.

## Important APIs, Types, and Functions
`mpls_xmit()` is the lwtunnel transmit hook. `mpls_build_state()` parses `MPLS_IPTUNNEL_DST` and optional `MPLS_IPTUNNEL_TTL` into `struct mpls_iptunnel_encap`. `mpls_fill_encap_info()`, `mpls_encap_nlsize()`, and `mpls_encap_cmp()` support route dump/compare. `mpls_iptun_ops` registers the lwtunnel methods with `lwtunnel_encap_add_ops()`.

## Control Flow
Netlink build validates the nested policy, requires a destination label stack, counts labels using `nla_get_labels()`, allocates enough state for the variable label array, fills labels, and sets TTL propagation mode. Transmit resolves the output device from `skb_dst()`, rejects unsupported devices or LRO, chooses TTL from IPv4 TTL, IPv6 hop limit, per-lwt default, or namespace default according to propagation settings, checks MPLS MTU after label insertion, ensures headroom, records inner protocol/network header, pushes labels with BOS on the bottom entry, updates stats, then sends through ARP or ND depending on IPv4/IPv6 route gateway details including 6PE v4-mapped IPv6 gateways.

## State and Persistence
Per-route tunnel state is stored in `lwtunnel_state` with variable-length `mpls_iptunnel_encap`: labels, default TTL, and TTL propagation mode. The file itself has no global mutable state beyond the registered lwtunnel ops. Runtime stats are updated on the output MPLS device or IP counters through helpers in `af_mpls.c`.

## Dependencies and Integration Points
Depends on lwtunnel infrastructure, route and destination entries, IPv4/IPv6 routing structs, neighbor transmit, MPLS label netlink helpers, output feasibility/MTU/stats helpers, and UAPI MPLS tunnel attributes. It integrates with `ip route ... encap mpls ...` user operations and soft-depends on `mpls_gso` for offload support.

## Risks
Transmit assumes `dst->ops->family` is AF_INET or AF_INET6 and that route gateway fields match the selected neighbor table. TTL behavior has three layers of policy and can regress interoperability if default and propagate cases are mixed. MTU checking subtracts label stack size from device MTU and must stay aligned with GSO validation. Netlink state comparison must include labels, TTL mode, and default TTL or route deduplication can be wrong.

## Test Signals
Signals include adding IPv4 and IPv6 routes with MPLS encap, routes with TTL 0 versus fixed TTL, multi-label stacks, route dumps preserving labels and TTL, MTU exceeded drops, output to down/non-MPLS devices, ARP/ND/6PE gateway transmit, and packet captures confirming BOS and label order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mpls/mpls_iptunnel.c -->
