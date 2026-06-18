# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_eui64.c

Purpose: Implements the IPv6 xtables `eui64` match, checking whether the IPv6 source interface identifier corresponds to the Ethernet source MAC converted to EUI-64.

Important APIs/types/functions: Uses `eui64_mt6`, Ethernet header helpers, `ARPHRD_ETHER`, `ETH_P_IPV6`, and a single `xt_match`.

Control flow: Runtime requires an Ethernet device, a present MAC header at least `ETH_HLEN`, and IPv6 ethertype/version. It builds the EUI-64 identifier by inserting `ff:fe` and toggling the universal/local bit, then compares against the low 64 bits of the IPv6 source address.

State and persistence: Stateless.

Dependencies/integration: Valid only on pre-routing/local-in/forward hooks where the ingress L2 header is available.

Risks and test signals: Risks are hotdropping skbs with missing MAC headers, use on non-Ethernet devices, and behavior after L2 header stripping. Tests should cover Ethernet match/mismatch, non-Ethernet devices, short MAC headers, and hook placement.
