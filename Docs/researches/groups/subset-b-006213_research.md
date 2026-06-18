# subset-b-006213 Research

Grouped code research for the IPv6 output, tunnel, UDP tunnel, virtual tunnel interface, multicast routing, IPComp, and socket-option glue files. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_output.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_tunnel.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ip6_tunnel.c

## Purpose
This file implements the generic IPv6 tunnel netdevice driver for IPv4-over-IPv6, IPv6-over-IPv6, and optionally MPLS-over-IPv6 under the `ip6tnl` rtnetlink kind. It manages tunnel device lookup/creation, fallback `ip6tnl0`, encapsulation and decapsulation, PMTU/error propagation, optional collect-metadata mode, tunnel encapsulation offloads, ioctl compatibility, and module/per-net registration.

## Important APIs, Types, And Functions
The per-net state is `struct ip6_tnl_net`, which holds the fallback device, wildcard and remote/local hash tables, and one collect-metadata tunnel pointer. Tunnel devices use `struct ip6_tnl` and `struct __ip6_tnl_parm`.

Externally visible helpers include `ip6_tnl_parse_tlv_enc_lim()`, `ip6_tnl_get_cap()`, `ip6_tnl_rcv_ctl()`, `ip6_tnl_rcv()`, `ip6_tnl_xmit_ctl()`, `ip6_tnl_xmit()`, `ip6_tnl_change_mtu()`, `ip6_tnl_get_iflink()`, `ip6_tnl_encap_add_ops()`, `ip6_tnl_encap_del_ops()`, `ip6_tnl_encap_setup()`, and `ip6_tnl_get_link_net()`. Netdevice and rtnetlink operations are wired through `ip6_tnl_netdev_ops` and `ip6_link_ops`.

Core internal flows are `ip6_tnl_lookup()`, `ip6_tnl_locate()`, `ip6_tnl_link()`, `ip6_tnl_unlink()`, `ipxip6_rcv()`, `__ip6_tnl_rcv()`, `ipxip6_tnl_xmit()`, `ip6_tnl_start_xmit()`, `ip6_tnl_link_config()`, `ip6_tnl_update()`, and `ip6_tnl_siocdevprivate()`.

## Control Flow
Receive handlers are registered as XFRM IPv6 tunnel handlers for AF_INET, AF_INET6, and AF_MPLS. `ipxip6_rcv()` looks up a tunnel by outer source/destination and ingress link, validates configured protocol, runs XFRM input policy, checks local/remote address validity with `ip6_tnl_rcv_ctl()`, pulls the outer header, optionally creates metadata dst state, and calls `__ip6_tnl_rcv()`. The decap helper validates optional checksum/sequence flags, converts Ethernet-style tunnels with `eth_type_trans()` when needed, resets inner headers, applies DSCP/ECN decapsulation, scrubs cross-netns skb metadata, attaches collect-metadata dst, updates tunnel stats, and injects into GRO cells.

Transmit starts at `ip6_tnl_start_xmit()`, which accepts only IPv4, IPv6, or MPLS payloads and rejects obvious IPv6 source/tunnel conflicts. `ipxip6_tnl_xmit()` builds the outer `flowi6` either from collect-metadata tunnel info or from configured tunnel parameters, handles encapsulation-limit decrement for inner IPv6, chooses traffic class/flowlabel/fwmark policy, applies ECN encapsulation, and delegates to `ip6_tnl_xmit()`. `ip6_tnl_xmit()` resolves NBMA remotes when configured remote is any, optionally uses `dst_cache`, validates xmit capability, performs IPv6 route and XFRM lookup, selects a source address for collect-metadata mode if needed, checks routing loops and PMTU, reallocates headroom, applies optional tunnel encapsulation, pushes tunnel-encapsulation-limit options, builds the outer IPv6 header, and sends through `ip6tunnel_xmit()`.

Control-plane flow supports legacy `SIOC*Tunnel` ioctls and rtnetlink creation/change/delete. Newlink rejects duplicate endpoint/link tuples and allows a single collect-metadata tunnel. Changelink prevents most mutation of fallback `ip6tnl0`, updates encap state, relinks tunnel hash entries under RTNL with `synchronize_net()`, recomputes capabilities and MTU/headroom, and emits netdevice state changes.

## State And Persistence
Tunnel state is in memory per net namespace and per netdevice. Hash-table membership is RCU-protected and updated under RTNL. Each tunnel stores parameters, flow template, encapsulation settings, header lengths, sequence state, error counters/time, GRO cells, dst cache, and a netdevice tracker. No on-disk persistence exists; userspace recreates tunnels through rtnetlink or ioctls.

The fallback `ip6tnl0` is created per namespace when fallback tunnels are enabled and is netns-immutable. `collect_md_tun` is a singleton pointer per namespace. Module parameter `log_ecn_error` persists only as runtime module/sysfs state.

## Dependencies And Integration Points
The file integrates with rtnetlink `ip6tnl`, XFRM tunnel dispatch, IPv6 route lookup, PMTU update/redirect handling, DSCP/ECN helpers, MPLS optional build support, metadata dst/tunnel-info APIs, tunnel encapsulation operations in `ip6tun_encaps`, GRO cells, netdevice stats, and legacy `ip_tunnel_header_ops`. It calls `ip6_output`-side helpers such as `ip6_dst_hoplimit()` and `ip6_tnl_parse_tlv_enc_lim()` is reused by VTI-like paths.

## Risks And Edge Cases
Loop avoidance is spread across address conflict checks, local/remote address validation, destination device comparison, and encap-limit processing. NBMA remote resolution depends on existing skb dst/neighbour or IPv4 route gateway state and can fail as link failure. PMTU math must account for Ethernet tunnel devices, IPv6 header, optional tunnel encap header, tunnel header, and 8-byte tunnel encapsulation-limit option.

Collect-metadata mode bypasses some configured tunnel state and requires valid `skb_tunnel_info`; it rejects additional tunnel encap on transmit. Error handling for ICMPv6 converts outer errors to inner ICMP/ICMPv6 only for specific conditions and depends on enough quoted packet bytes. Hash relinking must use `synchronize_net()` so concurrent RCU receive lookups do not see freed or inconsistent chains.

## Test Signals
Useful signals include `ip -6 tunnel add/change/del` and legacy ioctl coverage; IPv4, IPv6, and MPLS payload transmit/receive; fallback `ip6tnl0` protocol-only mutation; collect-metadata VXLAN/OVS-like tunnel metadata paths; ECN error logging; tunnel encapsulation-limit decrement and zero-limit ICMPv6 parameter-problem; PMTU too-big propagation to inner IPv4/IPv6; dst-cache invalidation after parameter change; duplicate tunnel rejection; netns teardown; and route-loop detection when egress resolves back to the same tunnel device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_tunnel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_udp_tunnel.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ip6_udp_tunnel.c

## Purpose
This file provides small shared helpers for IPv6 UDP-based tunnel drivers. It creates kernel UDP/IPv6 sockets, builds IPv6/UDP tunnel headers around an skb, and performs route lookup with optional dst-cache support for tunnel endpoints.

## Important APIs, Types, And Functions
Exported APIs are `udp_sock_create6()`, `udp_tunnel6_xmit_skb()`, and `udp_tunnel6_dst_lookup()`. They operate on `struct udp_port_cfg`, `struct socket`, `struct dst_entry`, `struct ip_tunnel_key`, `struct dst_cache`, IPv6 addresses, and UDP source/destination ports.

`udp_sock_create6()` supports v6-only mode, binding to an interface index, binding to local IPv6 address/port, optional connected peer address/port, and toggling UDPv6 checksum behavior. `udp_tunnel6_xmit_skb()` pushes `struct udphdr` and `struct ipv6hdr`, computes UDPv6 checksum with `udp6_set_csum()`, and sends via `ip6tunnel_xmit()`. `udp_tunnel6_dst_lookup()` constructs `flowi6` from tunnel key, ports, mark, traffic class, label, and output interface, then calls `ip6_dst_lookup_flow()`.

## Control Flow
Socket creation allocates an AF_INET6 datagram kernel socket, applies optional `IPV6_V6ONLY` and bind-to-index constraints, binds the local endpoint, optionally connects the peer endpoint, sets no-checksum tx/rx flags according to configuration, and returns the socket. All failure paths shut down and release the partially created socket and clear the caller's pointer.

Transmit assumes the caller already has route and headroom. It prepends UDP, assigns ports and length, attaches the dst to the skb, computes checksum or no-checksum state, prepends IPv6, fills flow label, payload length, next header, hop limit, and addresses, and hands off to the generic IPv6 tunnel transmit helper.

Route lookup first tries `dst_cache_get_ip6()` when a cache is supplied. On miss it initializes `flowi6`, performs XFRM-aware IPv6 dst lookup using the supplied socket, maps route failures to `-ENETUNREACH`, rejects circular routes where the dst device is the tunnel device, stores the selected source in both dst cache and caller storage, and returns a held dst.

## State And Persistence
The helpers own no persistent global state. Socket state is held by the caller after successful creation. The dst lookup helper may update a caller-provided `dst_cache` and writes the selected source address through `saddr`. Checksumming flags are stored on the UDP socket.

## Dependencies And Integration Points
This file is a library for drivers such as VXLAN, GENEVE, GUE, or other UDP tunnel users. It depends on kernel socket APIs, UDP tunnel configuration, IPv6 route/XFRM lookup, IPv6 checksum helpers, `ip6tunnel_xmit()`, and optional `CONFIG_DST_CACHE`.

## Risks And Edge Cases
UDPv6 checksum disabling is protocol-sensitive; many deployments require IPv6 UDP checksums except for explicitly permitted tunnel modes. Route lookup returns `-ENETUNREACH` for any `ip6_dst_lookup_flow()` error, losing more specific errno. Circular-route detection is only `dst_dev(dst) == dev`; more complex recursive tunnel loops rely on upper layers. The xmit helper does not validate headroom or skb writability.

## Test Signals
Test socket creation with local-only and connected peer configs, v6-only sockets, bind-ifindex failures, checksum on/off settings, route lookup cache hit/miss, no-route and circular-route failures, selected source address caching, and transmit packet capture validating IPv6 payload length, UDP length/checksum, flow label, hop limit, and source/destination ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_udp_tunnel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_vti.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ip6_vti.c

## Purpose
This file implements the IPv6 virtual tunnel interface driver, `vti6`, which binds IPv6 tunnel netdevices to XFRM/IPsec tunnel states. It provides policy-mark based transmit and receive paths for ESP, AH, IPComp, and optional IPv6 tunnel protocol handling, plus rtnetlink/ioctl configuration and per-net fallback device management.

## Important APIs, Types, And Functions
Per-net state is `struct vti6_net`, which contains fallback `ip6_vti0` and endpoint hash tables. The driver reuses `struct ip6_tnl` and `struct __ip6_tnl_parm` from the IPv6 tunnel infrastructure for parameters, keys, link, netdevice, and hash chaining.

Important functions include `vti6_tnl_lookup()`, `vti6_locate()`, `vti6_tnl_link()`, `vti6_tnl_unlink()`, `vti6_input_proto()`, `vti6_rcv()`, `vti6_rcv_cb()`, `vti6_state_check()`, `vti6_xmit()`, `vti6_tnl_xmit()`, `vti6_err()`, `vti6_link_config()`, `vti6_update()`, `vti6_siocdevprivate()`, and rtnetlink handlers `vti6_newlink()`, `vti6_changelink()`, and `vti6_dellink()`.

XFRM registration uses `xfrm6_protocol` handlers for ESP, AH, and COMP with high priority, and, when reachable, `xfrm6_tunnel` handlers for IPv6 tunnel traffic. Netdevice operations are in `vti6_netdev_ops`, and rtnetlink kind is `"vti6"`.

## Control Flow
Receive protocol handlers call `vti6_input_proto()`, which looks up a matching tunnel by outer source/destination, validates the tunnel protocol, runs XFRM input policy, checks local/remote receive capability through `ip6_tnl_rcv_ctl()`, stores the matched tunnel in `XFRM_TUNNEL_SKB_CB`, sets SPI family/destination offset metadata, and calls `xfrm_input()`. After XFRM processing, `vti6_rcv_cb()` validates inner mode/family, temporarily replaces `skb->mark` with the tunnel input key for policy check, scrubs cross-netns metadata, moves the skb to the tunnel device, and updates rx stats.

Transmit starts from `vti6_tnl_xmit()`, which accepts IPv6 and IPv4 payloads, clears protocol-specific skb control blocks, decodes the inner flow, overrides `flowi_mark` with the tunnel output key, and calls `vti6_xmit()`. `vti6_xmit()` ensures there is an skb dst by doing route lookup through the tunnel device if needed, performs `xfrm_lookup_route()`, verifies that the resulting XFRM state is IPv6 tunnel mode and matches configured endpoints, validates xmit capability, rejects local routing loops, enforces PMTU with ICMP/ICMPv6 errors, scrubs the skb, assigns the transformed dst/dev, calls `dst_output()`, and accounts transmit stats.

Control-plane flow mirrors `ip6_tunnel.c` but with VTI-specific parameters: local, remote, link, input key, output key, fwmark, and protocol fixed to IPv6. Ioctls support `SIOCGETTUNNEL`, add/change/delete, and rtnetlink supports new/change/delete/fill_info. Updates relink the tunnel hash under RTNL with `synchronize_net()` and recompute capabilities/MTU.

## State And Persistence
VTI state is runtime-only per net namespace and per netdevice. The tunnel hash tables are RCU-read and RTNL-updated. Each tunnel stores local/remote endpoint addresses, input/output keys, optional link, protocol, fwmark, netdevice tracker, and cached dst state inherited from `struct ip6_tnl`. XFRM security associations and policies are separate system state managed by XFRM; VTI only selects them via mark and endpoint checks.

The fallback device `ip6_vti0` is created per namespace when fallback tunnels are enabled. No settings are persisted by the driver itself.

## Dependencies And Integration Points
`ip6_vti.c` depends on XFRM state/policy lookup and protocol registration, IPv6 tunnel capability helpers from `ip6_tunnel.c`, IPv4 and IPv6 route lookup, ICMP/ICMPv6 PMTU reporting, rtnetlink tunnel attributes, netdevice notifier lifecycle through pernet exit, and generic tunnel header ops. It integrates with userspace `ip link add type vti6`, legacy tunnel ioctls, and IPsec policy/SAs configured outside this file.

## Risks And Edge Cases
The transmit path depends on an XFRM tunnel-mode state; if route lookup returns `DST_XFRM_QUEUE`, packets can queue before state validation. Mark handling is security-sensitive: output uses `o_key`, receive policy check uses `i_key`, and `vti6_err()` looks up XFRM state using the output key. PMTU behavior differs for IPv4 payloads depending on DF, while IPv6 payloads always get packet-too-big with minimum MTU clamping.

Tunnel lookup ignores link in comparison, unlike generic ip6tnl, so endpoint-only matching governs receive. RCU hash relinking must remain synchronized with readers. Fallback devices are deletable only through namespace teardown, while non-fallback tunnel conflicts must be rejected by endpoint tuples. The route-loop check only catches direct `dst_dev == dev`.

## Test Signals
Relevant tests include creating/changing/deleting `vti6` links through rtnetlink and ioctl, duplicate endpoint rejection, ESP/AH/IPComp inbound dispatch to the right tunnel, input/output key policy selection, IPv4 and IPv6 payload transmit through matching XFRM tunnel SAs, PMTU too-big behavior for IPv4 DF and IPv6, XFRM state mismatch drop, route-loop detection, fallback `ip6_vti0` behavior, netns teardown, and lockdep/RCU checks during concurrent traffic and tunnel change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_vti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6mr.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ip6mr.c

## Purpose
This file implements IPv6 multicast routing: multicast virtual interfaces, multicast forwarding cache entries, unresolved cache queries to a routing daemon, PIM-SM register handling, `/proc` visibility, rtnetlink route dump/get support, multicast-routing socket options/ioctls, per-net table initialization, and multicast packet forwarding from input and output paths.

## Important APIs, Types, And Functions
Central state lives in `struct mr_table`, `struct vif_device`, and `struct mfc6_cache`. IPv6-specific rule/result wrappers are `struct ip6mr_rule` and `struct ip6mr_result`. Global locks are `mrt_lock` for VIF/MFC/mroute socket state and `mfc_unres_lock` for unresolved queues. `mrt_cachep` allocates MFC entries.

Initialization and teardown are `ip6_mr_init()` and `ip6_mr_cleanup()`. Socket-facing APIs are `ip6_mroute_setsockopt()`, `ip6_mroute_getsockopt()`, `ip6mr_ioctl()`, `ip6mr_compat_ioctl()`, `ip6mr_sk_done()`, and `mroute6_is_socket()`. Packet paths are `ip6_mr_input()`, `ip6_mr_output()`, `ip6_mr_forward()`, `ip6_mr_output_finish()`, `ip6mr_forward2()`, `ip6mr_output2()`, and `ip6mr_prepare_xmit()`.

Control-plane helpers include `mif6_add()`, `mif6_delete()`, `ip6mr_mfc_add()`, `ip6mr_mfc_delete()`, `mroute_clean_tables()`, `ip6mr_cache_unresolved()`, `ip6mr_cache_resolve()`, `ip6mr_cache_report()`, `mr6_netlink_event()`, `mrt6msg_netlink_event()`, `ip6mr_rtm_getroute()`, and `ip6mr_rtm_dumproute()`.

## Control Flow
Per-network initialization registers fib notifier ops, creates multicast route tables and default rules, and optionally creates `/proc/net/ip6_mr_vif` and `/proc/net/ip6_mr_cache`. Module init creates the MFC slab cache, registers pernet ops, a netdevice notifier, optional PIM protocol handler, and rtnetlink route handlers.

Userspace enables a multicast routing socket with `MRT6_INIT` on a raw ICMPv6 socket. `MRT6_ADD_MIF` adds normal VIFs or PIM register VIFs, enabling all-multicast and incrementing IPv6 `mc_forwarding` counters. `MRT6_ADD_MFC` and proxy variants create or update forwarding cache entries, insert them into the rhashtable and cache list, notify fib/rtnetlink listeners, and replay any queued unresolved packets. Delete/flush paths remove VIFs and MFCs, notify listeners, drop or unregister PIM register devices, and destroy unresolved queues.

Incoming multicast packets enter `ip6_mr_input()`. It selects the multicast route table through rules, finds an exact `(S,G)` cache or fallback `(*,G)`/parent entry, queues unresolved packets and reports `MRT6MSG_NOCACHE` to the mroute socket if needed, or forwards via `ip6_mr_forward()`. Forwarding validates the incoming VIF, sends PIM assert reports on wrong-interface conditions, updates counters, clones skbs for all but one outgoing VIF, decrements hop limit, and transmits through netfilter forward hooks.

Local output with `IP6SKB_MCROUTE` enters `ip6_mr_output()`. If the skb was not already forwarded and cache lookup succeeds with the expected parent VIF, `ip6_mr_output_finish()` replicates to outgoing VIFs through `ip6_output()`; otherwise it falls back to normal IPv6 output or queues an unresolved query. PIM register handling decapsulates inbound PIM register packets to a virtual `pim6reg` device and sends whole-packet reports from that device back to the routing daemon.

## State And Persistence
All state is in memory per net namespace: multicast route tables, VIF arrays, MFC rhashtable/list, unresolved queue, mroute socket pointer, PIM flags, register VIF number, fib notifier sequence, and `/proc` entries. Cache entries track parent VIF, TTL thresholds, packet/byte/wrong-if counters, last-use/assert timestamps, flags, origin, and multicast group. Unresolved entries hold queued packets and expire after a timer-driven timeout.

There is no disk persistence. Static entries are flagged `VIFF_STATIC` or `MFC_STATIC` so selective flush commands can preserve or remove them, but they still disappear on namespace/module teardown.

## Dependencies And Integration Points
This file integrates with raw IPv6 sockets, multicast daemon APIs from `<linux/mroute6.h>`, rtnetlink route families `RTNL_FAMILY_IP6MR`, fib rules/notifiers, netdevice unregister notifications, IPv6 route output, netfilter IPv6 forward hooks, PIM protocol dispatch, procfs/seq_file, RCU, rhashtable, and generic multicast routing helpers shared with IPv4. `ip6_output.c` calls `mroute6_is_socket()` for multicast loopback behavior.

## Risks And Edge Cases
Concurrency is the major risk: data path is mostly RCU, table mutation is RTNL plus `mrt_lock`, unresolved queues use `mfc_unres_lock`, and socket lifetime relies on `SOCK_RCU_FREE`. VIF deletion must update all-multicast, `mc_forwarding`, register-device state, netdevice trackers, and maxvif consistently. Unresolved queues are capped to a few packets per entry but can still produce daemon backpressure or timeout netlink replies.

Forwarding behavior for `(*,*)`, `(*,G)`, proxy parent entries, wrong-interface asserts, PIM whole-packet reports, and local-output multicast routing is subtle. Rtnetlink strict getroute validation requires full 128-bit source/destination lengths when attributes are present. Compatibility ioctls must avoid speculative out-of-bounds VIF access with `array_index_nospec()`.

## Test Signals
Strong coverage includes raw ICMPv6 `MRT6_INIT/DONE`, add/delete normal and PIM register MIFs, add/delete/update exact and proxy MFCs, unresolved queue creation/report/replay/timeout, multicast forwarding across multiple VIFs with hop-limit thresholds, wrong-interface assert generation, `MRT6_FLUSH` static/non-static behavior, netdevice unregister cleanup, `/proc/net/ip6_mr_vif` and `ip6_mr_cache` output, rtnetlink `RTM_GETROUTE` and dumps, multiple multicast tables/rules when enabled, PIM register encapsulation/decapsulation, and netns teardown under active traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6mr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ipcomp6.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ipcomp6.c

## Purpose
This file registers IPv6 IP Payload Compression Protocol support with XFRM. It wires generic IPComp compression/decompression into the IPv6 stack, initializes IPComp XFRM state for transport or tunnel mode, creates/attaches associated IPv6 tunnel states for tunnel-mode IPComp, and handles ICMPv6 PMTU/redirect errors for compressed packets.

## Important APIs, Types, And Functions
Main functions are `ipcomp6_err()`, `ipcomp6_tunnel_create()`, `ipcomp6_tunnel_attach()`, `ipcomp6_init_state()`, and `ipcomp6_rcv_cb()`. The protocol registration objects are `ipcomp6_type` (`struct xfrm_type`) and `ipcomp6_protocol` (`struct xfrm6_protocol`). Module lifecycle is `ipcomp6_init()` and `ipcomp6_fini()`.

The file uses generic IPComp helpers `ipcomp_init_state()`, `ipcomp_destroy()`, `ipcomp_input()`, and `ipcomp_output()`, plus IPv6 tunnel SPI allocation/lookup helpers `xfrm6_tunnel_alloc_spi()` and `xfrm6_tunnel_spi_lookup()`.

## Control Flow
When an IPComp XFRM state is created, `ipcomp6_init_state()` accepts transport and tunnel modes, sets header length to zero or one IPv6 header, delegates compression-algorithm initialization to generic IPComp, and for tunnel mode attaches an associated IPv6 tunnel state. Attachment first looks up an existing tunnel SPI for the source address and matching XFRM state; if none exists it allocates a new state, fills IPv6 tunnel identity, selector, family, mode, source, mark, and if_id, initializes it, inserts it into XFRM state tables, and increments tunnel user counts.

Inbound IPComp packets are received through `xfrm6_protocol_register()` with `xfrm6_rcv` and `xfrm_input`, then generic IPComp input handles decompression. ICMPv6 errors handled by `ipcomp6_err()` only process packet-too-big and redirect. It derives the IPComp CPI as an XFRM SPI, looks up the matching state by destination, mark, protocol COMP, and AF_INET6, then applies `ip6_redirect()` or `ip6_update_pmtu()`.

## State And Persistence
This file owns only static registration objects and a lock-class key. Runtime state lives in XFRM states. Tunnel-mode IPComp creates or references an associated XFRM tunnel state and increments `tunnel_users`. No state is persisted outside XFRM's in-kernel security association lifetime.

## Dependencies And Integration Points
The file depends on the XFRM type/protocol registry, generic IPComp implementation, IPv6 route/PMTU/redirect helpers, PF_KEY/IPComp UAPI definitions, and IPv6 tunnel SPI allocation. It registers protocol `IPPROTO_COMP` for AF_INET6 and declares `MODULE_ALIAS_XFRM_TYPE(AF_INET6, XFRM_PROTO_COMP)`.

## Risks And Edge Cases
Tunnel-mode attach is sensitive to reference counts: newly created tunnel states are inserted and held, then assigned to `x->tunnel` and counted with `tunnel_users`. Error paths must mark failed states dead and drop references. `ipcomp6_err()` assumes enough quoted bytes exist at the IPComp header offset; callers in the IPv6 protocol error path are expected to enforce that. Unsupported modes return `-EINVAL` with extack text.

## Test Signals
Coverage should include transport-mode and tunnel-mode IPComp SA creation, unsupported mode rejection, compression/decompression of IPv6 packets through XFRM, associated tunnel state reuse and creation, teardown reference counts, ICMPv6 packet-too-big updating PMTU for COMP states, redirect handling, malformed or unrelated ICMP errors being ignored, and module load/unload registration rollback on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ipcomp6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ipv6_sockglue.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ipv6_sockglue.c

## Purpose
This file implements the IPv6 socket option interface: `setsockopt()` and `getsockopt()` handling for SOL_IPV6, router-alert raw socket registration, sticky extension-header options, multicast and source-filter APIs, packet-info and ancillary option state, flowlabel/IPsec policy delegation, IPv4 address-form conversion, and netfilter sockopt fallback.

## Important APIs, Types, And Functions
Global router-alert state is `ip6_ra_chain` protected by `ip6_ra_lock`; `ip6_min_hopcount` is a static key enabled when any socket sets a positive minimum hop count. Exported entry points are `ipv6_setsockopt()`, `ipv6_getsockopt()`, `do_ipv6_setsockopt()`, `do_ipv6_getsockopt()`, `ip6_ra_control()`, and `ipv6_update_options()`.

Multicast helpers include `ipv6_mcast_join_leave()`, `compat_ipv6_mcast_join_leave()`, `do_ipv6_mcast_group_source()`, `ipv6_set_mcast_msfilter()`, `compat_ipv6_set_mcast_msfilter()`, `ipv6_get_msfilter()`, and `compat_ipv6_get_msfilter()`. Sticky extension-header handling is in `ipv6_set_opt_hdr()` and `ipv6_getsockopt_sticky()`.

The code mutates `struct ipv6_pinfo` fields such as hop limits, multicast interface/hops, unicast interface, PMTU discovery, fragment size, traffic class, source preferences, sticky packet info, receive option bitfields, and RCU-managed `ipv6_txoptions`.

## Control Flow
`ipv6_setsockopt()` delegates SOL_IP options for non-raw sockets to IPv4, rejects non-SOL_IPV6, calls `do_ipv6_setsockopt()`, and on generic `-ENOPROTOOPT` tries netfilter IPv6 sockopts except for XFRM/IPsec policy options. `do_ipv6_setsockopt()` first handles multicast-routing options through `ip6_mroute_setsockopt()`. It then processes several lockless per-socket options with direct `WRITE_ONCE()` or bit updates, including hop limits, multicast loop/hops/all/interface, PMTU discovery, MTU/frag size, autoflowlabel, dontfrag, receive errors, router-alert isolate, min hop count, flowinfo send, unicast interface, and address preferences.

Options that require socket serialization take the socket lock and recheck that the socket is still AF_INET6. The locked switch handles `IPV6_ADDRFORM` conversion of connected v4-mapped TCP/UDP sockets to IPv4, v6-only, receive ancillary toggles, traffic class, transparent/freebind, original destination, sticky extension headers, packet-info, legacy 2292 packet options, multicast membership/source filters, anycast membership, router alert, flowlabel manager, XFRM/IPsec policy, and receive fragment size.

Sticky extension-header updates validate privilege for hop-by-hop and destination options, option length and alignment, routing header type, and SRH format, then replace the socket's RCU txoptions through `ipv6_update_options()`, which also refreshes TCP MSS/ext header length for connected sockets. Router alert registration adds or removes the raw socket from `ip6_ra_chain` and holds/drops a socket reference.

`ipv6_getsockopt()` mirrors the level/fallback logic, calls `do_ipv6_getsockopt()`, and optionally falls back to netfilter. Getsockopt handles multicast routing, multicast source filters, legacy packet options, current MTU/path MTU, sticky options, flowlabel lookup, and the scalar socket fields. It writes truncated integer lengths according to the supplied optlen.

## State And Persistence
State is socket-local except for `ip6_ra_chain`, `ip6_min_hopcount`, and multicast-routing state delegated to `ip6mr.c`. Socket state lives in `struct ipv6_pinfo`, `struct inet_sock`, `struct sock` flags, multicast/anycast membership lists, flowlabel tables, XFRM policies, and RCU-managed `struct ipv6_txoptions`. No state persists after socket close, although external XFRM policies or flowlabels may have their own lifetimes.

`IPV6_ADDRFORM` permanently converts an eligible established v4-mapped TCP/UDP IPv6 socket to IPv4 protocol/socket ops and cleans up IPv6 multicast/anycast/options. Router-alert registration holds a reference on the raw socket until removed.

## Dependencies And Integration Points
The file integrates with IPv6 datagram ancillary control parsing/emission, multicast listener/source-filter code, anycast membership, IPv6 flowlabel manager, XFRM user policy, TCP MSS recalculation, UDP pending state, netfilter sockopts, IPv4 socket ops for `IPV6_ADDRFORM`, netdevice/l3mdev validation for interface options, Segment Routing Header validation, PSP overhead, and multicast routing options from `ip6mr.c`. `ip6_output.c` reads `ip6_ra_chain` for forwarded router-alert delivery.

## Risks And Edge Cases
The option surface is broad and compatibility-sensitive. Lockless options can race with address-form conversion; the code explicitly rechecks family after taking the lock for locked options, but some UDP send and PMTU paths are documented as still having races after disabling IPv6 options during conversion. Sticky option memory accounting uses `sk_omem_alloc` and txoption refcounts and must release old options after replacement.

Multicast filter APIs must defend against optlen overflows, compat layout differences, and `sysctl_mld_max_msf` limits. `IPV6_UNICAST_IF` uses network-byte-order integer API semantics, validates device existence, and conflicts with bound devices. Router-alert registration is raw-socket-only and duplicate registrations return `-EADDRINUSE`; removal with no entry returns `-ENOBUFS`, matching legacy behavior. Privileged options require namespace capabilities.

## Test Signals
Useful tests include scalar set/get for hop limits, PMTU discovery, multicast loop/hops/all/interface, unicast interface, tclass, transparent/freebind permissions, dontfrag, autoflowlabel, min hop count static key, receive error queue purge, receive ancillary toggles, sticky hop/dst/routing/SRH options, legacy 2292 packet options, multicast join/leave and source filters in native and compat modes, anycast join/leave, router-alert registration and forwarded delivery, flowlabel manager get/set, XFRM/IPsec policy permission paths, `IPV6_ADDRFORM` conversion of connected v4-mapped TCP/UDP sockets, and netfilter sockopt fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ipv6_sockglue.c -->
