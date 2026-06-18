# sources/distributed-fs/ceph-client/net/ipv6/mip6.c

Purpose: Implements Mobile IPv6 route-optimization support as XFRM extension-header types plus a raw IPv6 Mobility Header filter.

Important APIs/types/functions: Key functions are `mip6_mh_filter`, `mip6_destopt_{input,output,reject,init_state,destroy}`, `mip6_rthdr_{input,output,init_state,destroy}`, and module init/exit. It registers two `struct xfrm_type` instances for `IPPROTO_DSTOPTS` and `IPPROTO_ROUTING`, and registers the rawv6 mobility-header filter with `rawv6_mh_filter_register`.

Control flow: The MH filter validates the fixed mobility header, rejects too-short type-specific messages, and requires `ip6mh_proto == IPPROTO_NONE`, sending ICMPv6 parameter problems for protocol violations. Destination-option output inserts a Home Address Option and rewrites the IPv6 source to the care-of address from `xfrm_state`. Routing-header output inserts Routing Header type 2 and rewrites destination to the care-of address. Input paths verify that packet source/destination matches the XFRM co-address unless the co-address is unspecified. The reject path rate-limits `km_report` notifications and skips MH flows.

State and persistence: Persistent state is limited to XFRM states owned externally and a static spinlock-protected `mip6_report_rate_limiter` keyed by timestamp, interface, source, and destination. Header length is stored in `x->props.header_len`.

Dependencies/integration: Depends on XFRM, raw IPv6 sockets, ICMPv6, Mobile IPv6 structures, and kernel migration reporting. Module aliases expose the XFRM types.

Risks and test signals: Risks include skb header-offset assumptions during push/rewrite, co-address locking, incorrect padding/alignment for HAO, and rate-limiter over/under-suppression. Tests should exercise XFRM state init rejection for nonzero SPI or wrong mode, outbound HAO and RH2 packet formatting, inbound co-address mismatch, malformed MH lengths/proto fields, and unload cleanup ordering after partial registration failures.
