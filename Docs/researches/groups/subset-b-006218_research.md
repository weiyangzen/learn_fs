# subset-b-006218 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/udp.c -->
# sources/distributed-fs/ceph-client/net/ipv6/udp.c

## Purpose
Implements UDP over IPv6 for the kernel INET6 stack. It supplies the `IPPROTO_UDP` IPv6 protocol handler, the `SOCK_DGRAM` protocol switch, socket operations through `udpv6_prot`, `/proc/net/udp6` support, UDPv6 receive demultiplexing, multicast delivery, ICMPv6 error processing, corked and uncorked sends, IPv4-mapped fallback, GSO setup, GRO-related receive controls, UDP tunnel encapsulation hooks, and BPF/cgroup integration.

## Important APIs, types, and functions
Key exported/public entry points are `udp6_ehashfn`, `__udp6_lib_lookup`, `udp6_lib_lookup_skb`, `udp6_lib_lookup`, `udpv6_recvmsg`, `udpv6_encap_enable`, `udpv6_sendmsg`, `udpv6_rcv`, `udp_v6_early_demux`, `udp6_proc_init`, `udp6_proc_exit`, `udpv6_init`, and `udpv6_exit`. Socket behavior is registered through `struct proto udpv6_prot` and `struct inet_protosw udpv6_protosw`; receive path dispatch is registered in `net_hotdata.udpv6_protocol`. Important helpers include `compute_score`, `udp6_lib_lookup1/2/4`, `udpv6_queue_rcv_one_skb`, `__udp6_lib_mcast_deliver`, `udp6_csum_init`, `udp_v6_send_skb`, and `udp_v6_push_pending_frames`.

## Control flow
Inbound packets enter `udpv6_rcv`, which validates UDP header length, trims excess payload, accepts jumbograms, initializes checksum state, attempts early-demux socket stealing, handles multicast through `__udp6_lib_mcast_deliver`, and otherwise does unicast socket lookup. Socket delivery runs XFRM policy checks, optional encapsulation receive hooks, cBPF/eBPF socket filters, checksum conversion, queue accounting, and receive-buffer error handling. Missing unicast sockets pass XFRM policy and checksum checks before incrementing no-port stats and emitting ICMPv6 port unreachable.

Socket lookup first tries destination-address hash chains and optional four-tuple hash acceleration, then reuseport/BPF sk_lookup, wildcard sockets, and a primary-hash fallback for receive-address-change races. Send path in `udpv6_sendmsg` validates sockaddr inputs, diverts IPv4-mapped destinations to IPv4 UDP when allowed, parses control messages and flow labels, runs cgroup BPF sendmsg hooks, resolves route/options, then either builds one skb on the lockless fast path or corks with `ip6_append_data`. `udp_v6_send_skb` writes the UDP header, validates UDP GSO constraints, computes hardware or software checksums, and submits with `ip6_send_skb`.

## State and persistence behavior
State is in sockets, net namespace UDP tables, per-socket UDP cork state (`udp_sock.pending`, `len`, GSO size), IPv6 destination cache, receive queues, stats counters, and static branch keys. No durable persistence exists. `udpv6_destroy_sock` flushes corked frames, marks dead sockets, calls encapsulation destroy hooks, decrements UDP encapsulation static branches, and cleans tunnel GRO state. `/proc/net/udp6` is generated dynamically from socket hash iteration.

## Dependencies and integration points
Depends on IPv6 routing, address selection, raw/protocol dispatch, netfilter IPv6 hooks, XFRM policy/input, BPF cgroup hooks and sk_lookup, reuseport, UDP tunnel encapsulation, GRO/GSO helpers, procfs seq files, ICMPv6, Segment Routing destination extraction, and common IPv4 UDP tables. Integration with UDP tunnels is through `udp_sk(...)->encap_*` callbacks and `udpv6_encap_needed_key`.

## Risks and test signals
Risk centers on checksum handling, zero-checksum tunnel policy, address/port hash races, reuseport rescoring, socket refcounting from early demux, cork state recovery, GSO size validation, and ICMP error matching for tunnels with non-symmetric ports. Test signals include IPv6 UDP send/receive, IPv4-mapped behavior with and without `IPV6_V6ONLY`, multicast fanout, zero-checksum tunnel sockets, UDP GSO/GRO, cork/MSG_MORE, BPF sendmsg/sk_lookup rewrite, PMTU/ICMP errors, `/proc/net/udp6` visibility, packet drops with UDP MIB counters, and XFRM-policy rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/udp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/udp_offload.c -->
# sources/distributed-fs/ceph-client/net/ipv6/udp_offload.c

## Purpose
Provides IPv6 UDP offload registration for GSO/UFO and GRO. It bridges generic UDP segmentation/aggregation code with IPv6 pseudo-header checksums, IPv6 fragment-header insertion, UDP tunnel segmentation, and UDP encapsulation socket lookup for GRO.

## Important APIs, types, and functions
The registered callbacks are `udp6_ufo_fragment`, `udp6_gro_receive`, and `udp6_gro_complete`, installed by `udpv6_offload_init` into `net_hotdata.udpv6_offload` and removed by `udpv6_offload_exit`. Helper `udp6_gro_lookup_skb` locates UDP tunnel or normal UDP sockets for encapsulated GRO decisions.

## Control flow
`udp6_ufo_fragment` handles UDP tunnel GSO first, dispatches UDP L4 GSO to `__udp_gso_segment`, or performs software UFO for legacy `SKB_GSO_UDP`: it completes the UDP checksum, ensures headroom, finds the first fragmentable IPv6 option, inserts a fragment header by moving the unfragmentable header region, selects an identification value, then calls `skb_segment`. `udp6_gro_receive` validates or converts UDP checksums unless the packet is already marked for flush, optionally looks up encapsulation sockets when `udpv6_encap_needed_key` is active, and delegates to `udp_gro_receive`. `udp6_gro_complete` finalizes fraglist or normal GRO packets, setting UDP length, GSO metadata, and pseudo-header checksum before calling `udp_gro_complete`.

## State and persistence behavior
No persistent state is owned. The file mutates per-packet skb headers, checksum flags, `skb_shinfo()` GSO metadata, and NAPI GRO control block fields. The only longer-lived state is the global IPv6 offload callback slot registered at init.

## Dependencies and integration points
Depends on `inet6_add_offload`, `inet6_del_offload`, generic UDP GRO/GSO, UDP tunnel GSO, IPv6 checksum helpers, `ip6_find_1stfragopt`, fragment header layout, and socket lookup from `udp.c`. It integrates with ESP-in-UDP indirectly because GRO socket lookup can find tunnel encapsulation sockets.

## Risks and test signals
Important risks are incorrect header movement when adding the fragment header, checksum mistakes around zero or converted checksums, tunnel-vs-plain GSO dispatch errors, and GRO completion metadata that confuses later segmentation. Test with UDPv6 GSO, UDP tunnel GSO, fraglist GRO, checksum-offload and software-checksum devices, packets with extension headers before the fragmentable region, and unregister/re-register paths during IPv6 stack teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/udp_offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/xfrm6_input.c -->
# sources/distributed-fs/ceph-client/net/ipv6/xfrm6_input.c

## Purpose
Implements IPv6-specific XFRM inbound glue for IPsec and related transforms. It marks IPv6 SPI lookup metadata, handles transport-mode finish and netfilter reinjection, decapsulates ESP-in-UDP for IPv6 including GRO support, receives tunnel packets, and exposes an address-based state lookup path.

## Important APIs, types, and functions
Exports `xfrm6_rcv_spi`, `xfrm6_rcv_tnl`, `xfrm6_rcv`, and `xfrm6_input_addr`. UDP encapsulation entry points are `xfrm6_udp_encap_rcv` and `xfrm6_gro_udp_encap_rcv`. Transport completion is split across `xfrm6_transport_finish` and `xfrm6_transport_finish2`.

## Control flow
`xfrm6_rcv_spi` records tunnel and IPv6 destination-offset metadata in skb control blocks, then calls generic `xfrm_input`. `xfrm6_transport_finish` restores the next-header byte from XFRM mode state, pushes network header bytes back, updates payload length and receive checksum, and either returns to GRO/L2 reinjection or runs the IPv6 pre-routing netfilter hook before `ip6_rcv_finish`.

`__xfrm6_udp_encap_rcv` inspects a UDP-encapsulated payload, eats NAT keepalives, lets IKE packets continue through UDP, identifies ESP packets, unclones the skb, reduces IPv6 payload length, and either pulls UDP/non-ESP-marker bytes or advances the transport header. `xfrm6_udp_encap_rcv` then calls `xfrm6_rcv_encap` for ESP. GRO handling finds ESP offload callbacks, rejects keepalive/IKE-looking payloads, marks UDP as the outer protocol, and calls ESP GRO receive.

`xfrm6_input_addr` allocates or extends the skb security path, tries exact, wildcard-source, then wildcard-address state lookup, rejects wrong-direction SAs, checks validity/expiry under state lock, invokes transform input, records the accepted state in `sec_path`, and updates lifetime byte/packet counters.

## State and persistence behavior
State changes live in skb control blocks, secpath vectors, XFRM state refcounts, state lifetime counters, and IPv6 header fields after UDP decapsulation. No disk persistence exists. A successful `xfrm6_input_addr` holds a state reference by storing it in `sp->xvec`.

## Dependencies and integration points
Depends on generic XFRM input, XFRM state DB, secpath management, netfilter IPv6 pre-routing, ESP offload registration in `inet6_offloads`, UDP encapsulation sockets from UDPv6, IPv4 fallback for IPv4 packets on dual-stack sockets, GRO infrastructure, and IP6 tunnel metadata.

## Risks and test signals
Risks include mishandling keepalive/IKE vs ESP detection, incorrect payload-length adjustment, unclone failure, secpath depth overflow, accepting wrong-direction SAs, and GRO packets losing L2 header context. Test ESP-in-UDP receive, NAT keepalives, IKE pass-through, transport-mode netfilter policy, tunnel receive, wildcard XFRM state lookup, invalid/expired SA rejection, GRO ESP-in-UDP, and XFRM MIB/audit counters on state misses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/xfrm6_input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/xfrm6_output.c -->
# sources/distributed-fs/ceph-client/net/ipv6/xfrm6_output.c

## Purpose
Supplies IPv6-specific XFRM outbound handling, including local PMTU/error reporting, post-routing netfilter integration, tunnel-mode fragmentation decisions, and final handoff to generic `xfrm_output`.

## Important APIs, types, and functions
Public functions are `xfrm6_local_rxpmtu`, `xfrm6_local_error`, and `xfrm6_output`. Internal helpers are `__xfrm6_output_finish`, `xfrm6_noneed_fragment`, and `__xfrm6_output`.

## Control flow
`xfrm6_output` wraps outbound packets in `NF_HOOK_COND` for IPv6 post-routing unless the packet has already been rerouted. `__xfrm6_output` handles the callback. If netfilter rerouted a packet and there is no XFRM state, it marks `IP6SKB_REROUTED` and calls normal `dst_output`. For tunnel-mode XFRM, it selects the correct MTU source, detects non-GSO oversize packets, reports local PMTU if DF behavior requires it, permits a narrow fragment-header case for ESP/AH by setting `ignore_df`, returns local errors for sockets, or fragments with `ip6_fragment` before continuing to `xfrm_output`.

## State and persistence behavior
Only per-packet state is changed: skb flags, `ignore_df`, ICMP/PMTU reporting to socket state, and netfilter routing flags. No persistent state is owned.

## Dependencies and integration points
Depends on IPv6 routing MTU helpers, `dst->xfrm`, generic XFRM output, IPv6 fragmentation, netfilter post-routing, ICMPv6 local error helpers, and socket path-MTU settings. It is the outbound peer of the IPv6 XFRM policy and protocol files.

## Risks and test signals
Risks are PMTU regressions, double post-routing after reroute, fragmenting packets that should report EMSGSIZE, and mishandling pre-existing fragment headers around ESP/AH. Test tunnel and transport mode IPsec, GSO vs non-GSO oversize packets, `IPV6_DONTFRAG`/PMTU settings, post-routing netfilter reroute, local EMSGSIZE delivery, and ESP/AH packets already carrying fragment headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/xfrm6_output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/xfrm6_policy.c -->
# sources/distributed-fs/ceph-client/net/ipv6/xfrm6_policy.c

## Purpose
Registers IPv6 address-family support for generic XFRM policy and destination handling. It provides route lookup, source address selection, transformed destination population/destruction, PMTU/redirect forwarding to underlying routes, per-net sysctl setup, and IPv6 XFRM init/teardown orchestration.

## Important APIs, types, and functions
Key structures are `xfrm6_dst_ops_template`, `xfrm6_policy_afinfo`, and `xfrm6_net_ops`. Important functions include `xfrm6_dst_lookup`, `xfrm6_get_saddr`, `xfrm6_fill_dst`, `xfrm6_update_pmtu`, `xfrm6_redirect`, `xfrm6_dst_destroy`, `xfrm6_dst_ifdown`, `xfrm6_net_init`, `xfrm6_net_exit`, `xfrm6_init`, and `xfrm6_fini`.

## Control flow
Policy lookup uses `xfrm6_dst_lookup` to build a `flowi6` from XFRM lookup params, including l3mdev, mark, addresses, protocol, and ULI fields, then calls `ip6_route_output` and returns either the route or its error. Source selection performs the same route lookup, obtains the IPv6 device, and calls `ipv6_dev_get_saddr`. Destination fill copies IPv6 route flags, gateway, destination/source route entries, route cookie, device ref, and idev ref into `xfrm_dst`, then adds it to the IPv6 uncached route list.

Net namespace initialization copies destination ops from the template, randomizes the secret, initializes sysctl when enabled, and registers pernet operations. Global init registers AF policy info, initializes protocol handlers, registers tunnel handlers for ESP/AH/IPCOMP, and unwinds in reverse on failure.

## State and persistence behavior
Per-net state includes `net->xfrm.xfrm6_dst_ops`, sysctl header/table storage, route operation secret, and destination GC threshold. XFRM destination objects hold device and `inet6_dev` references and uncached-route membership. No persistent storage exists.

## Dependencies and integration points
Depends on IPv6 route output, addrconf source selection, l3mdev, XFRM policy core, XFRM protocol/tunnel registration, sysctl, pernet operations, and IPv6 blackhole routing. `xfrm6_dst_ifdown` integrates with network-device teardown by switching affected idev references to loopback.

## Risks and test signals
Risks include route/device ref leaks, sysctl table lifetime bugs in non-init netns, uncached route list imbalance, wrong l3mdev/mark propagation, and init unwind mismatches. Test IPsec policy routing in multiple netns and VRFs, `xfrm6_gc_thresh` sysctl, interface down events with active XFRM routes, PMTU/redirect propagation, source address selection, and init failure injection around protocol/tunnel registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/xfrm6_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/xfrm6_protocol.c -->
# sources/distributed-fs/ceph-client/net/ipv6/xfrm6_protocol.c

## Purpose
Registers IPv6 protocol handlers for ESP, AH, and IPCOMP and provides chained handler registration for protocol-specific XFRM modules. It also supplies the IPv6 `xfrm_input_afinfo` callback used by generic XFRM receive.

## Important APIs, types, and functions
Exports `xfrm6_rcv_encap`, `xfrm6_protocol_register`, and `xfrm6_protocol_deregister`. Init/exit functions are `xfrm6_protocol_init` and `xfrm6_protocol_fini`. Static protocol descriptors are `esp6_protocol`, `ah6_protocol`, `ipcomp6_protocol`, and `xfrm6_input_afinfo`; handler lists are RCU pointers `esp6_handlers`, `ah6_handlers`, and `ipcomp6_handlers`.

## Control flow
Inbound ESP/AH/IPCOMP packets enter small protocol wrappers that pass the skb, protocol number, SPI, and encapsulation type into `xfrm6_rcv_encap`. That function walks the RCU handler chain for the protocol and calls each handler's callback until one consumes the packet. On failure it frees the skb and returns an error. Error handlers walk the same chain via `xfrm6_rcv_cb`, allowing modules to react to ICMPv6 errors.

Registration is serialized by `xfrm6_protocol_mutex`. A new handler is prepended only if the same callback is not already present, then the corresponding `inet6_protocol` is installed if needed. Deregistration unlinks the exact handler, unregisters the inet6 protocol when the list becomes empty, and waits for an RCU grace period.

## State and persistence behavior
Persistent runtime state is limited to the three RCU handler chains and installed inet6 protocol registrations. No disk state exists. Handler lifetime relies on module-level deregistration plus `synchronize_net`.

## Dependencies and integration points
Depends on IPv6 protocol registration, generic XFRM input AF registration, ESP/AH/IPCOMP modules registering `struct xfrm6_protocol`, RCU, and mutex serialization. It is initialized from `xfrm6_policy.c` and receives UDP-encapsulated ESP from `xfrm6_input.c`.

## Risks and test signals
Risks include duplicate handler registration, unregistering while readers are active, missing protocol deletion when the last handler leaves, and incorrect ICMP error propagation. Test module load/unload for ESP/AH/IPCOMP, inbound plain and UDP-encapsulated ESP, AH/IPCOMP receive, ICMPv6 errors to active SAs, concurrent traffic during deregistration, and error unwind from partial init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/xfrm6_protocol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/xfrm6_state.c -->
# sources/distributed-fs/ceph-client/net/ipv6/xfrm6_state.c

## Purpose
Provides IPv6-specific XFRM state address matching operations. This is a small AF adapter used by generic XFRM state management to compare IPv6 addresses and prefix lengths.

## Important APIs, types, and functions
Defines `xfrm6_state_addr_cmp`, `xfrm6_state_addr_check`, and `xfrm6_state_afinfo`. The AF info binds `.family = AF_INET6`, `.proto = IPPROTO_IPV6`, and the two address callbacks.

## Control flow
`xfrm6_state_addr_cmp` calls `ipv6_prefix_equal` for destination and source address pairs using the selector prefix lengths, returning mismatch on either failed comparison. `xfrm6_state_addr_check` calls the same comparator for state properties and selector values.

## State and persistence behavior
No state is allocated or persisted. It only reads `struct xfrm_tmpl`, `struct xfrm_state`, and `struct flowi` address fields.

## Dependencies and integration points
Depends on generic XFRM state core and IPv6 prefix comparison helpers. The `xfrm6_state_afinfo` object is consumed by IPv6 XFRM initialization elsewhere in the stack.

## Risks and test signals
The main risk is incorrect selector matching for non-/128 prefixes or swapped source/destination checks. Test with IPv6 IPsec policies using exact and prefix selectors, wildcard source/destination states, and flows that differ only outside selector prefix length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/xfrm6_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/xfrm6_tunnel.c -->
# sources/distributed-fs/ceph-client/net/ipv6/xfrm6_tunnel.c

## Purpose
Implements IPv6 XFRM tunnel SPI dispatch for tunnel-mode security protocols. It maintains per-net hash tables mapping SPI and remote address to tunnel handlers, supports wildcard fallback, exposes register/deregister APIs for tunnel protocol handlers, and registers ESP/AH/IPCOMP tunnel receive adapters.

## Important APIs, types, and functions
Exports `xfrm6_tunnel_register` and `xfrm6_tunnel_deregister`. Important routines include `xfrm6_tunnel_spi_lookup`, `xfrm6_tunnel_input`, `xfrm6_tunnel_rcv`, `xfrm6_tunnel_err`, `xfrm6_tunnel_init`, and `xfrm6_tunnel_fini`. Static protocol descriptors are `xfrm6_tunnel_esp`, `xfrm6_tunnel_ah`, and `xfrm6_tunnel_ipcomp`.

## Control flow
Handlers are stored per net namespace in two hash tables: one for exact remote address/SPI and one for priority-ordered wildcard handlers. Lookup first hashes the source address and SPI, then falls back to wildcard entries. Receive entry `xfrm6_tunnel_input` extracts SPI from the protocol header, finds a handler, calls it, or discards the skb and increments no-state stats. Protocol-specific wrappers pass ESP/AH/IPCOMP IDs to the common receive path and route errors to matching handler error callbacks when available.

Registration allocates an `xfrm6_tunnel_net`, inserts exact or wildcard handlers under lock, and uses priority ordering for wildcard entries. Deregistration removes the matching handler and frees the node after RCU grace protection.

## State and persistence behavior
State is per-net handler registration data, protected by locks and RCU. No persistent disk state exists. Lifetime is tied to network namespaces and protocol module registration.

## Dependencies and integration points
Depends on XFRM protocol registration from `xfrm6_protocol.c`, pernet operations, IPv6 address hashing/comparison, XFRM stats, RCU, and tunnel modules that provide `struct xfrm6_tunnel` callbacks. It integrates with inbound IPsec tunnel packets after protocol dispatch.

## Risks and test signals
Risks include handler ordering mistakes for wildcard tunnels, stale RCU nodes after deregistration, SPI/address hash collisions, and error callback routing to the wrong tunnel. Test exact and wildcard tunnel handlers, multiple priorities, handler unregister under traffic, ESP/AH/IPCOMP tunnel receive, ICMPv6 error callbacks, and per-net namespace isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/xfrm6_tunnel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/iucv/Kconfig -->
# sources/distributed-fs/ceph-client/net/iucv/Kconfig

## Purpose
Defines build-time configuration for S390 IUCV support and AF_IUCV sockets. It gates low-level z/VM Inter-User Communication Vehicle support and the socket-facing AF_IUCV protocol including HiperSockets transport.

## Important APIs, types, and functions
Configuration symbols are `CONFIG_IUCV` and `CONFIG_AFIUCV`. `IUCV` depends on `S390`, defaults to built-in on S390, and prompts for z/VM-only IUCV support. `AFIUCV` depends on `S390`, defaults to module when `QETH_L3` or `IUCV` is enabled, and enables AF_IUCV socket applications.

## Control flow
There is no runtime control flow. Kconfig controls whether `iucv.o` and/or `af_iucv.o` can be built by the Makefile and whether AF_IUCV may use classic IUCV, HiperSockets, or both at runtime.

## State and persistence behavior
State is kernel build configuration only. It affects compiled objects and module availability, not runtime persistence.

## Dependencies and integration points
Integrates with S390 architecture support, z/VM, QETH L3 HiperSockets, and the `net/iucv/Makefile`. Enabling `AFIUCV` without runtime z/VM IUCV still allows HiperSockets-oriented behavior if devices exist.

## Risks and test signals
Risks are mostly configuration expectations: AF_IUCV may be available as a module when only QETH_L3 is enabled, while classic IUCV operations require z/VM and `CONFIG_IUCV`. Test build matrices for S390 built-in/module combinations, non-S390 exclusion, and runtime module loading with and without z/VM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/iucv/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/iucv/Makefile -->
# sources/distributed-fs/ceph-client/net/iucv/Makefile

## Purpose
Builds the IUCV networking objects based on Kconfig selections.

## Important APIs, types, and functions
The object rules are `obj-$(CONFIG_IUCV) += iucv.o` and `obj-$(CONFIG_AFIUCV) += af_iucv.o`.

## Control flow
No runtime control flow. Kbuild includes the low-level driver and AF socket layer independently according to configuration.

## State and persistence behavior
No runtime state. It influences the build graph only.

## Dependencies and integration points
Ties `CONFIG_IUCV` to `iucv.c` and `CONFIG_AFIUCV` to `af_iucv.c`. This supports AF_IUCV being built when HiperSockets are desired even if classic IUCV is unavailable.

## Risks and test signals
Risk is build skew between the two symbols, especially AF_IUCV references to `iucv_if` when classic IUCV is conditionally available. Test allmodconfig/allyesconfig on S390 and modular load/unload paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/iucv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/iucv/af_iucv.c -->
# sources/distributed-fs/ceph-client/net/iucv/af_iucv.c

## Purpose
Implements PF/AF_IUCV sockets for S390. It presents stream and seqpacket sockets over either classic z/VM IUCV paths or HiperSockets frames, including bind/connect/listen/accept, send/receive, shutdown, socket options, callback handling, HiperSockets packet receive, netdevice event handling, and module registration.

## Important APIs, types, and functions
Registers `iucv_proto`, `iucv_sock_family_ops`, `iucv_sock_ops`, `af_iucv_handler`, and `iucv_packet_type`. Core socket functions are `iucv_sock_bind`, `iucv_sock_connect`, `iucv_sock_listen`, `iucv_sock_accept`, `iucv_sock_sendmsg`, `iucv_sock_recvmsg`, `iucv_sock_shutdown`, `iucv_sock_release`, and option handlers for `SO_IPRMDATA_MSG`, `SO_MSGLIMIT`, and `SO_MSGSIZE`. Classic IUCV callbacks include connection request/ack/reject/shutdown, RX, and TX complete. HiperSockets handlers include SYN, SYN|ACK, SYN|FIN, FIN, WIN, data RX, TX notify, and `afiucv_hs_rcv`.

## Control flow
Socket creation allocates `struct iucv_sock`, initializes queues and counters, selects classic IUCV transport if `pr_iucv` is available, links the socket globally, and exposes only stream/seqpacket semantics. Bind either matches the local z/VM user for classic IUCV or locates a HiperSockets netdevice by EBCDIC user id, sets source names, device refs, and message limits. Connect autobinds classic IUCV sockets if needed, stores destination IDs, sends HiperSockets SYN or calls `path_connect`, then waits for connected/disconnected state. Listen/accept use an accept queue guarded by `accept_q_lock`.

Send builds an skb, handles control messages for target class, waits under message limits, then either emits a HiperSockets frame with an AF_IUCV transport header or uses classic IUCV `message_send` with inline IPRM data, direct buffer, or buffer-list DMA descriptors. Receive dequeues skbs, supports stream partial reads and seqpacket truncation/EOR, returns target class as cmsg, manages HiperSockets window updates, drains backlog, and processes saved classic IUCV messages when buffer space returns.

Classic callbacks allocate child sockets on path pending, accept paths, queue incoming messages or descriptors, match TX completions by tag, and move state to disconnect/closed. HiperSockets packet receive decodes the transport header, locates matching sockets, drives the SYN/SYNACK/FIN/WIN/data state machine, and queues payloads.

## State and persistence behavior
Runtime state includes the global AF_IUCV socket list, per-socket names/user IDs, transport selection, IUCV path pointer, HiperSockets device ref, accept queue, send/backlog/message queues, TX tags, message/window counters, shutdown flags, and socket states (`IUCV_OPEN`, `BOUND`, `LISTEN`, `CONNECTED`, `DISCONN`, `CLOSING`, `CLOSED`). No durable persistence exists. Cleanup severs paths, releases device refs, purges queues, zaps sockets, unregisters packet/notifier/family/proto, and unregisters from low-level IUCV if used.

## Dependencies and integration points
Depends on S390 z/VM detection, `iucv_if` from `iucv.c`, EBCDIC conversion, QETH/HiperSockets netdevices, packet type `ETH_P_AF_IUCV`, socket core, skb memory accounting, security socket cloning, filters, netdevice notifier chain, and module registration. It integrates tightly with low-level IUCV path/message callbacks and with netdevice transmit notifications.

## Risks and test signals
Risks include socket-list locking races, path lifetime and `xchg` sever semantics, mismatched ASCII/EBCDIC IDs, HiperSockets flow-control counter imbalance, receive backlog starvation, window-update errors, partial stream-read offset bugs, device-down state transitions, and freeing sockets still on accept or global lists. Test classic z/VM connect/listen/accept, HiperSockets connect refusal and success, stream partial receive, seqpacket EOR/truncation, IPRM short messages, nonlinear large messages, shutdown both directions, message-limit blocking/wakeup, netdevice down/reboot notifier, module unload with active sockets, and cmsg target class behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/iucv/af_iucv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/iucv/iucv.c -->
# sources/distributed-fs/ceph-client/net/iucv/iucv.c

## Purpose
Provides the low-level S390 z/VM IUCV infrastructure. It wraps CP B2F0 IUCV commands, manages per-CPU interrupt buffers and command parameter blocks, exposes an IUCV bus and exported interface, registers handlers, manages path tables, dispatches external interrupts to registered users, and exports message/path operations used by AF_IUCV and other IUCV clients.

## Important APIs, types, and functions
Exports `iucv_bus`, `iucv_alloc_device`, `iucv_register`, `iucv_unregister`, `iucv_path_accept`, `iucv_path_connect`, `iucv_path_quiesce`, `iucv_path_resume`, `iucv_path_sever`, `iucv_message_purge`, `__iucv_message_receive`, `iucv_message_receive`, `iucv_message_reject`, `iucv_message_reply`, `__iucv_message_send`, `iucv_message_send`, `iucv_message_send2way`, and `iucv_if`. Internal command layouts are `union iucv_param` and packed CP parameter structs. Interrupt data is represented by `struct iucv_irq_data` and per-event decoded structs.

## Control flow
Initialization requires `machine_is_vm`, enables the IUCV control bit, queries max path IDs, registers external IRQ handling, creates a root device, installs CPU hotplug states for per-CPU DMA-capable buffers, registers a reboot notifier, converts fixed error strings to EBCDIC, registers the IUCV bus, and marks the exported interface available. Handler registration enables IUCV on first user by allocating the path table, declaring buffers on online CPUs, and enabling interrupt masks; non-SMP handlers force interrupts to a single CPU.

CP commands are issued through inline assembly `__iucv_call_b2f0` and typed wrappers. Path connect/accept/quiesce/resume/sever fill command blocks, call CP, update path fields and handler lists, and manage `iucv_path_table`. Message send/receive/reply/reject/purge handle inline IPRM data, buffer-list flags, DMA32 addresses, message IDs, tags, classes, and residual/audit results.

External interrupts copy the per-CPU interrupt buffer into allocated queue entries. Path-pending work goes to a workqueue because it may call functions unsuitable for tasklet context; other events go to a tasklet. Dispatch decodes connection complete/sever/quiesce/resume and message pending/complete events, finds the path by ID, and invokes registered handler callbacks.

## State and persistence behavior
Runtime state includes `iucv_available`, root device/bus state, max pathid, path table, handler list, per-CPU IRQ data and command blocks, CPU masks for declared buffers and enabled IRQs, task/work queues, active CPU marker, non-SMP handler count, and reboot notifier. No durable persistence exists. Reboot blocks interrupts and severs active paths; exit frees queued work, unregisters hotplug states, root device, bus, and external IRQ.

## Dependencies and integration points
Depends on S390/z/VM machine support, CP B2F0 instruction, external IRQ `EXT_IRQ_IUCV`, CPU hotplug, DMA-addressable memory below 2G, EBCDIC helpers, device/bus core, reboot notifier, tasklets/workqueues, and exported `net/iucv/iucv.h` contracts. AF_IUCV consumes `iucv_if`.

## Risks and test signals
Risks include path-ID reuse races, stale queued interrupts after sever, CPU hotplug leaving no enabled IUCV CPU, non-SMP handler ordering constraints, DMA32 address misuse, CP return-code mapping, and tasklet/work locking deadlocks around `iucv_table_lock`. Test VM-only init failure on non-z/VM, CPU online/offline while paths exist, handler register/unregister transitions, path pending/accept/connect/sever, message send/receive/reply/purge with IPRM and buffer lists, reboot notifier path severing, and concurrent path teardown with queued interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/iucv/iucv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/kcm/Kconfig -->
# sources/distributed-fs/ceph-client/net/kcm/Kconfig

## Purpose
Defines the KCM socket feature. KCM multiplexes message-oriented application protocols over kernel connections such as TCP sockets.

## Important APIs, types, and functions
The symbol is `CONFIG_AF_KCM`, a tristate named "KCM sockets". It depends on `INET` and selects `BPF_SYSCALL` and `STREAM_PARSER`.

## Control flow
No runtime control flow. Enabling the symbol causes Kbuild to build the KCM module/object and ensures required BPF and stream parser infrastructure is present.

## State and persistence behavior
Only build configuration state exists. It determines whether PF_KCM can be registered at runtime.

## Dependencies and integration points
Integrates with TCP/INET sockets, BPF socket-filter programs used as message parsers, and the stream parser library.

## Risks and test signals
Risks are missing selected dependencies or unsupported builds without INET. Test modular and built-in builds, dependency resolution, and PF_KCM socket creation when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/kcm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/kcm/Makefile -->
# sources/distributed-fs/ceph-client/net/kcm/Makefile

## Purpose
Builds the KCM socket implementation.

## Important APIs, types, and functions
`obj-$(CONFIG_AF_KCM) += kcm.o` declares the composite KCM object; `kcm-y := kcmsock.o kcmproc.o` links the socket implementation and procfs reporting.

## Control flow
No runtime control flow. Kbuild composes the module or built-in object from both source files when AF_KCM is enabled.

## State and persistence behavior
No runtime state. It affects object composition only.

## Dependencies and integration points
Connects Kconfig to `kcmsock.c` and `kcmproc.c`, so proc support is compiled into the KCM object and conditionally active inside `kcmproc.c` under `CONFIG_PROC_FS`.

## Risks and test signals
Risk is missing proc symbols or unresolved references if object composition changes. Test `CONFIG_AF_KCM=m/y` with `CONFIG_PROC_FS` on and off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/kcm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/kcm/kcmproc.c -->
# sources/distributed-fs/ceph-client/net/kcm/kcmproc.c

## Purpose
Provides `/proc/net/kcm` and `/proc/net/kcm_stats` views for KCM sockets. It exposes per-mux, per-KCM socket, per-psock, and aggregate parser/transmit statistics for diagnostics.

## Important APIs, types, and functions
Public init/exit functions are `kcm_proc_init` and `kcm_proc_exit`. Per-net proc setup uses `kcm_proc_init_net` and `kcm_proc_exit_net`. Seq-file iteration is implemented by `kcm_seq_start`, `kcm_seq_next`, `kcm_seq_stop`, and `kcm_seq_show`; formatting helpers include `kcm_format_mux_header`, `kcm_format_sock`, `kcm_format_psock`, and `kcm_format_mux`. Aggregate stats are produced by `kcm_stats_seq_show`.

## Control flow
`kcm_proc_init` registers pernet proc setup. Each namespace creates `kcm_stats` via `proc_create_net_single` and `kcm` via `proc_create_net`. `/proc/net/kcm` iterates the namespace mux list under RCU, prints a header, then formats each mux while taking `mux->lock` to walk its KCM sockets and psocks. `/proc/net/kcm_stats` locks the namespace mutex, folds already-aggregated closed mux/psock stats with active mux and psock stats, then prints mux-level, psock-level, and stream-parser counters.

## State and persistence behavior
No owning state beyond proc registrations. It reads live KCM state plus aggregate stats accumulated during mux release. Proc output is transient.

## Dependencies and integration points
Depends on `kcm_net_id`, KCM data structures from `net/kcm.h`, procfs, seq_file, net namespace generic storage, RCU list traversal, KCM aggregation helpers, and stream parser stats.

## Risks and test signals
Risks include lock ordering with active KCM teardown, reading fields not protected by the selected lock, RCU lifetime during mux iteration, and misleading aggregate labels. Test proc creation/removal per netns, reading while attaching/unattaching psocks, reading while sockets close, aggregate stats after mux release, and builds without `CONFIG_PROC_FS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/kcm/kcmproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/kcm/kcmsock.c -->
# sources/distributed-fs/ceph-client/net/kcm/kcmsock.c

## Purpose
Implements PF_KCM sockets, which multiplex framed application messages over attached TCP sockets. It owns mux creation/destruction, KCM socket send/receive semantics, psock attachment to TCP sockets, BPF/stream-parser receive framing, transmit psock reservation, clone/ioctl control, receive-disable options, proc initialization, per-net state, and module lifecycle.

## Important APIs, types, and functions
Registers `kcm_proto`, `kcm_family_ops`, datagram and seqpacket `proto_ops`, pernet `kcm_net_ops`, slab caches, and a single-thread workqueue. Key user operations are `kcm_create`, `kcm_sendmsg`, `kcm_recvmsg`, `kcm_splice_read`, `kcm_setsockopt`, `kcm_getsockopt`, `kcm_ioctl`, `kcm_release`, and `kcm_clone`. Attach control is through `SIOCKCMATTACH`, `SIOCKCMUNATTACH`, and `SIOCKCMCLONE`, using `struct kcm_attach`, `kcm_unattach`, and `kcm_attach`. Receive parsing uses strparser callbacks `kcm_rcv_strparser`, `kcm_parse_func_strparser`, and `kcm_read_sock_done`.

## Control flow
Creating a KCM socket allocates a mux, initializes mux lists/locks/hold queue, links it into per-net state, initializes the first KCM socket, and places that socket on the receive-waiter list. Clone creates another socket sharing the same mux. Attach looks up a TCP socket and BPF socket-filter program, rejects unsupported or already-attached sockets, initializes `strparser`, swaps TCP callbacks to KCM wrappers, holds the socket/file, links a psock into the mux, makes it available for transmit, and kicks receive parsing.

Receive flow starts from TCP `sk_data_ready`, enters strparser, runs the BPF parser to determine message length, reserves a KCM receiver if one is waiting, queues the message to that KCM receive queue, or pauses the psock with a ready message if no KCM can receive. `kcm_rfree`, `kcm_rcv_ready`, `requeue_rx_msgs`, receive-disable, and unreserve logic move queued messages among KCM sockets while honoring receive buffer limits.

Send flow builds an skb-backed message from copied or spliced pages. Datagram sockets complete on lack of `MSG_MORE`; seqpacket sockets require `MSG_EOR`. Completed messages are queued on `sk_write_queue`, then `kcm_write_msgs` reserves an available psock, sends page fragments through the lower TCP socket, handles `-EAGAIN` by saving fragment progress, aborts and retries on hard psock errors, and unreserves psocks when queues drain. `psock_write_space` and workqueue processing resume blocked writers.

Release cancels pending TX work, purges queues, aborts reserved psocks, requeues receive messages, removes the KCM socket from the mux, and releases the mux when the last KCM socket closes. Unattach restores TCP callbacks, stops/destroys strparser, drops ready messages, aggregates stats, and either frees the psock immediately or defers until a reserved transmit path unreserves it.

## State and persistence behavior
Runtime state includes per-net mux lists and aggregate stats, each mux's KCM socket list, psock list, waiters, available psocks, ready psocks, receive hold queue, locks, and counters. KCM sockets track TX partial message state, reserved TX psock, RX wait/reservation/disable flags, work item, and stats. Psocks track attached TCP socket callbacks, BPF program, strparser, reserved KCM, ready RX message, availability, done/unattaching/tx_stopped flags, stats, and held file/socket refs. No durable persistence exists.

## Dependencies and integration points
Depends on INET/TCP sockets, BPF socket-filter programs, stream parser, socket memory accounting, splice/page-frag helpers, net namespace generic IDs, proc support from `kcmproc.c`, RCU, workqueues, and ioctl UAPI from `linux/kcm.h`.

## Risks and test signals
Risks include callback restoration races on attached TCP sockets, psock reserved/free lifetime bugs, TX retry causing duplicate or corrupted message framing, receive requeue ordering, buffer accounting mismatches, BPF parser invalid lengths, deadlocks between mux locks and socket locks, clone/mux teardown races, and splice/EOR edge cases. Test attach/unattach under traffic, clone fanout, receive-disable/re-enable, datagram `MSG_MORE`, seqpacket `MSG_EOR`, splice send/read, BPF parser failures and oversized messages, TCP close/error propagation, socket release with reserved TX/RX psocks, proc stats under churn, and netns teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/kcm/kcmsock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/key/Makefile -->
# sources/distributed-fs/ceph-client/net/key/Makefile

## Purpose
Builds the PF_KEY key management socket implementation when enabled.

## Important APIs, types, and functions
The Makefile rule is `obj-$(CONFIG_NET_KEY) += af_key.o`, tying `CONFIG_NET_KEY` to the `af_key` object.

## Control flow
No runtime control flow. Kbuild includes or omits `af_key.o` according to the configuration.

## State and persistence behavior
No runtime state. It affects only build composition.

## Dependencies and integration points
Integrates the networking key-management subsystem with the kernel build. PF_KEY is commonly used by IPsec/XFRM key management, making this build switch relevant to the neighboring XFRM files in this work item.

## Risks and test signals
Risks are limited to build configuration and unresolved object dependencies. Test `CONFIG_NET_KEY=m/y/n` builds and IPsec key-management users that expect PF_KEY sockets when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/key/Makefile -->
