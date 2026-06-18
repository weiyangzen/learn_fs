
# sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_inet.c

Purpose: Registers nftables flowtable types for IPv4, IPv6, and mixed `NFPROTO_INET`, and provides the mixed-family hook dispatcher.

Important APIs and functions: `nf_flow_offload_inet_hook()` decodes the packet L2/encapsulation protocol from `skb->protocol`, VLAN, or PPPoE and dispatches to `nf_flow_offload_ip_hook()` or `nf_flow_offload_ipv6_hook()`. `nf_flow_rule_route_inet()` dispatches hardware rule construction to IPv4 or IPv6 route-action builders. Static `nf_flowtable_type` instances wire `.init`, `.setup`, `.action`, `.free`, and `.hook` into nftables.

Control flow: module init registers IPv4, IPv6, then inet flowtable types; exit unregisters in reverse. Runtime packets enter the configured flowtable hook, protocol detection peels one VLAN/PPPoE classification layer, then the family-specific datapath handles lookup and forwarding.

State and persistence: The file itself stores only static type descriptors. Real table state is allocated by `nf_flow_table_core.c`. No persistent state exists beyond registration lifetime.

Dependencies and integration: Integrates nftables flowtable registration with the family-specific hooks in `nf_flow_table_ip.c`, route rule builders in `nf_flow_table_offload.c`, and table lifecycle helpers in `nf_flow_table_core.c`.

Risks: Misclassification of VLAN/PPPoE packets leads to missed offload rather than packet corruption because unknown protocols return `NF_ACCEPT`. Test signals include module alias loading for AF_INET/AF_INET6/NFPROTO_INET, IPv4/IPv6 dispatch under VLAN and PPPoE, and unregister behavior with active nftables flowtable configurations.
