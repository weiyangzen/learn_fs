# subset-b-006217 IPv6 network research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/seg6_local.c -->
# sources/distributed-fs/ceph-client/net/ipv6/seg6_local.c

## Purpose
`seg6_local.c` implements the IPv6 Segment Routing local SID lightweight-tunnel endpoint. It is the receive-side action engine for `LWTUNNEL_ENCAP_SEG6_LOCAL`, handling SRv6 End, End.X, End.T, End.DX2, End.DX4, End.DX6, End.DT4, End.DT6, End.DT46, End.B6, End.B6.Encaps, and End.BPF behaviors. It also owns netlink parsing, dumping, comparison, optional counters, flavor support, and lwtunnel registration for local SRv6 behaviors.

## Important APIs, types, and functions
Core state is carried by `struct seg6_local_lwt`, which stores the selected action, parsed attributes, nexthops, table or VRF table IDs, SRH template, BPF program reference, optional per-CPU counters, flavor configuration, and the selected `seg6_action_desc`. `struct seg6_action_desc` maps each UAPI action to required attributes, optional attributes, input callback, headroom, and optional build/destroy hooks. `seg6_action_table[]` is the main behavior registry.

Packet helpers include `get_and_validate_srh()`, `decap_and_validate()`, `advance_nextseg()`, `seg6_lookup_any_nexthop()`, `seg6_lookup_nexthop()`, `seg6_pop_srh()`, and `end_dt_vrf_core()`. Input callbacks implement the actions: `input_action_end()`, `input_action_end_x()`, `input_action_end_t()`, `input_action_end_dx2()`, `input_action_end_dx6()`, `input_action_end_dx4()`, `input_action_end_dt4()`, `input_action_end_dt6()`, `input_action_end_dt46()`, `input_action_end_b6()`, `input_action_end_b6_encap()`, and `input_action_end_bpf()`.

Control-plane helpers include per-attribute parsers/dumpers/comparators such as `parse_nla_srh()`, `parse_nla_table()`, `parse_nla_vrftable()`, `parse_nla_bpf()`, `parse_nla_counters()`, and `parse_nla_flavors()`. `seg6_local_build_state()`, `seg6_local_destroy_state()`, `seg6_local_fill_encap()`, `seg6_local_get_encap_size()`, and `seg6_local_cmp_encap()` implement the `lwtunnel_encap_ops` contract.

## Control flow
For packets, `seg6_local_input()` first rejects non-IPv6 packets, optionally runs the lwtunnel netfilter local-in hook, and then calls `seg6_local_input_core()`. The core retrieves the original route's lwtunnel state, dispatches to the action descriptor's input function, and updates optional per-CPU counters after the action returns.

Standard End and End.X validate the SRH and HMAC, decrement `segments_left`, update the IPv6 destination address, resolve the next route, and call `dst_input()`. End.X uses a configured IPv6 nexthop and optional output interface. End.T resolves within a configured table. NEXT-C-SID flavor paths shift the compressed SID argument in the destination address until the argument becomes zero, then fall back to normal End or End.X processing. RFC8986 PSP flavor support uses a packet-info/action lookup table and `seg6_pop_srh()` to remove the SRH at the penultimate segment.

Decapsulation actions call `decap_and_validate()` to reject packets with nonzero `segments_left`, validate HMAC, find the inner protocol, pull the outer headers, reset checksum state, and clear tunnel offload metadata. End.DX2 forwards an inner Ethernet frame through a configured Ethernet device after MTU, carrier, LRO, and protocol checks. End.DX6 and End.DX4 decapsulate IPv6 or IPv4, reset conntrack, optionally run prerouting hooks, route to an explicit or inner destination nexthop, and re-enter the stack with `dst_input()`.

End.DT4/DT6/DT46 route decapsulated traffic through a VRF table when `CONFIG_NET_L3_MASTER_DEV` is available. Build-time hooks map the configured VRF table to a VRF ifindex and enforce strict-mode requirements. Runtime processing presents the decapsulated packet as received by the VRF master and then routes it. Legacy DT6 table mode remains supported when a plain table attribute is configured.

End.B6 inserts an SRH inline after validating the current SRH. End.B6.Encaps advances the current SRH, marks inner headers, encapsulates with a new outer IPv6/SRH stack, and routes. End.BPF advances the current SRH, exposes a per-CPU mutable SRH state to `BPF_PROG_TYPE_LWT_SEG6LOCAL`, validates any BPF-edited SRH, and either routes normally or honors BPF redirect.

Netlink build flow parses a nested `SEG6_LOCAL_ACTION`, finds the descriptor, parses required attributes first, optional attributes second, then runs a behavior-specific constructor such as the End.DT VRF builder. Failures unwind any resources acquired by parsed attributes.

## State and persistence
All state is in kernel memory attached to a route's lwtunnel state. SRH templates and BPF names are dynamically allocated; BPF programs hold references; counters are per-CPU `pcpu_seg6_local_counters`; VRF mode records a net pointer, ifindex, table, family, and mode. No state persists beyond route/lwtunnel lifetime or module lifetime. Counter aggregation for netlink dumps uses `u64_stats_sync` to read per-CPU packet, byte, and error counters safely.

## Dependencies and integration points
This file integrates with the IPv6 route/FIB stack, lwtunnel core, SRv6 UAPI, HMAC validation, BPF lwt seg6local helpers, VRF/l3mdev, netfilter lwtunnel hooks, dst cache/routing, IP tunnel decapsulation helpers, Ethernet device transmit, conntrack reset, and netlink attribute policy code. `seg6_local_init()` registers `seg6_local_ops`; `seg6_local_exit()` unregisters it.

## Risks and edge cases
SRH mutation is sensitive to skb writability, header offsets, checksum updates, and extension-header ordering. `seg6_pop_srh()` must correctly preserve transport header position and reject fragment/auth ordering that cannot be safely updated. Flavor masks must stay disjoint from unsupported operations, and NEXT-C-SID block/function lengths must remain byte-aligned and within 128 bits. End.DT VRF mode depends on strict VRF table mapping and netns consistency. Decapsulation paths must avoid accepting packets with residual SRH segments or stale offload/conntrack state. Optional attribute cleanup must not double-free resources when required and optional masks change. Netlink size accounting must match emitted attributes, especially counters, BPF nests, SRHs, and flavor nests.

## Test signals
Useful tests create routes with every `SEG6_LOCAL_ACTION`, validate missing/extra attributes, dump and compare lwtunnel state, and exercise counter increments on success and drop. Packet tests should cover End, End.X, End.T, PSP, NEXT-C-SID, DX2 MTU/device failures, DX4/DX6 prerouting hooks, DT4/DT6 VRF strict-mode failures, DT46 protocol selection, B6/B6.Encaps SRH insertion, invalid HMAC, SRH with nonzero `segments_left` on decap, malformed extension header chains, and BPF programs returning OK, DROP, REDIRECT, invalid return values, and invalid SRH edits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/seg6_local.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/sit.c -->
# sources/distributed-fs/ceph-client/net/ipv6/sit.c

## Purpose
`sit.c` implements the SIT tunnel driver: IPv6, IPv4, and optionally MPLS carried over IPv4, with compatibility support for 6to4, 6rd, and ISATAP. It registers the `"sit"` rtnetlink kind, per-net fallback `sit0` device, xfrm tunnel protocol handlers, ioctl controls, and transmit/receive paths for protocol 41-style tunnels.

## Important APIs, types, and functions
Per-net state is `struct sit_net`, which stores four tunnel hash tables: wildcard, local-only, remote-only, and local+remote, plus the fallback device. Lookup and registration helpers are `ipip6_tunnel_lookup()`, `__ipip6_bucket()`, `ipip6_tunnel_link()`, `ipip6_tunnel_unlink()`, `ipip6_tunnel_create()`, and `ipip6_tunnel_locate()`.

Control interfaces include `ipip6_tunnel_ctl()`, `ipip6_tunnel_siocdevprivate()`, `ipip6_newlink()`, `ipip6_changelink()`, `ipip6_fill_info()`, and `ipip6_validate()`. PRL/ISATAP helpers include `ipip6_tunnel_get_prl()`, `ipip6_tunnel_add_prl()`, `ipip6_tunnel_del_prl()`, `ipip6_tunnel_prl_ctl()`, and `isatap_chksrc()`. 6rd support is handled by `check_6rd()`, `try_6rd()`, and `ipip6_tunnel_update_6rd()` when configured.

Data-path functions include `ipip6_rcv()`, `sit_tunnel_rcv()`, `ipip_rcv()`, optional `mplsip_rcv()`, `ipip6_tunnel_xmit()`, `sit_tunnel_xmit__()`, and `sit_tunnel_xmit()`. Device lifecycle is wired through `ipip6_netdev_ops`, `ipip6_tunnel_setup()`, `ipip6_tunnel_init()`, `ipip6_tunnel_uninit()`, and `ipip6_dev_free()`.

## Control flow
Module initialization registers per-net state, xfrm4 tunnel handlers for IPv6-in-IPv4, IPv4-in-IPv4, optional MPLS-in-IPv4, and then the rtnetlink link kind. Per netns initialization creates `sit0` when fallback tunnels are enabled and places it in the wildcard bucket.

Receive flow starts in the xfrm handler. `ipip6_rcv()` looks up a matching tunnel by outer source/destination and ingress scope, verifies that the tunnel accepts IPv6 or any protocol, reassigns the skb to the tunnel device, checks spoofing rules, pulls the IPv4 outer header, decapsulates ECN, updates tunnel rx stats, and injects the inner IPv6 packet via `netif_rx()`. `sit_tunnel_rcv()` handles inner IPv4 and MPLS by checking xfrm policy, pulling the outer header with the correct inner protocol, and delegating to generic `ip_tunnel_rcv()`.

Transmit flow in `sit_tunnel_xmit()` dispatches by skb protocol. IPv6 uses `ipip6_tunnel_xmit()`, which chooses an outer IPv4 destination from configured remote, ISATAP neighbor, embedded 6rd/6to4 address, or IPv4-compatible neighbor; routes the outer packet; enforces PMTU/DF rules; handles ECN encapsulation; prepares headroom and offloads; optional UDP tunnel encapsulation; and calls `iptunnel_xmit()`. IPv4 and MPLS use generic `ip_tunnel_xmit()` through `sit_tunnel_xmit__()`.

Configuration through ioctl or rtnetlink validates IP header version, header length, protocol, DF/TTL behavior, link directionality, duplicate tunnel keys, encapsulation parameters, fwmark, MTU, and optional 6rd attributes. Updating a tunnel unlinks it from hash buckets, synchronizes readers, changes endpoint/link/fwmark fields, relinks it, resets the dst cache, recalculates device binding, and emits a state change.

## State and persistence
Tunnel state is in `struct ip_tunnel` instances attached to netdevices. Per-net hash tables expose active tunnel lookup under RCU; updates are protected by RTNL and use `synchronize_net()` where endpoint keys move. Each tunnel owns parameters, fwmark, dst cache, optional PRL list, optional 6rd config, error counters/timestamps, and netdevice stats. The fallback `sit0` is per-netns and immutable across netns moves. No state is persistent after device/netns/module teardown.

## Dependencies and integration points
The driver depends on netdevice core, rtnetlink, xfrm4 tunnel registration, IPv4 routing and ICMP handling, IPv6 address and neighbor logic, PMTU helpers, ECN helpers, generic IP tunnel helpers, pernet operations, net namespace fallback tunnel policy, optional MPLS, optional 6rd, and L3 master scope handling. It exposes `MODULE_ALIAS_RTNL_LINK("sit")` and `MODULE_ALIAS_NETDEV("sit0")`.

## Risks and edge cases
Tunnel lookup priority must preserve exact local+remote matches before partial and wildcard matches. ISATAP PRL reads and deletes rely on RCU lifetime and `prl_count` consistency. 6rd spoofing checks can reject NATed protocol-41 traffic unless `only_dnatted()` finds an address on the tunnel device. PMTU logic must not emit impossible IPv6 MTUs below `IPV6_MIN_MTU`, and tunnel self-routing must detect loops. Updating endpoint keys must avoid concurrent readers seeing inconsistent hash placement. Netlink and ioctl paths must keep directionality of point-to-point versus multipoint devices consistent. Module cleanup waits for RCU callbacks because PRL entries can be freed asynchronously.

## Test signals
Coverage should create/delete/change SIT devices by `ip link` and ioctl, test duplicate local/remote/link keys, fallback `sit0` behavior, IPv6/IPv4/MPLS encapsulation where configured, PMTU too-big generation, ECN error logging, dst cache invalidation after link/fwmark changes, ISATAP PRL add/change/delete/get, 6rd parameter validation, 6to4 embedded destination selection, spoofed source/destination detection, L3 master ingress lookup, netns teardown, and module unregister failure cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/sit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/syncookies.c -->
# sources/distributed-fs/ceph-client/net/ipv6/syncookies.c

## Purpose
`syncookies.c` implements IPv6 TCP SYN cookie generation and validation. It lets a listening TCPv6 socket reconstruct enough request state from an ACK when the SYN queue overflowed, avoiding allocation on the initial SYN under pressure.

## Important APIs, types, and functions
`syncookie6_secret[2]` stores lazily initialized siphash keys. `msstab[]` maps the encoded MSS index to IPv6-appropriate MSS values. `cookie_hash()`, `secure_tcp_syn_cookie()`, and `check_tcp_syn_cookie()` create and validate the 32-bit cookie using source/destination IPv6 addresses, TCP ports, peer initial sequence, time counter, and small encoded data field. Public helpers include `__cookie_v6_init_sequence()`, `cookie_v6_init_sequence()`, `__cookie_v6_check()`, and `cookie_v6_check()`. `cookie_tcp_check()` reconstructs a `request_sock` from a valid cookie and TCP options.

## Control flow
When syncookies are needed, `__cookie_v6_init_sequence()` selects the largest supported MSS not greater than the offered MSS, rewrites the caller's MSS to that table value, and returns a secure sequence value. Later, an ACK is checked by subtracting the base hash and peer sequence, validating cookie age against `MAX_SYNCOOKIE_AGE`, and extracting the MSS index.

`cookie_v6_check()` is called on a listening socket path for non-RST ACKs when sysctl syncookies are enabled. It either delegates to a BPF cookie checker or uses `cookie_tcp_check()`. The checker rejects sockets without recent overflow, invalid cookies, failed timestamp-cookie decoding, or failed request allocation. On success it fills IPv6 remote/local addresses, runs the LSM `security_inet_conn_request()` hook, preserves packet options when the listener requested them, initializes window scaling and receive space, routes the request through `tcp_v6_syn_recv_sock()`, and returns either the created child socket, the original listener, or a drop path.

## State and persistence
The only local persistent state is the static random siphash secret array. Cookies encode transient time and MSS index but store no per-connection server memory until the final ACK. Reconstructed request state is allocated only after validation and follows normal TCP request/child socket lifetimes. Statistics are updated through `LINUX_MIB_SYNCOOKIESFAILED` and `LINUX_MIB_SYNCOOKIESRECV`.

## Dependencies and integration points
This file integrates with TCP option parsing, timestamp cookie decoding, BPF syncookie hooks, TCPv6 request socket ops, secure IPv6 sequence helpers, IPv6 packet option preservation, LSM connection-request hooks, route/child socket creation, and the IPv4 `net->ipv4.sysctl_tcp_syncookies` sysctl used by shared TCP code.

## Risks and edge cases
The MSS table must remain sorted and encodeable within `COOKIEBITS`. Cookie validation depends on using the exact same address/port/sequence tuple and time window. Timestamp offset adjustment must match `secure_tcpv6_seq_and_ts_off()` or timestamp cookies will fail. The path must not create sockets when the listener did not recently overflow, otherwise syncookies would weaken normal TCP semantics. Packet options are retained by taking an skb reference, so error paths must free reconstructed request state correctly.

## Test signals
Tests should force SYN queue overflow on TCPv6 listeners, verify valid ACKs create children, invalid cookies increment failure stats, stale cookies are rejected, MSS selection matches the table, timestamp and non-timestamp clients work, BPF syncookie hooks can accept or reject, packet options are preserved for interested sockets, LSM rejection frees the request, and syncookie handling is skipped when the sysctl is disabled or the packet is RST.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/syncookies.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/sysctl_net_ipv6.c -->
# sources/distributed-fs/ceph-client/net/ipv6/sysctl_net_ipv6.c

## Purpose
`sysctl_net_ipv6.c` registers `/proc/sys/net/ipv6` sysctl tables. It provides per-network-namespace IPv6 tunables, route and ICMP subtrees, and a small init-net read-oriented table for global MLD and optional CALIPSO settings.

## Important APIs, types, and functions
`ipv6_table_template[]` defines per-netns entries such as `bindv6only`, `anycast_src_echo_reply`, flowlabel controls, `fwmark_reflect`, id generation timing, nonlocal bind, extension-header limits, multipath hash policy and fields, `seg6_flowlabel`, route-notification policy, and IOAM IDs. `ipv6_rotable[]` defines `mld_max_msf`, `mld_qrv`, and optional NetLabel CALIPSO cache controls.

`proc_rt6_multipath_hash_policy()` and `proc_rt6_multipath_hash_fields()` wrap min/max handlers and emit `NETEVENT_IPV6_MPATH_HASH_UPDATE` on successful writes. Lifecycle is handled by `ipv6_sysctl_net_init()`, `ipv6_sysctl_net_exit()`, `ipv6_sysctl_register()`, and `ipv6_sysctl_unregister()`.

## Control flow
At global registration, the file first registers `ipv6_rotable` in init_net under `net/ipv6`, then registers a pernet subsystem. For each netns, `ipv6_sysctl_net_init()` duplicates `ipv6_table_template`, adjusts every `.data` pointer by the offset from `init_net` to the target `struct net`, obtains dynamically built route and ICMP sysctl tables from `ipv6_route_sysctl_init()` and `ipv6_icmp_sysctl_init()`, and registers `net/ipv6`, `net/ipv6/route`, and `net/ipv6/icmp`.

Failure paths unwind in reverse order: unregister registered headers and free copied tables. Netns exit reads the original allocated table pointers from `ctl_table_arg`, unregisters ICMP, route, and root IPv6 headers, and frees all three table allocations. Global unregister removes the init-net table and pernet subsystem.

## State and persistence
Sysctl values mostly live in `struct net.ipv6.sysctl` and are therefore per-network-namespace in-memory state. The duplicated ctl tables are per-netns allocations whose data pointers target that namespace. `ip6_header` stores the init-net global table header. Values persist only for the lifetime of the namespace or kernel boot.

## Dependencies and integration points
This file integrates with the sysctl core, pernet subsystem, IPv6 route sysctl generation, ICMPv6 sysctl generation, netevent notifications, IOAM defaults, FIB multipath hash fields, MLD globals, and optional NetLabel CALIPSO controls. Multipath write handlers notify listeners that route hashing behavior may need recalculation.

## Risks and edge cases
Pointer rebasing assumes every template `.data` points into `init_net` at the same struct offset used by every netns; adding a non-netns data pointer to the template would be unsafe unless handled specially. Registration failure paths must match the allocation/registration order to avoid leaks or unregistering invalid headers. Multipath handlers must notify only after successful writes. Min/max bounds protect several u8/u32/u64 values; missing bounds on new sysctls could expose invalid network behavior.

## Test signals
Tests should create and destroy network namespaces, read and write representative `/proc/sys/net/ipv6` values, verify per-netns isolation, check route and ICMP subtrees exist, validate min/max rejection for flowlabel reflect, auto flowlabels, multipath policy/fields, fib notify mode, and IOAM IDs, and confirm multipath hash writes emit `NETEVENT_IPV6_MPATH_HASH_UPDATE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/sysctl_net_ipv6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/tcp_ao.c -->
# sources/distributed-fs/ceph-client/net/ipv6/tcp_ao.c

## Purpose
`tcp_ao.c` provides IPv6-specific support for TCP Authentication Option (TCP-AO, RFC 5925). It derives IPv6 traffic keys, looks up matching master keys for sockets and requests, hashes IPv6 pseudoheaders and skbs, parses IPv6 AO socket options, and signs SYN-ACKs.

## Important APIs, types, and functions
`tcp_v6_ao_calc_key()` builds the AO KDF input block containing label `"TCP-AO"`, IPv6 source and destination addresses, ports, send/receive ISNs, and output length, then calls common `tcp_ao_calc_traffic_key()`. Wrappers adapt it to different contexts: `tcp_v6_ao_calc_key_skb()`, `tcp_v6_ao_calc_key_sk()`, and `tcp_v6_ao_calc_key_rsk()`.

Lookup helpers `tcp_v6_ao_lookup()` and `tcp_v6_ao_lookup_rsk()` choose the L3 master index and IPv6 peer address before calling common `tcp_ao_do_lookup()`. Hash helpers are `tcp_v6_ao_hash_pseudoheader()`, `tcp_v6_ao_hash_skb()`, and `tcp_v6_ao_synack_hash()`. `tcp_v6_parse_ao()` delegates socket option parsing to the common TCP-AO parser with `AF_INET6`.

## Control flow
Key derivation starts a TCP signature pool, writes a packed KDF input into the pool scratch buffer, asks common AO code to calculate the traffic key, and ends the pool. The socket wrapper swaps address/port and ISN order for receive direction. The request wrapper derives from `inet_request_sock` IPv6 local/remote addresses and TCP request ISNs.

For packet authentication, pseudoheader hashing writes IPv6 source, destination, TCP length, and protocol into the scratch buffer and updates the async hash request. Full skb hashing delegates to common AO skb hashing with `AF_INET6`. SYN-ACK hashing allocates a temporary traffic-key buffer, derives the request key, hashes the SYN-ACK skb, and frees the buffer.

## State and persistence
This file does not own long-lived AO key state. Keys live in common TCP-AO structures attached to sockets or time-wait/request state. Local state is temporary stack data, signature-pool scratch memory, and a temporary SYN-ACK hash buffer.

## Dependencies and integration points
It integrates with the common TCP-AO implementation, TCP signature pool, crypto ahash API, IPv6 socket/request structures, L3 master device lookup, and the TCPv6 ops tables in `tcp_ipv6.c`. The functions are selected through `tcp_sock_af_ops` and `tcp_request_sock_ops` when `CONFIG_TCP_AO` is enabled.

## Risks and edge cases
Send and receive key derivation must use the correct address/port/ISN orientation or peers will compute different traffic keys. L3 master index selection affects key matching for VRF-bound sockets. SYN-ACK hashing uses `GFP_ATOMIC`; allocation failure must cleanly abort authentication. The packed KDF input layout must remain consistent with RFC 5925 and common AO code. Temporary traffic keys must be freed on every exit path.

## Test signals
Tests should configure TCP-AO on IPv6 sockets, verify successful connection establishment, failed authentication with wrong keys or key IDs, VRF/l3mdev-specific key lookup, send and receive key directionality, SYN-ACK signing under request sockets, option parsing errors, and allocation-failure/error injection around signature pool and SYN-ACK key allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/tcp_ao.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/tcp_ipv6.c -->
# sources/distributed-fs/ceph-client/net/ipv6/tcp_ipv6.c

## Purpose
`tcp_ipv6.c` is the main TCP-over-IPv6 implementation. It registers the IPv6 TCP protocol handler and socket protocol, implements active connect, ICMPv6 error handling, SYN/SYN-ACK/request processing, reset and ACK generation, IPv4-mapped socket fallback, receive demultiplexing, child socket creation, optional MD5/TCP-AO hooks, `/proc/net/tcp6`, and per-net raw control sockets used for replies.

## Important APIs, types, and functions
Connection setup is handled by `tcp_v6_pre_connect()` and `tcp_v6_connect()`. Error handling uses `tcp_v6_err()`, `tcp_v6_mtu_reduced()`, and `inet6_csk_update_pmtu()`. Server-side setup uses `tcp_v6_init_req()`, `tcp_v6_route_req()`, `tcp_v6_conn_request()`, `tcp_v6_send_synack()`, `tcp_v6_syn_recv_sock()`, and `tcp_v6_cookie_check()`.

Packet responses are generated by `tcp_v6_send_response()`, `tcp_v6_send_reset()`, `tcp_v6_send_ack()`, `tcp_v6_timewait_ack()`, and `tcp_v6_reqsk_send_ack()`. Receive entry points are `tcp_v6_rcv()` and `tcp_v6_do_rcv()`. Socket and protocol ops are `ipv6_specific`, `ipv6_mapped`, optional `tcp_sock_ipv6_specific`, optional `tcp_sock_ipv6_mapped_specific`, `tcpv6_prot`, and `tcpv6_protosw`.

Optional authentication support includes MD5 key parsing/hash helpers under `CONFIG_TCP_MD5SIG` and TCP-AO function pointers under `CONFIG_TCP_AO`. Proc output is provided by `get_openreq6()`, `get_tcp6_sock()`, `get_timewait6_sock()`, `tcp6_seq_show()`, `tcp6_proc_init()`, and `tcp6_proc_exit()`.

## Control flow
Active `connect()` validates the sockaddr, handles flowlabel and link-local scope, rejects multicast, rewrites `::` to loopback, and supports IPv4-mapped destinations by switching AF ops/backlog/auth hooks to IPv4 and calling `tcp_v4_connect()`. Native IPv6 builds a `flowi6`, applies socket options and security classification, resolves a route, updates source address binding, stores the dst, sets extension-header overhead, initializes MSS clamp, hashes the socket into the bind/connect tables, chooses secure initial sequence and timestamp offset, and calls `tcp_connect()`. Failure unwinds TCP state, bind source, destination port, and route caps.

Inbound ICMPv6 errors look up the established socket, handle time-wait and request sockets, optionally ignore ICMPs protected by TCP-AO policy, check sequence validity, process redirects, update PMTU for Packet Too Big, handle SYN_SENT/SYN_RECV hard errors, and record soft or hard errors depending on socket ownership and `RECVERR6`.

Listen-side SYN processing rejects non-unicast IPv6 destinations and IPv4-mapped IPv6 sources, then delegates to common `tcp_conn_request()`. Request initialization stores IPv6 addresses, link-local ingress ifindex, packet options, and route data. SYN-ACK sending builds a TCP skb, calculates IPv6 checksum, reflects flowlabel/TOS where configured, includes MD5 or AO authentication when selected by request ops, and sends through `ip6_xmit()`.

`tcp_v6_rcv()` is the external protocol handler. It verifies host packet type, header length, checksum setup, socket lookup, xfrm policy, inbound authentication hash, filters, and fills TCP skb control block. It handles established sockets, listeners, new SYN-RECV request sockets, time-wait state, no-socket resets, checksum errors, backlog queuing, and reuseport migration. `tcp_v6_do_rcv()` is the socket-level receive path: it delegates IPv4 skbs to TCPv4 for mapped sockets, checks PSP policy, fast-paths established sockets into `tcp_rcv_established()`, handles listener syncookie promotion, runs state processing, and latches IPv6 packet options for userspace.

Child creation in `tcp_v6_syn_recv_sock()` enforces accept queue capacity, routes the request, creates an open-request child, copies IPv6 socket state and options, stores dst, initializes MSS and congestion-control state, copies MD5 or AO state, inherits the port, inserts into the established hash, and transfers saved packet options when this CPU owns the request.

## State and persistence
Long-lived state lives in `struct tcp6_sock`, embedded `struct ipv6_pinfo`, common TCP socket fields, request sockets, time-wait sockets, dst cache pointers, MD5/AO key storage, and per-net `net->ipv6.tcp_sk` raw control sockets. `/proc/net/tcp6` exposes live in-memory TCP state. No file-backed persistence exists. Synchronization uses socket locks, RCU lookups, refcounts, BH locking, request ownership rules, and per-net registration lifetime.

## Dependencies and integration points
This file integrates with the IPv6 protocol registry, INET6 socket layer, inet hash tables, route and dst cache code, xfrm policy, LSM security hooks, cgroup connect BPF, MPTCP, PSP policy, busy-poll/RPS, TCP common input/output/state code, syncookies, TCP MD5, TCP-AO, procfs seq iteration, pernet subsystem, ICMPv6, flowlabel handling, IPv4 TCP for mapped sockets, and net statistics.

## Risks and edge cases
IPv4-mapped transitions must restore IPv6 ops if IPv4 connect fails. Link-local connects require correct scope and bound-device checks. ICMP sequence validation must avoid accepting off-path errors while still handling Packet Too Big and redirects. Reset generation must not answer multicast/non-unicast traffic and must authenticate with MD5/AO when required. Request-socket and time-wait paths have delicate reference, lock, and skb control-block restoration rules. Child socket creation must avoid leaks when option duplication, authentication copy, or port inheritance fails. Proc dumping is lockless and must tolerate transient values. New auth or option features must be wired consistently into native IPv6 and mapped IPv4 ops.

## Test signals
Tests should cover native IPv6 connect, link-local scope, flowlabel reflection, IPv4-mapped connect success/failure, cgroup connect BPF rejection, listener SYN/SYN-ACK/accept, syncookie promotion, TFO paths, request overflow, ICMPv6 Packet Too Big and redirects, min-hopcount drops, no-socket reset behavior, MD5 and AO authenticated resets/ACKs/SYN-ACKs, time-wait ACK/RST transitions, reuseport migration, xfrm policy rejection, PSP policy rejection, packet option latching, `/proc/net/tcp6` output for established/request/timewait sockets, and per-net init/exit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/tcp_ipv6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/tcpv6_offload.c -->
# sources/distributed-fs/ceph-client/net/ipv6/tcpv6_offload.c

## Purpose
`tcpv6_offload.c` registers TCPv6 GRO and GSO callbacks. It lets the IPv6 stack coalesce inbound TCPv6 packets and segment outbound TCPv6 skbs, including fraglist GRO/GSO cases and checksum repair when segmented packets carry differing headers.

## Important APIs, types, and functions
`tcp6_gro_receive()` validates the TCPv6 GRO checksum, pulls the TCP header, optionally detects fraglist GRO eligibility with `tcp6_check_fraglist_gro()`, and delegates to common `tcp_gro_receive()`. `tcp6_gro_complete()` finalizes a GRO skb, marks `SKB_GSO_TCPV6`, computes the pseudoheader checksum, or marks fraglist GSO. `tcp6_gso_segment()` validates TCPv6 GSO, handles fraglist segmentation, fixes partial checksum state, and delegates to `tcp_gso_segment()`.

Fraglist-specific helpers are `tcp6_check_fraglist_gro()`, `__tcpv6_gso_segment_csum()`, `__tcpv6_gso_segment_list_csum()`, and `__tcp6_gso_segment_list()`. `tcpv6_offload_init()` installs the callbacks in `net_hotdata.tcpv6_offload` and registers them with `inet6_add_offload()`.

## Control flow
On GRO receive, the code avoids checksum work when a flush is already required. Otherwise it validates with `ip6_gro_compute_pseudo`, pulls the TCP header, checks whether a matching established socket exists for fraglist GRO, records `NAPI_GRO_CB(skb)->is_flist`, and passes the packet to generic TCP GRO.

On GRO completion, fraglist packets set `SKB_GSO_FRAGLIST | SKB_GSO_TCPV6`, copy the segment count, and mark checksum unnecessary. Non-fraglist packets write an inverted TCPv6 pseudoheader checksum, set TCPv6 GSO type, and run common TCP GRO completion.

On GSO, non-TCPv6 skbs and too-short headers fail. Fraglist GSO uses `skb_segment_list()` only when the skb layout matches the expected gso size and is not dodgy; otherwise checksum is forced back to software. If checksum state is not partial, the code builds the pseudoheader checksum before calling common TCP GSO. Segment-list checksum repair normalizes source/destination IPv6 addresses and TCP ports across later segments when they differ from the first segment.

## State and persistence
The file owns no persistent per-flow state. It initializes a global hotdata offload callback structure at boot/module init. Runtime state is in skb shared info, NAPI GRO control block fields, checksums, and temporary socket lookup references.

## Dependencies and integration points
It depends on generic GRO/TCP offload code, IPv6 pseudoheader checksum helpers, inet6 established socket lookup, NAPI GRO metadata, skb fraglist segmentation, `ip6_offload.h`, and the IPv6 offload registry. It is reached by device receive/transmit offload paths, not normal TCP socket code directly.

## Risks and edge cases
Fraglist GRO must not merge packets for an established socket that expects normal stream processing. Socket lookup references must be released. Checksum repair for segment lists must update IPv6 addresses and TCP ports exactly once per changed segment. The GSO path must reject malformed or non-TCPv6 skbs and avoid trusting dodgy fraglist layouts. Incorrect `gso_type` flags would hand incompatible skbs to drivers.

## Test signals
Tests should exercise TCPv6 GRO aggregation, GRO checksum failure flushing, fraglist GRO with and without established socket lookup, TCPv6 GSO with `CHECKSUM_PARTIAL`, GSO from software checksum state, fraglist GSO valid and dodgy layouts, NAT-like segment-list checksum repair for changed addresses/ports, and registration through `inet6_add_offload()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/tcpv6_offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/tunnel6.c -->
# sources/distributed-fs/ceph-client/net/ipv6/tunnel6.c

## Purpose
`tunnel6.c` is the generic IPv6 outer tunnel demultiplexer for IPv6-in-IPv6, IPv4-in-IPv6, and optional MPLS-in-IPv6. It lets tunnel implementations register prioritized handlers behind the IPv6 protocol numbers and provides ICMPv6 error dispatch plus optional xfrm input callbacks.

## Important APIs, types, and functions
Global RCU lists are `tunnel6_handlers`, `tunnel46_handlers`, and `tunnelmpls6_handlers`, protected for updates by `tunnel6_mutex`. Exported APIs `xfrm6_tunnel_register()` and `xfrm6_tunnel_deregister()` insert or remove `struct xfrm6_tunnel` handlers by address family and priority.

Receive functions are `tunnel6_rcv()`, `tunnel46_rcv()`, and `tunnelmpls6_rcv()`. Error dispatchers are `tunnel6_err()`, `tunnel46_err()`, and `tunnelmpls6_err()`. When `CONFIG_INET6_XFRM_TUNNEL` is enabled, `tunnel6_rcv_cb()` and `tunnel6_input_afinfo` integrate with xfrm input callbacks. Module lifecycle is `tunnel6_init()` and `tunnel6_fini()`.

## Control flow
Registration selects the handler list by family (`AF_INET6`, `AF_INET`, or `AF_MPLS`), walks it under the mutex, rejects duplicate priority, and inserts before the first lower-priority position. Deregistration finds the exact handler pointer, unlinks it, unlocks, and calls `synchronize_net()` so in-flight RCU readers complete before the handler can disappear.

Receive handlers first ensure enough bytes are present for the expected inner header, then walk the family-specific handler list under RCU. A handler consumes the skb by returning zero. If no handler accepts the packet, the code sends ICMPv6 destination-unreachable/port-unreachable and frees the skb. Error handlers similarly walk registered tunnel handlers until one accepts the error; otherwise they return `-ENOENT`.

Initialization registers IPv6 protocol handlers for `IPPROTO_IPV6`, `IPPROTO_IPIP`, and optional `IPPROTO_MPLS`, then registers xfrm input afinfo when configured. Failure unwinds previously registered protocols. Exit unregisters xfrm afinfo and all protocols, logging failures.

## State and persistence
State consists only of global in-memory RCU handler lists. Handler objects are owned by registering tunnel modules; this file owns list linkage and synchronization but not handler allocation. There is no persistence beyond module lifetime.

## Dependencies and integration points
The file integrates with `inet6_add_protocol()` / `inet6_del_protocol()`, ICMPv6 generation, xfrm tunnel handler structures, optional MPLS support, optional xfrm input afinfo, skb header pull helpers, RCU, and module export symbols used by tunnel drivers.

## Risks and edge cases
Priority collisions are rejected, so registering modules must coordinate priorities. Deregistration must pass the same family and handler pointer used at registration. Receive paths free skbs when no handler accepts them, so handlers must return zero only after taking ownership. MPLS protocol registration is conditional both on build support and runtime init branching. Error dispatch depends on each handler's `err_handler` being safe for the skb/error tuple.

## Test signals
Tests should register multiple mock tunnel handlers with different priorities, verify duplicate priority rejection, receive packets accepted by first matching handler, no-handler ICMPv6 unreachable generation, IPv4/IPv6/MPLS family separation, error-handler dispatch and `-ENOENT` fallback, deregistration with in-flight receive, and init failure unwind for protocol or xfrm afinfo registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/tunnel6.c -->
