# sources/distributed-fs/ceph-client/net/ipv4/ip_forward.c

Purpose: implements IPv4 packet forwarding after routing has selected an output route. It enforces forwarding policy, TTL, strict source-route rules, PMTU/DF behavior, redirect generation, priority updates, netfilter forwarding hooks, and final output.

Important APIs/functions: central public entry point is `ip_forward(struct sk_buff *skb)`. Helpers are `ip_exceeds_mtu()` and `ip_forward_finish()`. Key types are `struct sk_buff`, `struct iphdr`, `struct rtable`, `struct ip_options`, `struct net`, and `struct dst_entry`.

Control flow: `ip_forward()` drops non-host packets, skb-owned packets, LRO packets, and packets failing XFRM forward policy. Router-alert packets are handed to `ip_call_ra_chain()`. The function updates checksums for forwarding, rejects TTL <= 1 with ICMP time exceeded, validates XFRM route forwarding, rejects strict source-route packets whose route uses a gateway, increments forwarding stats, and records `IPSKB_FORWARDED`. It computes forward MTU and, if DF/GSO rules require, sends ICMP fragmentation-needed and drops. Before changing the packet it copies writable headroom with `skb_cow()`, decrements TTL, sends redirects when requested and safe, optionally maps TOS to priority, then invokes the `NF_INET_FORWARD` hook. `ip_forward_finish()` applies forward options, clears timestamps, handles switchdev offload-consumed packets, and calls `dst_output()`.

State and persistence: no long-lived state is created; the function mutates per-packet skb/IPCB fields, TTL, checksum, priority, timestamps, and statistics. It depends on route state already attached to the skb and may emit ICMP side effects. Net namespace sysctl `ip_fwd_update_priority` affects priority mutation.

Dependencies and integration: sits between `ip_input` route resolution and `dst_output`, and integrates with XFRM, netfilter IPv4 forwarding, routing/PMTU, ICMP, source-route option handling, switchdev L3 forwarding offload, and IP statistics.

Risks: MTU/DF logic must preserve RFC behavior for fragments, GSO, `ignore_df`, and `frag_max_size`; mistakes can blackhole PMTU discovery or forward oversize packets. The packet must be copied writable before TTL/checksum mutation. Router-alert and source-route behavior intersects with security policy. Redirect generation must not run for source-routed or IPsec path packets.

Test signals: forwarding selftests with TTL expiry, PMTU/DF and GSO cases, strict and loose source-route packets, router-alert delivery, XFRM forward policy drops, netfilter forward hook behavior, switchdev offload marks, and SNMP counter checks for forwarded, header-error, and fragment-failure paths.
