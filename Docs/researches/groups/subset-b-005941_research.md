# subset-b-005941 research

Grouped source research for ceph-client networking headers. Each section preserves the original source path as its document title and is wrapped for reconciliation into mirrored per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ip6_fib.h -->
# sources/distributed-fs/ceph-client/include/net/ip6_fib.h

Purpose: Defines the IPv6 forwarding information base data model and exported lookup/update interfaces. It is the core contract between IPv6 route management, policy rules, neighbour/device state, notifier users, BPF route iterators, and route cache/dst users.

Important APIs/types/functions: `fib6_config` carries netlink route mutations, including table, metrics, source/destination prefixes, gateways, nexthop id, encapsulation, and FDB flags. `fib6_node`, `fib6_table`, `fib6_info`, `fib6_nh`, `rt6_info`, and `fib6_result` model the trie, tables, routes, nexthops, dst entries, and lookup result. Key APIs include `fib6_get_table`, `fib6_new_table`, `fib6_rule_lookup`, `fib6_lookup`, `fib6_table_lookup`, `fib6_select_path`, `fib6_node_lookup`, `fib6_locate`, `fib6_add`, `fib6_del`, notifier calls, GC functions, and rules helpers.

Control flow: Readers use RCU-protected trie/table traversal, perform table or rule lookup, then call selection helpers for multipath/nexthop choice. Writers add/delete `fib6_info` entries under table locks and update serial numbers/notifiers. Inline expiry helpers toggle `RTF_EXPIRES`; cookie helpers pair memory barriers with serial-number updates.

State and persistence: Route state is in per-net `fib6_table` hashes, trie nodes, route refcounts, per-route metrics, GC hlist links, sibling lists, exception buckets, and per-cpu dst caches. It is in-memory kernel state, reconstructed from configuration/control plane rather than persisted by this header.

Dependencies/integration: Depends on IPv6 route UAPI, `dst`, `flowi6`, IPv4 shared `fib_nh_common`, inet peers, nexthop objects, fib notifiers, netlink, RCU, BPF iterators, and optional IPv6 multiple-table/subtree/rules support.

Risks: Incorrect lock/RCU pairing can expose freed routes; missed refcounting around `fib6_info_hold_safe` can use stale entries; wrong GC list handling can leak routes or age exceptions incorrectly; source-subtree counters can desynchronize if increments/decrements are not paired. Test signals include IPv6 route add/delete/dump, policy rules, multipath, route expiry, PMTU exception GC, notifier consumers, BPF route iteration, and IPv6 disabled build stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ip6_fib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ip6_route.h -->
# sources/distributed-fs/ceph-client/include/net/ip6_route.h

Purpose: Declares IPv6 route lookup, route mutation, PMTU, redirect, default-router, and dst-cache helpers used by IPv6 input/output paths and socket code.

Important APIs/types/functions: `route_info` represents RA route information options. `RT6_LOOKUP_F_*` flags steer strict interface lookup, reachability, source-address preferences, link-state handling, and no-ref dst behavior. APIs include `ip6_route_input`, `ip6_route_input_lookup`, `ip6_route_output_flags`, `ip6_route_lookup`, `ip6_pol_route`, `ip6_route_add`, `ip6_ins_rt`, `ip6_del_rt`, `rt6_lookup`, `rt6_multipath_hash`, default-router helpers, PMTU/redirect handlers, route dump helpers, device sync functions, and `ip6_fragment`.

Control flow: Output callers build a `flowi6`, look up a dst, optionally store it in socket state through `ip6_dst_store`/`ip6_sk_dst_store_flow`, and use route cookies to detect invalidation. Input lookup and policy lookup feed `fib6_result`, then route selection and nexthop selection decide the dst. PMTU and redirect paths update exceptions under route state.

State and persistence: The header manipulates in-memory dst cache, socket cached destination cookies, route exceptions, MTU metrics, default-router entries, and uncached route lists. `ip6_route_get_saddr` may prefer route prefsrc if it belongs to the same L3 master, otherwise it asks address configuration for a source address.

Dependencies/integration: Integrates `ip6_fib.h`, `addrconf`, sockets, lwtunnel headroom, nexthop objects, L3 master devices, netlink dumps, neighbour lookup, and IPv6 fragmentation.

Risks: `RT6_LOOKUP_F_DST_NOREF` must match release behavior in `ip6_rt_put_flags`; PMTU calculations must subtract lwtunnel headroom; source selection can be wrong across VRFs; RA/default-router paths need lifetime and preference coverage. Test signals include route cache invalidation after route updates, socket dst reuse, VRF source selection, IPv6 forwarding MTU, PMTU exceptions, redirects, and IPv6-disabled fallback returning `-EAFNOSUPPORT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ip6_route.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ip6_tunnel.h -->
# sources/distributed-fs/ceph-client/include/net/ip6_tunnel.h

Purpose: Provides the shared IPv6 tunnel object model and encapsulation hooks for IP6 tunnel drivers, including GRE-specific sequence/header fields and metadata/dst cache support.

Important APIs/types/functions: `__ip6_tnl_parm` contains tunnel name, link, protocol, encapsulation limit, hop limit, collect-metadata mode, flowinfo, local/remote IPv6 endpoints, input/output flags and keys, fwmark, and ERSPAN fields. `ip6_tnl` binds parameters to a netdev, net namespace, flow template, dst cache, GRO cells, error state, GRE sequence state, header lengths, encapsulation parameters, and master link. `ip6_tnl_encap_ops` registers optional FOU/GUE-style encapsulation callbacks. APIs cover encapsulation registration/setup, receive/transmit admission, receive, transmit, TLV parsing, capability detection, link-net/iflink lookup, MTU changes, and `ip6tunnel_xmit`.

Control flow: Transmit checks recursion depth, clears IPv6 skb control block, sets flags, calls `ip6_local_out`, then records tunnel tx stats. Optional encapsulation looks up `ip6tun_encaps[type]` under RCU and invokes `encap_hlen` or `build_header`.

State and persistence: Tunnel state lives in per-net tunnel lists via `next`, netdev-private `ip6_tnl`, dst cache, GRO cells, error counters with timestamps, seqno atomics, and encapsulation configuration. It is volatile runtime configuration bound to netlink/device lifecycle.

Dependencies/integration: Uses generic `ip_tunnels.h`, IPv6 route/output, dst cache, GRO cells, netdevice trackers, and optional `CONFIG_INET`.

Risks: Recursion-loop protection is critical; RCU encapsulation operations must tolerate unregister races; MTU/headroom changes can break PMTU; sequence fields are GRE-only and must not be misused by other tunnel types. Test signals include tunnel xmit recursion drops, encap add/delete races, metadata collect mode, PMTU/MTU changes, GRE ERSPAN fields, and IPv6 tunnel receive capability filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ip6_tunnel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ip_fib.h -->
# sources/distributed-fs/ceph-client/include/net/ip_fib.h

Purpose: Defines the IPv4 FIB data structures, route lookup contracts, nexthop/common nexthop state, route-table operations, policy-rule hooks, multipath hashing, source validation, notifier events, and proc/dump helpers.

Important APIs/types/functions: `fib_config` is the netlink route-change description. `fib_nh_common` is shared by IPv4 and IPv6 nexthops and holds device, gateway, lwtunnel state, weight, per-cpu output routes, input route, and PMTU exceptions. `fib_nh`, `fib_info`, `fib_result`, `fib_table`, and notifier structures cover route sharing, trie lookup results, and hardware/offload events. APIs include `fib_table_lookup/insert/delete/dump/flush`, `fib_lookup`, rules helpers, `fib_validate_source`, device sync, MTU sync, multipath hash/path selection, nexthop init/release, trie table creation, and nexthop netlink encoding.

Control flow: `fib_lookup` chooses direct main/default table lookup or policy-rule lookup depending on `CONFIG_IP_MULTIPLE_TABLES` and per-net custom-rule state. Route results carry selected nexthop common state and are later refined by multipath selection. Early flow dissection populates ports/protocol only when rules require L4 keys.

State and persistence: In-memory per-net IPv4 route tables, route info refcounts, nexthop exception hash buckets, per-cpu route caches, metrics, route-class IDs, and notifier state are maintained by implementation files. This header exposes refcount transitions through `fib_info_hold/put`.

Dependencies/integration: Integrates with `flowi4`, fib rules/notifiers, inet DSCP, inetpeer, lwtunnel, L3 master devices, netlink route policies, nexthop objects, and procfs.

Risks: FIB lookup must run under the right RCU/rtnl context; no-ref lookups require callers not to retain routes unsafely; DSCP masked match affects route selection compatibility; multipath hash fields are UAPI and must remain append-only. Test signals include single/multiple table builds, route add/delete/dump, reverse-path/source validation, device down/up/MTU events, route exceptions, classid, and multipath hashing with configurable fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ip_fib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ip_tunnels.h -->
# sources/distributed-fs/ceph-client/include/net/ip_tunnels.h

Purpose: Provides generic IP tunnel types and helpers for IPv4-based tunnels and metadata/lwtunnel users, shared by GRE, SIT, VTI, ERSPAN, FOU/GUE, and tunnel offload paths.

Important APIs/types/functions: `ip_tunnel_key` stores tunnel id, IPv4/IPv6 endpoints, bitmap flags, label, nhid, TOS/TTL, transport ports, and flow flags. `ip_tunnel_info` wraps key, encapsulation, optional dst cache, mode, and options. `ip_tunnel`, `ip_tunnel_net`, `tnl_ptk_info`, and `ip_tunnel_parm_kern` define netdev tunnel state, per-net tunnel tables, parsed packet info, and kernel-side config. Helpers convert flags to/from legacy `__be16`, initialize keys/flows, test metadata/dst-cache usability, and copy options.

Control flow: Transmit code initializes `flowi4`, optionally builds an encapsulation header via RCU registered `iptun_encaps`, handles offloads, pulls headers, checks PMTU, and updates per-cpu tx stats. Receive helpers validate/pull IP headers, prepare VLAN/inner protocol offsets, and feed generic tunnel receive.

State and persistence: Runtime state includes tunnel hash tables, fallback and collect-metadata devices, dst caches, PRL entries, error timestamps/counts, sequence counters, ERSPAN fields, 6rd parameters, GRO cells, fwmark, collect-md, and ignore-DF. Static key `ip_tunnel_metadata_cnt` tracks metadata users.

Dependencies/integration: Uses netdevice, sk_buff, flow, DSCP/ECN, lwtunnel, dst cache, rtnetlink, gro cells, L3 master devices, optional IPv6 route helpers, page/offload APIs, and netns generic IDs.

Risks: Tunnel recursion is deliberately lower than generic xmit recursion due to stack usage; option flag bitmap/legacy conversion must preserve UAPI behavior; headroom is capped to avoid skb offset overflow; GSO encapsulation bits must be cleared correctly. Test signals include netlink create/change/delete, collect metadata, encap operation registration, PMTU replies, VLAN inner protocol pull, stats for success/error/drop, IPv4/IPv6 inner DS field inheritance, and offload/GSO paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ip_tunnels.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ip_vs.h -->
# sources/distributed-fs/ceph-client/include/net/ip_vs.h

Purpose: Defines the IP Virtual Server in-kernel API: packet header parsing, connection/service/destination state, schedulers, persistence engines, protocol modules, applications, sync daemon, estimators, resizable hash tables, sysctls, transmit methods, and conntrack hooks.

Important APIs/types/functions: `ip_vs_iphdr` abstracts IPv4/IPv6 packet metadata and extension-header parsing. `ip_vs_rht` provides RCU/seqcount-protected resizable hash tables. Core structs include `ip_vs_conn`, `ip_vs_service`, `ip_vs_dest`, `ip_vs_scheduler`, `ip_vs_pe`, `ip_vs_app`, `ip_vs_protocol`, `ip_vs_proto_data`, and `netns_ipvs`. APIs cover connection lookup/new/put/expire, service/dest lookup, scheduler bind/unbind, app and persistence registration, protocol init/cleanup, estimator management, sync daemon control, transmit variants, netns init/cleanup, hooks registration, and conntrack integration.

Control flow: Packet hooks parse IP headers, find or schedule a connection using protocol handlers, bind destinations and apps, then transmit by forwarding method: NAT, tunnel, direct route, bypass, local, or null. Resizable tables are walked under RCU and seqcount retry while resize may expose old/new tables. Timers expire conns/dests and estimator kthreads process stats in tick buckets.

State and persistence: Per-net `netns_ipvs` holds service and connection tables, protocol/app tables, real-server tables, stats, delayed works, sysctls, sync daemon state, estimator kthreads, hook masks, trash lists, and counters. Connections have timers, refcounts, flags, state, seq deltas, app data, PE data, and destination refs. All is runtime/netns state configured through IPVS control plane.

Dependencies/integration: Integrates Linux netfilter, conntrack, IPv4/IPv6 headers, checksum helpers, namespace lifecycle, workqueues, timers, RCU, modules, sysctl, housekeeping CPU masks, and user UAPI `linux/ip_vs.h`.

Risks: Refcount, timer, RCU, and resize interactions are high risk; conntrack confirmation can prevent redirecting old flows; mixed IPv4/IPv6 destinations affect sync; sysctl defaults must match behavior without `CONFIG_SYSCTL`; checksum delta helpers must use correct address family. Test signals include IPv4/IPv6 services, each forwarding method, scheduler modules, persistence templates, FTP/app helpers, conn table resize, sync master/backup, estimator start/stop/reload, conntrack on/off, and netns teardown with live conns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ip_vs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ipcomp.h -->
# sources/distributed-fs/ceph-client/include/net/ipcomp.h

Purpose: Declares the IPComp transform interface used by XFRM/IPsec compression processing and provides a header accessor for sk_buffs.

Important APIs/types/functions: The file forward-declares `ip_comp_hdr`, `netlink_ext_ack`, and `xfrm_state`. `ipcomp_input`, `ipcomp_output`, `ipcomp_destroy`, and `ipcomp_init_state` form the transform lifecycle: initialize compression state from netlink/XFRM config, compress/decompress packets, and release state. `ip_comp_hdr()` returns the transport header cast as an IPComp header.

Control flow: XFRM input/output implementation calls these functions after policy/state lookup. The inline accessor assumes the skb transport header already points at the IPComp header; it performs no validation itself.

State and persistence: Persistent transform state is owned by `struct xfrm_state` and the implementation. This header only exposes lifecycle hooks and carries no global state.

Dependencies/integration: Depends on sk_buff, XFRM state, and netlink extended ack reporting. It integrates with IPv4/IPv6 IPsec paths through XFRM rather than direct route/tunnel code.

Risks: Header pointer correctness is essential; callers must ensure linear/pulled transport header before casting. Compression state initialization needs clear extack errors for bad algorithms or unsupported parameters. Test signals include XFRM IPComp SA creation failure/success, packet input/output compression, malformed/truncated IPComp headers, transform destroy paths, and IPv4/IPv6 policy integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ipcomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ipconfig.h -->
# sources/distributed-fs/ceph-client/include/net/ipconfig.h

Purpose: Exposes early boot automatic IP configuration state for kernel components that need boot-time network identity and root-server information.

Important APIs/types/functions: External initdata-style variables include `ic_proto_enabled`, `ic_set_manually`, `ic_myaddr`, `ic_gateway`, `ic_servaddr`, `root_server_addr`, and `root_server_path`. Protocol bits include `IC_PROTO`, `IC_BOOTP`, `IC_RARP`, and `IC_USE_DHCP`.

Control flow: Boot-time IP configuration code sets the global variables based on kernel command line, BOOTP/DHCP, or RARP. Consumers can inspect whether protocols were enabled and whether addresses were manually supplied.

State and persistence: State is global early-boot configuration, not a per-net runtime table. Comments mark it as initdata-like, so lifetime is tied to early initialization decisions and boot root setup.

Dependencies/integration: Depends only on Linux fixed-width/network-endian types. Integrates with NFS-root boot paths and low-level IP autoconfiguration.

Risks: The header exposes globals without locking because intended use is early boot; late consumers must not assume these remain mutable runtime netns state. DHCP is represented as a bit layered on BOOTP protocol selection. Test signals include command-line IP configuration, BOOTP/DHCP/RARP selection, NFS-root server/path propagation, and manual-address precedence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ipconfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ipv6.h -->
# sources/distributed-fs/ceph-client/include/net/ipv6.h

Purpose: Main internal IPv6 networking header for constants, address helpers, fragmentation helpers, stats macros, router alert chain, flow labels, tx options, socket controls, input/output prototypes, extension-header parsing, multicast, proc/sysctl hooks, and small socket setters.

Important APIs/types/functions: Defines Next Header constants, address type/scope bits, extension-header limits, `frag_hdr`, fragmentation iterator/state structs, `ipv6_txoptions`, `ip6_flowlabel`, `ipcm6_cookie`, flowlabel helpers, address compare/prefix/hash helpers, flowlabel generation, header manipulation helpers, and prototypes for IPv6 receive, transmit, routing lookup, output, forwarding, datagram connect, socket options, error queues, multicast, proc/sysctl, and conversion helpers.

Control flow: Packet send paths build `ipcm6_cookie`, merge tx options/flow labels, select route/dst, append or build skb data, fragment if needed, then call IPv6 output. Receive paths enter `ipv6_rcv`, parse extension headers, route/input/forward, and deliver protocols. Inline helpers gate source binding, RA acceptance, PMTU behavior, and auto flowlabel generation via per-net sysctls.

State and persistence: State includes per-socket IPv6 options and flowlabel lists, refcounted `ipv6_txoptions`, global router-alert chain protected by rwlock, per-net MIB counters, sysctl-controlled limits, and flowlabel refcounts/expiration. Header-owned state is mostly declarations; storage lives in implementation/netns structs.

Dependencies/integration: Integrates with sk_buffs, sockets, flow dissector, inet DSCP, SNMP/MIB, addrconf, route code, multicast, procfs, sysctl, and optional IPv6 build stubs.

Risks: Address helper assumptions on prefix length and unaligned 64-bit access must hold; tx option refcounts use RCU and can leak/use-after-free if mishandled; extension-header limits are security-sensitive; flowlabel generation must avoid leaking useful hash data. Test signals include address classification, extension-header limit drops, fragmentation/fraglist, flowlabel socket options, source preference setters, multicast joins, error queue delivery, IPv6-only bind rules, and IPv6 disabled stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ipv6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ipv6_frag.h -->
# sources/distributed-fs/ceph-client/include/net/ipv6_frag.h

Purpose: Defines IPv6 reassembly queue metadata and inline helpers for fragment hash-table integration, expiration, and upper-layer-header truncation checks.

Important APIs/types/functions: `ip6_defrag_users` enumerates local delivery and conntrack bridge/input/output users, with high-offset variants for conntrack namespaces. `frag_queue` embeds `inet_frag_queue` and adds input ifindex, next-header offset, and ECN accumulation. `ip6frag_init`, key/object hash functions, compare function, `ip6frag_expire_frag_queue`, and `ipv6frag_thdr_truncated` are the core helpers.

Control flow: Reassembly creates queues keyed by `frag_v6_compare_key`; rhashtable uses the hash/compare helpers. Expiration locks the queue, marks drop, kills or flushes it, updates IPv6 reassembly failure/timeout stats, and sends ICMPv6 time exceeded only if the first fragment arrived and a head skb can be pulled. Truncation checking walks extension headers and verifies enough bytes exist for TCP/UDP/ICMP or at least one byte for unknown L4.

State and persistence: Fragment queues are in-memory per-frag-directory state with queue flags, locks, refs, ECN, ifindex, and skb trees. Expiration mutates flags and refs and frees the head skb.

Dependencies/integration: Depends on `inet_frag`, IPv6 extension parsing, ICMPv6, addrconf device stats, RCU device lookup, and skb drop reasons.

Risks: Expire path must avoid dead fqdir and hold/release refs correctly; head skb extraction is needed because skb `dev` aliases rbnode storage; ICMP should not be emitted for missing-first-fragment queues. Test signals include fragment timeout with and without first fragment, conntrack defrag users, truncated L4 first fragments, ECN accumulation, dead namespace/fqdir exit, and stats increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ipv6_frag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/iucv/af_iucv.h -->
# sources/distributed-fs/ceph-client/include/net/iucv/af_iucv.h

Purpose: Defines the AF_IUCV socket layer data structures for IBM s390 IUCV and HiperSockets transport, including socket states, wire transport header, send/receive queues, socket options, and skb control metadata.

Important APIs/types/functions: `sockaddr_iucv` names a VM guest user/application endpoint. `sock_msg_q` associates an `iucv_path`, message, list node, and lock. `af_iucv_trans_hdr` is the packed HiperSockets transport header with SYN/ACK/FIN/WIN/SHT flags, node/user/app identifiers, and embedded IUCV message metadata. `iucv_sock` embeds `struct sock` and stores endpoint names, accept queue, parent, path, HiperSockets device, send/backlog queues, message queue, tags, msg limits, counters, transport type, and tx notification callback. `iucv_skb_cb` stores class, tag, and receive offset.

Control flow: Socket code moves through open/bound/listen/connected/disconnect/closing/closed states. Data uses send and backlog skb queues plus message queue entries tied to IUCV path messages. HiperSockets packets use `iucv_trans_hdr()` over the skb network header.

State and persistence: Per-socket state includes path ownership, queue contents, message limits, counters, pending sends, and transport selection. `iucv_sock_list` holds bound sockets under rwlock with an autobind counter. State is volatile socket lifetime state.

Dependencies/integration: Depends on s390 IUCV base API, Linux sockets, sk_buffs, netdevice for HiperSockets, and poll/list/spinlock primitives.

Risks: Packed header layout is ABI-like for HiperSockets transport; queue and counter updates need lock/atomic correctness; message limit defaults are large and flow-control bugs can exhaust memory. Test signals include bind/listen/connect/disconnect, tx notification variants, IPRMDATA socket option, message limit enforcement, HiperSockets header parsing, and skb control block use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/iucv/af_iucv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/iucv/iucv.h -->
# sources/distributed-fs/ceph-client/include/net/iucv/iucv.h

Purpose: Declares the low-level s390 IUCV programming interface for registering handlers, establishing/quiescing/resuming/severing paths, and sending/receiving/replying/purging messages.

Important APIs/types/functions: Flags such as `IUCV_IPRMDATA`, `IUCV_IPQUSCE`, `IUCV_IPBUFLST`, `IUCV_IPPRTY`, `IUCV_IPANSLST`, `IUCV_IPSYNC`, and `IUCV_IPLOCAL` mirror CP function flags. `iucv_array` describes 31-bit address/length buffer lists. `iucv_path` stores path id, message limit, flags, private pointer, handler, and list node. `iucv_message` stores id, audit, class, tag, length, reply size, inline rmmsg, and flags. `iucv_handler` is the interrupt callback vector for path and message events. `iucv_interface` exports function pointers and bus/root device handles.

Control flow: Users register an `iucv_handler`; pending path interrupts are offered in registration order and accepted by calling `iucv_path_accept`. Connected paths receive complete, sever, quiesce, resume, message pending, and message complete callbacks. Message APIs support receive, reply, reject, send, send2way, and purge.

State and persistence: Runtime state lives in allocated `iucv_path` objects, handler path lists, IUCV device bus state, and CP-managed message/path ids. Inline allocation initializes message limit and flags; free is plain `kfree`.

Dependencies/integration: Depends on s390 DMA/address types, device model bus registration, debug support, kmalloc, and CP Programming Services semantics.

Risks: Positive return codes are CP-returned status rather than errno; callers must handle both. Callback order affects ownership of pending paths. Buffer-list flags require valid 31-bit DMA-addressable arrays. Test signals include handler registration/unregistration, path pending accept/reject ordering, quiesce/resume behavior, priority and synchronous sends, buffer-list receive/send, send2way reply completion, and purge audit propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/iucv/iucv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/iw_handler.h -->
# sources/distributed-fs/ceph-client/include/net/iw_handler.h

Purpose: Defines the kernel-only Wireless Extensions handler API used by legacy wireless drivers to expose ioctl handlers, request metadata, ioctl descriptions, spy data, and event stream helpers.

Important APIs/types/functions: `iw_request_info` carries command and flags such as compat ioctl mode. `iw_handler` is the generic handler signature. `iw_handler_def` lists standard and optional private handler arrays, private argument descriptions, and a `get_wireless_stats` hook. `iw_ioctl_description` describes header type, copy token size, min/max tokens, and flags such as event/restrict/no-max. `iw_spy_data` stores spy addresses, quality, and thresholds. APIs include `wireless_send_event`, optional `wireless_nlevent_flush`, and event stream add/check helpers.

Control flow: The wireless core validates/copies ioctl payloads using description metadata, indexes handler arrays by ioctl number, calls driver handlers, and interprets `EIWCOMMIT` as a delayed commit request. Event helpers append fixed events, point events, or values into caller-provided streams and compat-adjust lengths when needed.

State and persistence: Driver-owned static `iw_handler_def` describes capabilities. Per-device spy data and statistics are driver/device state. This header carries no global mutable state except external event flushing.

Dependencies/integration: Depends on `linux/wireless.h`, net_device, Ethernet address constants, compat event lengths, and net/wireless core implementation.

Risks: Legacy ioctl pointer/copy semantics are vulnerable if description metadata is wrong; compat 32/64 event sizes must be correct to avoid leaking kernel memory; private handler arrays can be misindexed. Test signals include standard/private ioctl dispatch, compat events, event truncation returning `-E2BIG`, spy threshold events, restricted GET permissions, and `EIWCOMMIT` handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/iw_handler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/kcm.h -->
# sources/distributed-fs/ceph-client/include/net/kcm.h

Purpose: Defines Kernel Connection Multiplexor internal socket, psock, mux, per-net, and statistics structures for multiplexing message-oriented KCM sockets over lower transport sockets parsed by strparser.

Important APIs/types/functions: `kcm_psock_stats`, `kcm_mux_stats`, and `kcm_stats` track tx/rx counters and attach/unattach/drop/retry events. `kcm_tx_msg` tracks partial transmit progress and fragments. `kcm_sock` embeds `struct sock` and holds mux membership, tx/rx psock pointers, wait lists, tx mutex, receive disable state, sequence skb, and stats. `kcm_psock` wraps a lower sock, `strparser`, saved callbacks, BPF parser, rx/tx owner KCM sockets, ready message, and stats. `kcm_net` and `kcm_mux` aggregate per-net and mux lists, locks, waiters, queues, and stats.

Control flow: KCM clients wait for available psocks for transmit and ready psocks for receive. Lower socket callbacks are replaced/saved by psock attach; strparser frames receive messages and BPF may parse boundaries. Aggregate helpers add psock/mux stats to retained totals during teardown.

State and persistence: State is in-memory socket/netns lifetime state: mux lists, psock lists, waiters, ready queues, held rx queue, callback replacement, stats, and done/unattaching flags. Proc init/exit optionally exposes stats.

Dependencies/integration: Depends on sockets, sk_buffs, strparser, UAPI KCM, BPF program pointer, mutex/spinlock/list/workqueue primitives, and procfs.

Risks: The comment warns not to use bitfields for flags set under different locks, highlighting lock-domain risk. Callback restoration, psock detach, and wait-list cleanup are sensitive. Test signals include attach/unattach, receive ready drops, tx wait/retry, partial tx fragments, mux teardown, procfs stats, BPF parser framing, and concurrent lower socket callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/kcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/l3mdev.h -->
# sources/distributed-fs/ceph-client/include/net/l3mdev.h

Purpose: Provides the L3 master device API used by VRF-like devices to steer FIB rules, route table lookup, link-scope IPv6 lookup, and L3 receive/output hooks.

Important APIs/types/functions: `l3mdev_type` currently defines VRF. `l3mdev_ops` supplies per-device callbacks for FIB table id, L3 receive, L3 output, and IPv6 link-scope lookup. APIs include table lookup registration, ifindex lookup by table id, FIB rule match, flow update, master ifindex/device lookup, table lookup by device/index, link-scope lookup, and IP/IP6 receive/output inline wrappers. Disabled builds return no-op or negative stubs.

Control flow: FIB rule matching compares `flowi_l3mdev` with input or output ifindex based on `FLOWI_FLAG_L3MDEV_OIF`. Flow update populates L3 master context. Receive wrappers select the master for L3 slaves or L3 rx-handler devices and invoke `l3mdev_l3_rcv`; output wrappers inspect dst device under RCU and invoke master output op for slaves.

State and persistence: The header does not own state; L3 master membership is in netdevice upper/lower relationships and per-device `l3mdev_ops`. Table lookup callbacks are registered per L3 type.

Dependencies/integration: Depends on `dst`, fib rules, netdevice L3 master/slave flags, RCU device lookup, IPv6 `flowi6`, and VRF implementation.

Risks: RCU device lookup must wrap master access; const removal in `l3mdev_master_dev_rcu` is intentional but must remain read-only; disabled stubs must not accidentally make rules match incorrectly. Test signals include VRF table lookup, input/output FIB rules, link-local IPv6 route lookup, L3 receive/output hooks, netdevice enslave/unenslave, and no-op behavior without `CONFIG_NET_L3_MASTER_DEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/l3mdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/lag.h -->
# sources/distributed-fs/ceph-client/include/net/lag.h

Purpose: Provides a tiny abstraction for determining whether a link aggregation port device is transmit-capable, hiding whether the port belongs to team or bonding.

Important APIs/types/functions: `net_lag_port_dev_txable()` checks `netif_is_team_port()` and calls `team_port_dev_txable()` for team ports; otherwise it calls `bond_is_active_slave_dev()` for bonding.

Control flow: Callers pass a lower/port net_device. The helper dispatches to the appropriate subsystem based on netdevice type, returning a boolean suitable for filtering eligible transmit ports.

State and persistence: No state is owned here. It reads team/bonding state from the net_device and respective subsystem helpers.

Dependencies/integration: Depends on netdevice, `linux/if_team.h`, and `net/bonding.h`. It integrates with drivers or core code that need generic LAG port eligibility.

Risks: The helper assumes non-team ports are bonding slaves; callers should only use it for known LAG ports. Misuse on unrelated devices can produce bonding-specific false results. Test signals include team active/inactive ports, bonding active/backup slave states, and callers avoiding non-LAG devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/lag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/lapb.h -->
# sources/distributed-fs/ceph-client/include/net/lapb.h

Purpose: Defines the internal Link Access Procedure Balanced control block, frame constants, state machine values, timers, queues, and helper prototypes for LAPB over network devices.

Important APIs/types/functions: Constants define LAPB I/S/U control frames, RR/RNR/REJ, SABM/SABME/DISC/DM/UA/FRMR, poll/final bits, FRMR error bits, command/response addresses, states 0-4, default mode/window/timers/retry count, and modulus values. `lapb_frame` stores decoded type, N(R), N(S), command/response, poll/final, and raw control bytes. `lapb_cb` stores netdev, mode, state, sequence variables, conditions, timers, queues, callback table, FRMR data, lock, and refcount.

Control flow: Interface callbacks notify connect/disconnect/data events. Input decodes frames and advances the state machine. Output kicks queued frames, establishes data link, sends enquiries/responses, retransmits, validates acknowledgements, and emits control/FRMR frames. Timers drive retransmission and delayed ACK behavior.

State and persistence: Per-link `lapb_cb` owns volatile protocol state: send/receive sequence counters, ack/write queues, timers, retry counts, window, state, and condition flags.

Dependencies/integration: Depends on public LAPB UAPI/callback definitions, net_device, sk_buff queues, timers, spinlocks, and refcounts.

Risks: Sequence/window validation and timer transitions are protocol-critical; queue cleanup/requeue must avoid skb leaks; debug macro currently prints only if level is below `LAPB_DEBUG`. Test signals include connect/disconnect handshakes, I-frame ack/reject paths, modulo-8/modulo-128 windows, T1/T2 expiry, FRMR generation, busy peer conditions, and queue cleanup on teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/lapb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/libeth/cache.h -->
# sources/distributed-fs/ceph-client/include/net/libeth/cache.h

Purpose: Supplies compile-time cacheline layout assertion macros for libeth data structures, especially structures split into read-mostly, read-write, and cold cacheline groups.

Important APIs/types/functions: `libeth_cacheline_group_assert` validates a named cacheline group size using `offsetof` and `offsetofend`; on 64-bit 64-byte-cacheline builds it requires exact size, otherwise less-than-or-equal. `libeth_cacheline_struct_assert` validates aggregate struct size and cacheline alignment. `libeth_cacheline_set_assert` checks read-mostly, read-write, cold groups and final struct size. Helper macros compute aligned sums for one to three groups.

Control flow: These are compile-time static assertions only. They run during compilation and produce build errors when structures drift from expected layout.

State and persistence: No runtime state. The macros enforce source-level layout contracts.

Dependencies/integration: Depends on Linux cache macros, `SMP_CACHE_BYTES`, static assertions, and local struct group naming convention `__cacheline_group_begin__*`/`end__*`.

Risks: Exact assertions only apply to 64-bit/64-byte cacheline builds, while other builds allow smaller/equal sizes; expected values must be updated intentionally when structure layouts change. Test signals are compile coverage on supported architectures and CI builds with `CONFIG_64BIT` and 64-byte cachelines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/libeth/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/libeth/rx.h -->
# sources/distributed-fs/ceph-client/include/net/libeth/rx.h

Purpose: Defines libeth receive-buffer management and packet-type metadata helpers for Ethernet drivers using page_pool, XDP, checksum/hash offloads, and descriptor-decoded packet types.

Important APIs/types/functions: Headroom and buffer sizing macros define SKB/XDP headroom, L2 overhead, maximum header size, order-0 pages, stride, and page length. `libeth_fqe` stores netmem, offset, and truesize. `libeth_fq` describes a fill queue with hotpath `libeth_fq_fp`, page pool, buffer array, count/truesize, type, header split, XDP flag, buffer length, and NUMA node. `libeth_rx_alloc`, `libeth_rx_sync_for_cpu`, and `libeth_rx_recycle_slow` manage buffers. `libeth_rx_pt`, `libeth_rx_csum`, and `libeth_rqe_info` decode packet type, checksum, and descriptor info.

Control flow: Queue creation prepares page_pool-backed buffers. `libeth_rx_alloc` allocates netmem and returns DMA address plus offset and page_pool offset. After hardware writes, `libeth_rx_sync_for_cpu` either recycles zero-length buffers or syncs DMA for CPU. Packet-type helpers decide IP version, checksum availability, hash availability, and set skb hash type.

State and persistence: State is per-queue runtime buffer state and descriptor metadata. Page_pool owns recycling; `libeth_fqe` tracks each buffer.

Dependencies/integration: Depends on VLAN, page_pool netmem helpers, XDP, net_device feature bits, pkt hash types, and IPv6 build option.

Risks: Zero-length buffer handling prevents processing stripped-FCS fragments; DMA sync offsets must match allocation offsets; IPv6 packet-type handling compiles out when IPv6 is disabled; checksum/hash helpers trust descriptor packet-type mapping. Test signals include page_pool allocation failure, zero-length recycle, XDP and SKB headroom, header split queues, checksum/hash feature toggles, IPv6-disabled builds, and packet-type hash generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/libeth/rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/libeth/tx.h -->
# sources/distributed-fs/ceph-client/include/net/libeth/tx.h

Purpose: Defines libeth transmit completion descriptors and common completion helpers for skb, fragments, slab buffers, XDP, and XSK transmit paths.

Important APIs/types/functions: `libeth_sqe_type` classifies send queue elements as empty/context, slab, frag, skb, XDP_TX, XDP_XMIT, XDP_XMIT_FRAG, XSK_TX, and XSK_TX_FRAG. `libeth_sqe` stores type, batch/report index, object union, DMA unmap address/length, fragment count, packet/byte stats, and driver-private scratch. `LIBETH_SQE_CHECK_PRIV` verifies private data fits. `libeth_cq_pp` bundles DMA device, XDP frame bulk, stats pointer, XDP count, and NAPI context. `libeth_tx_complete` handles common completion; `libeth_tx_complete_any` covers remaining/special types.

Control flow: Completion first unmaps DMA for skb/frag/slab types, then updates skb stats and consumes skb or frees slab memory. Other types fall through to specialized handling elsewhere. Every completed SQE is reset to `LIBETH_SQE_EMPTY`.

State and persistence: State is per-descriptor completion metadata and per-poll on-stack stats. No persistent global state.

Dependencies/integration: Depends on sk_buff, DMA mapping helpers, NAPI skb consumption, XDP frame bulk, libeth stats types, and driver queues.

Risks: Wrong `type` causes missed unmap/free or double-free; only common types update stats in the inline helper, so XDP/XSK paths must use `libeth_tx_complete_any`; driver-private data size must be asserted. Test signals include skb completion stats, frag-only unmap, slab free, empty/context no-op, NAPI/non-NAPI skb consume, XDP/XSK special completion, and SQE reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/libeth/tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/libeth/types.h -->
# sources/distributed-fs/ceph-client/include/net/libeth/types.h

Purpose: Defines common libeth hotpath stats and XDP queue helper structures shared by receive and transmit support code.

Important APIs/types/functions: `libeth_rq_napi_stats`, `libeth_sq_napi_stats`, and `libeth_xdpsq_napi_stats` are compact NAPI-loop counters with named fields and flexible-array raw aliases for bulk operations. `libeth_xdpsq_lock` represents a spinlock plus sharing flag for shared XDP send queues. `libeth_xdpsq_timer` stores queue pointer, lock pointer, and delayed work for lazy cleanup of non-interrupt XDP queues. `libeth_xdp_buff_stash` stores just the necessary `xdp_buff` fields to resume partially built frames: data pointer, headroom, len, frame size, and flags.

Control flow: Drivers embed these structs in queue state and pass them to libeth helpers. Stats are updated in NAPI poll/completion loops. Shared XDPSQs use the lock wrapper. Lazy cleanup timers schedule delayed work to free stale XDP buffers when queues do not interrupt.

State and persistence: All state is per-driver-queue runtime state. There are no globals. The stash is transient between NAPI polls.

Dependencies/integration: Depends on workqueue and spinlock primitives and is consumed by libeth RX/TX/XDP helpers.

Risks: The raw flexible-array aliases assume exact field layout for aggregation; timer cleanup must coordinate with queue locking; stashed XDP fields must be sufficient and kept in sync with XDP expectations. Test signals include stats aggregation by raw arrays, shared vs unshared XDPSQ locking, lazy cleanup delayed work, partial XDP buffer stash/restore, and structure size/alignment checks from libeth cache assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/libeth/types.h -->
