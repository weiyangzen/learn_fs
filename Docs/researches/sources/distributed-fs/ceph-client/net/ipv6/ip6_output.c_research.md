# sources/distributed-fs/ceph-client/net/ipv6/ip6_output.c

## Purpose
This file implements the main IPv6 transmit side for the Ceph-client kernel tree copy: local packet output, forwarding, route lookup helpers, fragmentation, corked datagram assembly, and pending-frame flush/send helpers. It is the shared path used by TCP/SCTP-style `ip6_xmit()` callers, UDP/raw corking via `ip6_append_data()`, multicast routing output, and generic `dst_output()` routing callbacks.

## Important APIs, Types, And Functions
Exported transmit entry points are `ip6_output()`, `ip6_xmit()`, `ip6_fragment()`, `ip6_append_data()`, `ip6_push_pending_frames()`, `ip6_flush_pending_frames()`, `ip6_make_skb()`, and route helpers `ip6_dst_lookup()`, `ip6_dst_lookup_flow()`, and `ip6_sk_dst_lookup_flow()`. Support exports include `ip6_dst_hoplimit()`, `ip6_autoflowlabel()`, `ip6_fraglist_init()`, `ip6_fraglist_prepare()`, `ip6_frag_init()`, and `ip6_frag_next()`.

Core local-output helpers are `ip6_finish_output2()`, `__ip6_finish_output()`, and `ip6_finish_output()`. Forwarding is centered on `ip6_forward()`, `ip6_pkt_too_big()`, `ip6_forward_proxy_check()`, `ip6_call_ra_chain()`, and `ip6_forward_finish()`. Corked datagram state is handled through `struct inet_cork_full`, `struct inet6_cork`, `struct ipv6_txoptions`, `struct flowi6`, and skb write queues.

## Control Flow
`ip6_xmit()` grows headroom for link, IPv6, and extension headers; pushes fragmentable and non-fragmentable IPv6 options; builds the IPv6 header; checks PMTU unless the skb is GSO or ignores DF; passes through L3 master handling and `NF_INET_LOCAL_OUT`; and finally uses `dst_output()`. `ip6_output()` is the post-routing transmit path: it assigns the egress device from the dst, rejects disabled IPv6, runs `NF_INET_POST_ROUTING` unless the skb was rerouted, then reaches `ip6_finish_output()`.

`ip6_finish_output()` first runs cgroup egress BPF. `__ip6_finish_output()` handles XFRM reroute, GSO validation, fragmentation, and final neighbor output. `ip6_finish_output2()` performs multicast loopback and node-local multicast suppression, lightweight-tunnel transmit redirection, SNMP stats, nexthop neighbor lookup/create, and `neigh_output()`.

`ip6_forward()` validates forwarding enablement, packet type, LRO, XFRM forward policy, router-alert raw delivery, hop-limit expiry, proxy-NDP local handling, redirect generation, source-address validity, PMTU, COW headroom, hop-limit decrement, and `NF_INET_FORWARD` dispatch. It generates ICMPv6 errors for hop-limit, link-local source, and packet-too-big cases.

Fragmentation uses a fast frag-list path when geometry, headroom, and clone constraints are already suitable; otherwise it allocates new fragments with `ip6_frag_next()`. Both paths update fragment stats and preserve skb metadata, delivery time, dst, owner, security mark, netfilter state, and extension metadata. Corked datagram flow starts in `ip6_append_data()`, initializes cork/dst/tx options on the first write, queues one or more skbs in `__ip6_append_data()`, then `__ip6_make_skb()` coalesces the queue into a final skb with IPv6 header and dst before `ip6_send_skb()`.

## State And Persistence
The file does not persist state beyond kernel memory. It mutates skb metadata, per-socket cork fields, socket write queues, socket timestamp keys, route/dst references, and network-device/IPv6 SNMP counters. Route lookup may store connected socket dst caches through `ip6_sk_dst_store_flow()`. Corked options are deep-copied into `inet_cork_full.base6.opt` and released by `ip6_cork_release()`.

Fragmentation state is transient in `struct ip6_frag_state` or `struct ip6_fraglist_iter`. Memory accounting is tied to `sk_wmem_alloc`, skb destructors, zerocopy user-arg references, and page-frag ownership; failures roll back cork length, timestamp keys, and zerocopy references where needed.

## Dependencies And Integration Points
This file sits at the junction of IPv6 routing, neighbor discovery, XFRM/IPsec, netfilter, cgroup BPF, raw IPv6 router-alert sockets, multicast routing, lightweight tunnels, L3 master devices, PMTU/ICMPv6, skb GSO/offload, and socket corking. It depends on helpers from `ip6_route`, `addrconf`, `rawv6`, `icmp`, `xfrm`, `lwtunnel`, `ip_tunnels`, and generic socket/skb memory APIs.

Multicast loopback calls `mroute6_is_socket()` from `ip6mr.c`. Router-alert forwarding delivers to `ip6_ra_chain` maintained by `ipv6_sockglue.c`. UDP/raw datagram send paths depend on the corking APIs here, while tunnel code uses `ip6_dst_hoplimit()`, `ip6_output()`, and route lookup helpers.

## Risks And Edge Cases
High-risk areas are PMTU and fragmentation decisions, especially `frag_max_size`, GSO slow-path segmentation, `ignore_df`, socket `frag_size`, and RFC 7112 first-fragment header-chain requirements. The corking path has complex memory accounting and zerocopy downgrade/abort behavior; regressions can leak user references, undercount `sk_wmem_alloc`, or corrupt partial writes.

Forwarding is security-sensitive around source address validation, link-local behavior, XFRM policy, proxy-NDP handoff, and redirect generation. `ip6_call_ra_chain()` clones to all but the final router-alert socket, so raw socket registration/lifetime must stay protected by `ip6_ra_lock`. Fragment fast-path ownership transfer from frag_list skbs adjusts `truesize` and destructors and must be undone on slow-path fallback.

## Test Signals
Strong signals include IPv6 local TCP/UDP/raw send, corked UDP with extension headers, zerocopy and splice send paths, PMTU `EMSGSIZE` reporting, GSO packets larger than MTU, local and forwarded fragmentation, route-cache reuse on connected sockets, IPv6 forwarding with redirects and XFRM policy, proxy-NDP handoff, router-alert raw socket delivery, multicast loopback/node-local suppression, cgroup egress BPF drop, and netfilter local/post-routing/forward hook coverage. KASAN/KMSAN plus lockdep are useful for corking and frag-list ownership paths.
