# sources/distributed-fs/ceph-client/include/net/ip6_tunnel.h

Purpose: Provides the shared IPv6 tunnel object model and encapsulation hooks for IP6 tunnel drivers, including GRE-specific sequence/header fields and metadata/dst cache support.

Important APIs/types/functions: `__ip6_tnl_parm` contains tunnel name, link, protocol, encapsulation limit, hop limit, collect-metadata mode, flowinfo, local/remote IPv6 endpoints, input/output flags and keys, fwmark, and ERSPAN fields. `ip6_tnl` binds parameters to a netdev, net namespace, flow template, dst cache, GRO cells, error state, GRE sequence state, header lengths, encapsulation parameters, and master link. `ip6_tnl_encap_ops` registers optional FOU/GUE-style encapsulation callbacks. APIs cover encapsulation registration/setup, receive/transmit admission, receive, transmit, TLV parsing, capability detection, link-net/iflink lookup, MTU changes, and `ip6tunnel_xmit`.

Control flow: Transmit checks recursion depth, clears IPv6 skb control block, sets flags, calls `ip6_local_out`, then records tunnel tx stats. Optional encapsulation looks up `ip6tun_encaps[type]` under RCU and invokes `encap_hlen` or `build_header`.

State and persistence: Tunnel state lives in per-net tunnel lists via `next`, netdev-private `ip6_tnl`, dst cache, GRO cells, error counters with timestamps, seqno atomics, and encapsulation configuration. It is volatile runtime configuration bound to netlink/device lifecycle.

Dependencies/integration: Uses generic `ip_tunnels.h`, IPv6 route/output, dst cache, GRO cells, netdevice trackers, and optional `CONFIG_INET`.

Risks: Recursion-loop protection is critical; RCU encapsulation operations must tolerate unregister races; MTU/headroom changes can break PMTU; sequence fields are GRE-only and must not be misused by other tunnel types. Test signals include tunnel xmit recursion drops, encap add/delete races, metadata collect mode, PMTU/MTU changes, GRE ERSPAN fields, and IPv6 tunnel receive capability filtering.
