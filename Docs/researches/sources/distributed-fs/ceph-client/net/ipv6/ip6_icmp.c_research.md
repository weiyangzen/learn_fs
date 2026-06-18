# sources/distributed-fs/ceph-client/net/ipv6/ip6_icmp.c

Purpose: provides `icmpv6_ndo_send()` for network-device style IPv6 ICMP error sending when NAT connection tracking may require source-address restoration.

Important APIs, types, and functions: `icmpv6_ndo_send()` is exported when IPv6 and NF NAT are enabled. It uses `nf_ct_get()`, conntrack NAT status, `skb_clone()`, `skb_ensure_writable()`, and `icmp6_send()`.

Control flow: if no conntrack entry exists or NAT is not active, the helper sends ICMPv6 directly. For NATed packets it clones shared skbs, validates that the IPv6 header is writable and in bounds, temporarily replaces the source address with the original conntrack tuple source for the packet direction, sends ICMPv6, restores the address, and consumes any clone.

State and persistence: no persistent state. It temporarily mutates an skb IPv6 source address and restores it before return.

Dependencies and integration points: used by tunnel/device transmit paths that need ICMPv6 errors in ndo context. Integrates with nf_conntrack/NAT and core ICMPv6 send logic.

Risks: compiled only under `CONFIG_IPV6` and `CONFIG_NF_NAT`; callers need fallback awareness when unavailable. Writable-header checks must remain strict to avoid corrupting malformed skbs. Temporary header mutation makes clone/writeability correctness critical.

Test signals: NATed tunnel PMTU/error generation, non-NAT direct ICMPv6 send, shared skb clone path, malformed/truncated skb rejection, and build matrix with NAT enabled/disabled.
