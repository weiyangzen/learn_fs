<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ip_output.c -->
# sources/distributed-fs/ceph-client/net/ipv4/ip_output.c

## Purpose
Implements the IPv4 transmit path for locally generated packets: final header checksum and LOCAL_OUT/POST_ROUTING hooks, route-backed packet output, multicast/broadcast loopback, GSO and fragmentation handling, corked datagram assembly, skb construction from user/kernel buffers, and helper replies such as TCP reset/ack style unicast replies.

## APIs, Types, and Functions
Exported entry points include `ip_send_check()`, `__ip_local_out()`, `ip_local_out()`, `ip_build_and_send_pkt()`, `ip_output()`, `__ip_queue_xmit()`, `ip_queue_xmit()`, `ip_do_fragment()`, `ip_fraglist_init()`, `ip_fraglist_prepare()`, `ip_frag_init()`, `ip_frag_next()`, `ip_generic_getfrag()`, `ip_append_data()`, `__ip_make_skb()`, `ip_send_skb()`, `ip_push_pending_frames()`, `ip_flush_pending_frames()`, `ip_make_skb()`, `ip_send_unicast_reply()`, and `ip_init()`. Important local helpers are `ip_finish_output2()`, `ip_finish_output_gso()`, `__ip_finish_output()`, `ip_finish_output()`, `ip_mc_output()`, `ip_fragment()`, `__ip_append_data()`, `ip_setup_cork()`, `ip_cork_release()`, and `ip_reply_glue_bits()`.

## Control Flow
Transmit starts either from a prebuilt skb (`ip_local_out()`, `ip_output()`), a transport skb needing an IPv4 header (`__ip_queue_xmit()`), or corked data (`ip_append_data()` then `ip_push_pending_frames()`). The local path sets total length and checksum, applies L3 master handling, runs `NF_INET_LOCAL_OUT`, and then calls destination output. Post-routing output runs cgroup egress BPF and `NF_INET_POST_ROUTING`, handles multicast/broadcast loopback clones, resolves lightweight tunnels and neighbours, and emits through `neigh_output()`.

Large packets are processed by `__ip_finish_output()`: GSO skbs are either emitted directly if segment sizes fit the MTU or segmented and fragmented; non-GSO skbs exceeding MTU or carrying `frag_max_size` go through `ip_fragment()`. Fragmentation uses a fast `frag_list` path when geometry/headroom/share checks pass, otherwise allocates and copies fragments with `ip_frag_next()`. Corked sends accumulate skbs on a write queue, choose checksum/zerocopy/splice/page-frag modes, then `__ip_make_skb()` chains fragments, builds the final IPv4 header, assigns DF/TTL/TOS/ID/options, attaches the route, and releases cork state.

## State and Persistence
The file mostly mutates transient skb, cork, and socket state. Persistent or longer-lived state includes socket route capabilities (`sk_setup_caps()`), `inet->cork.base` fields and `sk_write_queue` until pushed or flushed, socket write-memory accounting, timestamp keys, dst references stolen into corks/skbs, IP statistics counters, neighbour confirmation, and peer/route/multicast initialization in `ip_init()`. Error paths update socket error queues through `ip_local_error()` and increment MIB discard/fragment failure counters.

## Dependencies and Integration
This code is a central integration point for routing (`rtable`, `dst_output`, `ip_route_output_flow()`), netfilter, cgroup BPF egress, L3 master devices, lightweight tunnels, XFRM reroute, neighbour/ARP output, socket corking, checksum and GSO helpers, zerocopy/splice page handling, ICMP PMTU feedback, IGMP multicast, and protocol callers such as TCP, UDP, raw sockets, ICMP, and tunnel modules.

## Risks
High-risk areas are MTU/DF interactions, fragment list validation and ownership transfer, checksum mode transitions, cork error unwinding, zerocopy reference accounting, route reference lifetime, timestamp key rollback, local multicast clone semantics, and subtle skb metadata copying across fragments. Recursion through XFRM/netfilter/lwtunnel and mixed GSO/fragmentation paths are especially sensitive to regressions.

## Test Signals
Useful signals include packetdrill or kselftest coverage for UDP corking, MSG_MORE, MSG_ZEROCOPY, MSG_SPLICE_PAGES, PMTU EMSGSIZE and ICMP generation, netfilter LOCAL_OUT/POST_ROUTING ordering, cgroup egress drops, multicast and broadcast loopback delivery, GSO over low-MTU paths, raw/IP options handling, and fragment counters (`FRAGOKS`, `FRAGFAILS`, `FRAGCREATES`). Runtime validation should inspect skb lengths, DF/MF/offset fields, checksums, route/device selection, and socket error queue contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ip_output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ip_sockglue.c -->
# sources/distributed-fs/ceph-client/net/ipv4/ip_sockglue.c

## Purpose
Provides IPv4 socket API glue: SOL_IP control-message send/receive handling, router-alert registration, ICMP/local error queue delivery, programmatic socket option setters, multicast membership/source-filter option handling, generic IP setsockopt/getsockopt dispatch, and packet-info preparation for receive side ancillary data.

## APIs, Types, and Functions
Exported APIs are `ip_cmsg_recv_offset()`, `ip_icmp_error()`, `ip_sock_set_tos()`, `ip_sock_set_freebind()`, `ip_sock_set_recverr()`, `ip_sock_set_mtu_discover()`, `ip_sock_set_pktinfo()`, `ip_setsockopt()`, and `ip_getsockopt()`. Key internal functions include `ip_cmsg_send()`, `ip_ra_control()`, `ip_local_error()`, `ip_recv_error()`, `do_ip_setsockopt()`, `do_ip_getsockopt()`, multicast helpers for `ip_msfilter`, `group_filter`, source membership, compat structures, and `ipv4_pktinfo_prepare()`. The file defines the `ip4_min_ttl` static key.

## Control Flow
Receive ancillary data is gated by `inet_cmsg_flags()` and emitted in likely-use order: packet info, TTL, TOS, received/return options, security label, original destination, checksum, and fragment size. Send control messages parse SOL_SOCKET, SOL_IP, and optional v4-mapped IPv6 pktinfo into `ipcm_cookie` fields before transport send. Error handling clones or allocates skbs, fills `sock_extended_err`, queues them to `sk_error_queue`, and `ip_recv_error()` later copies payload, offender address, timestamps, ancillary data, and `IP_RECVERR`.

`do_ip_setsockopt()` first handles options that can be toggled without the socket lock, then locks RTNL when multicast table state requires it and locks the socket for options that mutate IPv4 options, checksum conversion, multicast interfaces/memberships/source filters, and XFRM policy. `do_ip_getsockopt()` mirrors this by returning lockless scalar state when safe and locking for multicast filter queries. Netfilter gets a fallback chance for unknown non-excluded options.

## State and Persistence
State lives primarily in `inet_sock` bits and fields: TOS, TTL, multicast TTL/interface/address, pmtudisc, min TTL, local port range, receive flags, `inet_opt` RCU pointer, and unicast interface. Router alert state persists in `net->ipv4.ra_chain` under `ra_mutex` and is removed with RCU-delayed socket put. Error queues persist until read or purged. Multicast membership and source-filter state is delegated to IGMP helpers. The `ip4_min_ttl` static key is enabled when any socket sets a nonzero minimum TTL and is not disabled here.

## Dependencies and Integration
Integrates with the BSD socket API, cmsg helpers, user/compat copy helpers, IGMP multicast state, route/FIB lookup for pktinfo, security/LSM secctx conversion, timestamping error queues, XFRM policy sockets, multicast routing socket options, netfilter socket options, IPv6 compatibility for v4-mapped pktinfo and receive info, RTNL locking, and RCU-managed IP options.

## Risks
Risks include optlen compatibility mistakes, integer overflow in variable-size source-filter allocations, stale or incorrectly locked `inet_opt` changes affecting TCP MSS, inconsistent multicast interface validation with L3 master devices, error queue address offsets for short payloads, static key lifetime for `IP_MINTTL`, and security/capability checks around transparent bind and XFRM policy. Router-alert cleanup depends on RCU ordering and destructor behavior.

## Test Signals
Good tests exercise `setsockopt()` and `getsockopt()` for every scalar option with int and byte optlen forms, multicast join/leave and source-filter compat paths, `IP_PKTINFO`/`IP_RECVTTL`/`IP_RECVTOS` cmsgs, raw `IP_HDRINCL`, `IP_RECVERR` local and ICMP errors, `IP_RECVERR_RFC4884`, `IP_UNICAST_IF` with L3 masters, netfilter fallback options, and socket lock/RTNL lockdep coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ip_sockglue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ip_tunnel.c -->
# sources/distributed-fs/ceph-client/net/ipv4/ip_tunnel.c

## Purpose
Implements the generic IPv4 tunnel netdevice library used by concrete frontends such as IPIP, GRE-derived devices, and VTI. It manages per-net tunnel lookup tables, tunnel creation/deletion/update, common receive decapsulation checks, encapsulation operation registration, transmit routing/PMTU handling, ioctl and rtnetlink support, MTU/headroom calculation, and per-net fallback tunnel lifecycle.

## APIs, Types, and Functions
Exported APIs include `ip_tunnel_lookup()`, `ip_tunnel_rcv()`, `ip_tunnel_encap_add_ops()`, `ip_tunnel_encap_del_ops()`, `ip_tunnel_encap_setup()`, `ip_md_tunnel_xmit()`, `ip_tunnel_xmit()`, `ip_tunnel_ctl()`, `ip_tunnel_parm_from_user()`, `ip_tunnel_parm_to_user()`, `ip_tunnel_siocdevprivate()`, `__ip_tunnel_change_mtu()`, `ip_tunnel_change_mtu()`, `ip_tunnel_dellink()`, `ip_tunnel_get_link_net()`, `ip_tunnel_get_iflink()`, `ip_tunnel_init_net()`, `ip_tunnel_delete_net()`, `ip_tunnel_newlink()`, `ip_tunnel_changelink()`, `__ip_tunnel_init()`, `ip_tunnel_uninit()`, and `ip_tunnel_setup()`. Important state types are `struct ip_tunnel`, `struct ip_tunnel_net`, `struct ip_tunnel_parm_kern`, `struct ip_tunnel_encap`, `struct ip_tunnel_info`, and hash buckets keyed by remote/key.

## Control Flow
Receive frontends call `ip_tunnel_lookup()` with link, flags, remote/local/key. Lookup tries exact local+remote+key, wildcard local, local-only/multicast, wildcard fallback, metadata tunnel, then fallback device. `ip_tunnel_rcv()` validates checksum and sequence flags, decapsulates ECN, resets inner protocol/device context, attaches metadata dst when present, updates stats, scrubs cross-net packets, and hands the skb to GRO cells.

Transmit through `ip_tunnel_xmit()` derives an outer destination from configured params, tunnel metadata, inner IPv4 route, or IPv6-compatible neighbour; applies TOS/TTL inheritance; performs optional UDP/GUE/FOU-style encapsulation; uses per-tunnel or per-metadata dst cache when safe; blocks self-recursion to the same device; updates PMTU and sends ICMP/ICMPv6 feedback for oversized inner packets; then calls `iptunnel_xmit()`. `ip_md_tunnel_xmit()` is the metadata-only variant driven by `skb_tunnel_info()`.

Create/update paths allocate or register netdevices, bind them to an egress device to derive headroom and MTU, add/remove them from RCU hash tables, reset dst caches, and expose both legacy private ioctls and rtnetlink newlink/changelink/dellink operations.

## State and Persistence
Per-network-namespace state is held in `ip_tunnel_net`: hash buckets, fallback tunnel device, collect-metadata tunnel pointer, device type, and rtnl ops. Each `ip_tunnel` persists params, input sequence number, error count/time, fwmark, net pointer, dst cache, GRO cells, encap settings, headroom lengths, and collect-md mode. Hash membership is RCU-protected and modified under RTNL. Encapsulation ops live in the global `iptun_encaps` table using cmpxchg and `synchronize_net()`.

## Dependencies and Integration
The library depends on netdevice/rtnetlink, namespaces, RCU hlist traversal, routing, dst cache, neighbour lookup, XFRM policy callers, ECN helpers, GRO cells, ICMP/ICMPv6 PMTU reporting, metadata dst, tunnel encapsulation ops, l3mdev/link binding, and concrete rtnl link ops provided by frontend modules.

## Risks
Risks include ambiguous wildcard lookup precedence, collect-metadata singleton conflicts, RCU hash removal races, sequence-number wrap handling, PMTU calculations with Ethernet vs tunnel devices, route cache invalidation, tunnel recursion, metadata tunnel address-family mismatches, user/kernel tunnel parameter conversion overflow, MTU clamping, and cleanup of fallback devices across namespace teardown.

## Test Signals
Test with multiple tunnels differing by local/remote/key/link, wildcard and fallback devices, collect-md exclusivity, rtnetlink create/change/delete, legacy SIOC* ioctls, PMTU and ICMP generation for IPv4 and IPv6 payloads, TOS/TTL inheritance, UDP encapsulation ops, dst-cache invalidation after route/link changes, GRO receive, namespace create/destroy, and lockdep/RCU checks around concurrent lookup and deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ip_tunnel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ip_tunnel_core.c -->
# sources/distributed-fs/ceph-client/net/ipv4/ip_tunnel_core.c

## Purpose
Provides shared tunnel primitives not tied to one IPv4 tunnel netdevice: outer IPv4 header transmit, tunnel header pull/offload preparation, metadata reply construction, PMTU checking with synthetic ICMP/ICMPv6 replies for bridged tunnels, lightweight tunnel netlink state parsing/filling for IPv4 and IPv6 encap routes, metadata static-key accounting, protocol parsing, and common netlink parameter extraction.

## APIs, Types, and Functions
Exports the global encap operation tables `iptun_encaps` and `ip6tun_encaps`, plus `iptunnel_xmit()`, `__iptunnel_pull_header()`, `iptunnel_metadata_reply()`, `iptunnel_handle_offloads()`, `skb_tunnel_check_pmtu()`, `ip_tunnel_core_init()`, `ip_tunnel_metadata_cnt`, `ip_tunnel_need_metadata()`, `ip_tunnel_unneed_metadata()`, `ip_tunnel_parse_protocol()`, `ip_tunnel_header_ops`, `ip_tunnel_netlink_encap_parms()`, and `ip_tunnel_netlink_parms()`. Local lwtunnel handlers build/fill/compare `struct lwtunnel_state` containing `struct ip_tunnel_info` and options for Geneve, VXLAN GBP, and ERSPAN.

## Control Flow
`iptunnel_xmit()` enforces recursion limits, scrubs packets for cross-net transmission, installs a fresh outer IPv4 header, selects an ID, calls `ip_local_out()`, and updates tunnel tx stats. `__iptunnel_pull_header()` removes outer tunnel bytes, determines inner protocol including Ethernet payloads, clears VLAN/queue/hash state, scrubs, and normalizes offloads. `iptunnel_handle_offloads()` marks encapsulation and updates GSO type or disables risky checksum offload assumptions.

PMTU checking compares inner packet length against destination MTU minus headroom, updates PMTU, and when requested rewrites the original skb into an ICMPv4 fragmentation-needed or ICMPv6 packet-too-big response while avoiding invalid sources, multicast/broadcast, fragments, and ICMP error loops. LWT build functions parse nested netlink attributes, validate option families are not mixed, allocate state and dst caches, fill keys/options/flags, and later serialize or compare the same state.

## State and Persistence
Persistent state includes the global RCU encap op arrays, registered lwtunnel encap ops for `LWTUNNEL_ENCAP_IP` and `LWTUNNEL_ENCAP_IP6`, optional per-lwtunnel dst caches, and the `ip_tunnel_metadata_cnt` static key tracking whether metadata tunnel users exist. Most other state is transient skb rewriting, netlink parse output, and `ip_tunnel_info` instances stored in lwtunnel route state.

## Dependencies and Integration
Integrates with IPv4 output, dst/routing, lwtunnel infrastructure, static keys, Geneve/VXLAN/ERSPAN metadata formats, ICMP and ICMPv6, Ethernet header helpers, VLAN/offload/GSO helpers, XFRM/tunnel headers, netlink attribute policy validation, and frontend devices that use `ip_tunnel_header_ops` and metadata mode.

## Risks
Risk centers on destructive skb rewriting in PMTU reply builders, bounds validation of variable-length Geneve options, mutually exclusive option-family enforcement, checksum correctness for synthetic ICMPv6, recursion accounting balance, GSO/offload flag combinations, dst-cache lifetime in lwtunnel state, and memcmp-based lwtunnel comparison over fields that must remain fully initialized.

## Test Signals
Useful coverage includes lwtunnel route add/dump/compare for IPv4 and IPv6 encap, Geneve/VXLAN/ERSPAN option validation including malformed nesting and max option length, PMTU reply synthesis for bridged IPv4/IPv6 payloads, GSO and non-GSO offload transitions, tunnel recursion-limit drops, metadata static-key refcounting, and protocol parsing on valid/invalid IPv4/IPv6 network headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ip_tunnel_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ip_vti.c -->
# sources/distributed-fs/ceph-client/net/ipv4/ip_vti.c

## Purpose
Implements IPv4 Virtual Tunnel Interface devices for IPsec/XFRM. VTI maps inbound ESP/AH/IPComp/IPIP packets to tunnel netdevices, uses tunnel keys as policy marks, transmits inner IPv4/IPv6 packets through XFRM tunnel-mode states, handles ICMP errors for associated states, and exposes `vti` rtnetlink and legacy tunnel controls.

## APIs, Types, and Functions
The module is registered through `module_init(vti_init)` and `module_exit(vti_fini)`. Important functions are `vti_input()`, `vti_rcv()`, `vti_rcv_cb()`, `vti_state_check()`, `vti_xmit()`, `vti_tunnel_xmit()`, `vti4_err()`, `vti_tunnel_ctl()`, `vti_tunnel_init()`, `vti_init_net()`, `vti_netlink_parms()`, `vti_newlink()`, `vti_changelink()`, and `vti_fill_info()`. It registers `xfrm4_protocol` handlers for ESP, AH, and IPComp, optional `xfrm_tunnel` handlers for IPIP/IPIP6, `pernet_operations`, and `rtnl_link_ops` kind `vti`.

## Control Flow
Inbound protocol handlers set XFRM SPI metadata and call `vti_input()`, which looks up a keyless VTI tunnel by outer source/destination/link, checks inbound XFRM policy, stores the tunnel in `XFRM_TUNNEL_SKB_CB`, optionally switches `skb->dev`, and enters `xfrm_input()`. After XFRM decapsulation, `vti_rcv_cb()` validates inner mode/family, temporarily applies the tunnel input key as `skb->mark` for policy check, scrubs cross-net packets, assigns the tunnel device, and updates rx stats.

Transmit starts in `vti_tunnel_xmit()`, validates inner IPv4/IPv6, decodes an XFRM flow, overrides the mark with the tunnel output key, and calls `vti_xmit()`. `vti_xmit()` obtains or builds a route, performs `xfrm_lookup_route()`, verifies a tunnel-mode AF_INET state matches configured endpoints, checks MTU and sends ICMP/ICMPv6 errors when needed, then outputs through the XFRM dst. Error handling maps ICMP frag-needed and redirects back to XFRM state lookup using protocol SPI and output key mark.

## State and Persistence
Per-net tunnel state is supplied by the generic `ip_tunnel` library under `vti_net_id`, with fallback device `ip_vti0`. Tunnel keys persist in `parms.i_key` and `parms.o_key` and are used as policy marks rather than GRE keys on the wire. The module persists protocol registrations, optional tunnel handlers, rtnl link ops, fwmark, netdevice stats, and per-device dst retention through `netif_keep_dst()`.

## Dependencies and Integration
VTI sits between netdevices and XFRM: it depends on `ip_tunnel_lookup()`, pernet tunnel lifecycle, XFRM input/output/policy/state lookup, ESP/AH/IPComp headers, IPv4/IPv6 route decoding, ICMP/ICMPv6 PMTU reporting, rtnetlink, namespace capabilities, and legacy private ioctl conversion through `ip_tunnel_siocdevprivate()`.

## Risks
Risks include policy mark confusion between input and output keys, accepting packets for the wrong tunnel when endpoints are wildcarded, XFRM state mismatch causing blackholes, MTU handling for IPv6 minimums, SPI parsing from short ICMP payloads, registration unwind ordering, legacy GRE key compatibility conversion, and receive callback behavior when `x->sel.family` is unspecified.

## Test Signals
Tests should create VTI devices with local/remote/key/fwmark combinations, install matching and nonmatching XFRM tunnel states/policies, verify inbound ESP/AH/IPComp decapsulation and mark-based policy, transmit IPv4 and IPv6 inner packets, exercise PMTU and redirects, cover rtnetlink dump/change and SIOC tunnel controls, and validate namespace teardown plus module registration failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ip_vti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ipcomp.c -->
# sources/distributed-fs/ceph-client/net/ipv4/ipcomp.c

## Purpose
Registers IPv4 IP Payload Compression Protocol support for XFRM. It defines the IPv4 IPComp XFRM type, handles ICMP PMTU/redirect errors for compressed packets, initializes IPComp state including tunnel-mode companion IPIP state, and registers the protocol receive hooks.

## APIs, Types, and Functions
The module exposes itself through `module_init(ipcomp4_init)`, `module_exit(ipcomp4_fini)`, and `MODULE_ALIAS_XFRM_TYPE(AF_INET, XFRM_PROTO_COMP)`. Important functions are `ipcomp4_err()`, `ipcomp_tunnel_create()`, `ipcomp_tunnel_attach()`, `ipcomp4_init_state()`, and `ipcomp4_rcv_cb()`. Static registration objects are `ipcomp_type` (`xfrm_type`) and `ipcomp4_protocol` (`xfrm4_protocol`), with a `lock_class_key` for generated tunnel states.

## Control Flow
ICMP errors are filtered to fragmentation-needed and redirects, the CPI is converted into an XFRM SPI, and matching COMP state is looked up using skb mark, destination, SPI, protocol, and AF_INET. PMTU or redirect updates are then delegated to IPv4 route/XFRM helpers. State initialization allows transport mode directly and tunnel mode with extra IPv4 header length. Generic `ipcomp_init_state()` sets compression details; tunnel mode additionally attaches or creates a companion IPIP XFRM state under `xfrm_cfg_mutex`.

## State and Persistence
Registered XFRM type/protocol entries persist for the module lifetime. For tunnel mode, `x->tunnel` points to a companion IPIP `xfrm_state`; that state has copied selector, addresses, family, mode, flags, mark, if_id, initialized lock class, and incremented `tunnel_users`. State reference counts are deliberately held to represent tunnel use and are released by generic XFRM/IPComp destruction paths.

## Dependencies and Integration
Depends on XFRM type/protocol registration, generic IPComp input/output/destructor helpers, IPv4 ICMP route update helpers, XFRM state allocation/lookup/insert/reference handling, rtnetlink locking context, and the IPIP protocol model used as the tunnel wrapper for compressed tunnel-mode traffic.

## Risks
Risks include incorrect CPI-to-SPI mapping, companion tunnel state leaks or reference imbalance, unsupported mode handling, lock-class assumptions, PMTU updates with insufficient ICMP payload, and registration failure cleanup. Compression algorithm behavior and adaptive tuning are explicitly outside this file and noted as TODOs.

## Test Signals
Signals include XFRM state add/delete for IPComp transport and tunnel mode, failure paths for unsupported modes or missing companion state, compressed packet input/output, ICMP fragmentation-needed PMTU propagation, redirect handling, module load/unload registration order, and reference tracking of `tunnel_users`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ipcomp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ipconfig.c -->
# sources/distributed-fs/ceph-client/net/ipv4/ipconfig.c

## Purpose
Implements early boot IPv4 autoconfiguration for systems that need networking before userspace, especially NFS/CIFS root. It parses `ip=`, `nfsaddrs=`, `dhcpclass=`, and `carrier_timeout=` kernel parameters; opens candidate devices; obtains configuration via static parameters, DHCP, BOOTP, or RARP; applies interface address/netmask/broadcast/MTU and default route; records DNS/NTP/root-server data; and exposes boot configuration in proc files.

## APIs, Types, and Functions
Externally visible boot data includes `ic_set_manually`, `ic_proto_enabled`, `ic_myaddr`, `ic_gateway`, `ic_servaddr`, `root_server_addr`, and `root_server_path`; `root_nfs_parse_addr()` is exported for init-time root parsing. Major functions include `ic_open_devs()`, `ic_close_devs()`, `ic_setup_if()`, `ic_setup_routes()`, `ic_defaults()`, RARP handlers `ic_rarp_init()`, `ic_rarp_recv()`, `ic_rarp_send_if()`, BOOTP/DHCP handlers `ic_bootp_init()`, `ic_bootp_send_if()`, `ic_do_bootp_ext()`, `ic_bootp_recv()`, dynamic loop `ic_dynamic()`, proc helpers, `wait_for_devices()`, dispatcher `ip_auto_config()`, parser `ic_proto_name()`, and setup handlers registered with `__setup()`.

## Control Flow
Command-line parsing runs early and sets manual/static/dynamic choices. `ip_auto_config()` runs as a `late_initcall`: it initializes proc output, returns if disabled, waits for devices and deferred probes, opens loopback plus eligible non-loopback devices, waits for carrier, and decides whether dynamic discovery is needed because address/server data is missing or multiple devices are present. Dynamic discovery registers packet handlers, sends DHCP/BOOTP/RARP requests over capable devices with backoff, waits for `ic_got_reply`, handles DHCP offer-to-request-to-ack sequencing, and cleans packet handlers.

When data is available, it parses root server address from `root_server_path`, fills defaults such as hostname and classful netmask, records the protocol used, logs the chosen configuration, sets interface address/netmask/broadcast and optional MTU through devinet/netdevice ioctls, adds a default route if configured, and closes unselected devices except lower devices of the chosen stacked interface.

## State and Persistence
Most control variables are `__initdata` and disappear after init, including open device list, selected device pointer, protocol choices, DHCP identifiers, carrier timeout, receive lock, and reply flags. Persistent boot results include IP address, gateway, server/root addresses/path, nameservers, NTP servers, DNS domain, hostname/domainname updates, configured interface state, route table entries, and proc files `/proc/net/pnp` and `/proc/net/ipconfig/ntp_servers`. Dynamic packet reception is synchronized by `ic_recv_lock`.

## Dependencies and Integration
Integrates with early kernel init, root NFS/CIFS selection, netdevice registration/probing, RTNL, devinet ioctl address configuration, route ioctl, ARP/RARP packet type hooks, handcrafted BOOTP/DHCP packets sent through `dev_queue_xmit()`, procfs/seq_file, UTS namespace names, random transaction IDs, jiffies timers, and build-time protocol options `CONFIG_IP_PNP_DHCP`, `CONFIG_IP_PNP_BOOTP`, and `CONFIG_IP_PNP_RARP`.

## Risks
Risks include boot hangs or long delays waiting for carrier/devices, DHCP option parsing bounds and malformed replies, reliance on init_net only, fragmented BOOTP replies being unsupported, classful netmask guesses, static globals shared across retry loops, fallback DNS overwrite rules, device reopen behavior for root filesystems, proc creation before successful config, and command-line parsing ambiguity for empty fields or client identifiers.

## Test Signals
Validation can use QEMU or network namespaces with early userspace/rootfs simulations for static `ip=`, DHCP, BOOTP, RARP, multiple interfaces, no carrier, missing devices, NFS/CIFS retry-forever paths, root path server-prefix parsing, DHCP options for DNS/domain/root path/MTU/NTP/vendor/client ID, malformed replies, and proc output. Boot logs should confirm selected device, protocol, address, route, nameservers, NTP servers, and cleanup of nonselected devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ipconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ipip.c -->
# sources/distributed-fs/ceph-client/net/ipv4/ipip.c

## Purpose
Implements the concrete IPIP tunnel driver for IPv4-over-IPv4 and, when enabled, MPLS-over-IPv4. It registers the `ipip` rtnetlink kind and fallback `tunl0`, handles IPIP/MPLS receive and ICMP errors, validates tunnel protocols, drives generic tunnel transmit/receive helpers, supports collect-metadata and optional tunnel encapsulation attributes, and exposes forward-path information.

## APIs, Types, and Functions
The module initializes with `ipip_init()` and exits with `ipip_fini()`. Key functions are `ipip_err()`, `ipip_tunnel_rcv()`, `ipip_rcv()`, optional `mplsip_rcv()`, `ipip_tunnel_xmit()`, `ipip_tunnel_ctl()`, `ipip_fill_forward_path()`, `ipip_tunnel_setup()`, `ipip_tunnel_init()`, `ipip_tunnel_validate()`, `ipip_netlink_parms()`, `ipip_newlink()`, `ipip_changelink()`, `ipip_get_size()`, `ipip_fill_info()`, and pernet `ipip_init_net()`/`ipip_exit_rtnl()`. Static objects include `ipip_link_ops`, `ipip_handler`, optional `mplsip_handler`, `ipip_policy`, and module parameter `log_ecn_error`.

## Control Flow
Inbound packets arrive through XFRM tunnel handlers. `ipip_tunnel_rcv()` looks up a keyless tunnel by outer source/destination/link, validates configured protocol, checks XFRM inbound policy, pulls the outer header, optionally creates metadata dst for collect-md, resets the MAC header, and calls `ip_tunnel_rcv()` with IP or MPLS packet info. ICMP errors locate the reverse tunnel and update PMTU, process redirects, or record soft errors for connected tunnels.

Transmit validates the inner protocol, ensures it matches configured `tiph->protocol`, prepares offloads with `SKB_GSO_IPXIP4`, records inner IP protocol, and dispatches either metadata transmit or configured `ip_tunnel_xmit()`. Rtnetlink newlink parses generic tunnel params, encap params, collect metadata, and fwmark; changelink forbids switching to collect-md and enforces point-to-point flag consistency.

## State and Persistence
Per-net state is generic `ip_tunnel_net` under `ipip_net_id`, including fallback `tunl0`. Each tunnel stores configured IPv4 header params, encap settings, fwmark, collect-md flag, dst cache, error count/time, and device stats. The module persists XFRM tunnel registrations for AF_INET and optional AF_MPLS, rtnl link ops, pernet operations, and the `log_ecn_error` module parameter.

## Dependencies and Integration
Depends on the generic tunnel library, XFRM tunnel registration, rtnetlink, netdevice ops, IPv4 route/ICMP helpers, metadata dst, optional MPLS, tunnel offload/GSO helpers, netlink policies for `IFLA_IPTUN_*`, and legacy private ioctls through the generic tunnel control path.

## Risks
Risks include accepting malformed or mismatched protocol tunnel parameters, collect-md singleton conflicts handled in the generic layer, ECN error logging noise, short ICMP payloads limiting precise error relay, PMTU/redirect propagation to wrong link/protocol, offload handling for MPLS payloads, and changelink constraints around point-to-point versus wildcard tunnels.

## Test Signals
Tests should cover creating `ipip` and `tunl0` devices, configured and wildcard remote endpoints, IPv4 and MPLS payloads, collect-md mode, netlink dump/change validation, legacy SIOC add/change/delete, PMTU and redirect ICMP handling, ECN decapsulation logging, forward-path reporting, offloaded/GSO packets, namespace teardown, and module load/unload registration cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ipip.c -->
