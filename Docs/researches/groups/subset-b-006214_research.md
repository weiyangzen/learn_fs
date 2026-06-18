# Research: subset-b-006214

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/mcast.c -->
# sources/distributed-fs/ceph-client/net/ipv6/mcast.c

Purpose: Implements IPv6 multicast listener management for sockets and devices, including MLDv1/MLDv2 joins, leaves, source filters, query/report receive handling, report generation, procfs exposure, per-net control sockets, and netdevice event integration.

Important APIs/types/functions: exported socket/device APIs include `ipv6_sock_mc_join`, `ipv6_sock_mc_join_ssm`, `ipv6_sock_mc_drop`, `ipv6_sock_mc_close`, `ip6_mc_source`, `ip6_mc_msfilter`, `ip6_mc_msfget`, `inet6_mc_check`, `ipv6_dev_mc_inc`, `ipv6_dev_mc_dec`, `ipv6_chk_mcast_addr`, `ipv6_mc_{init_dev,destroy_dev,up,down,unmap,remap}`, and `ipv6_mc_dad_complete`. Key state lives in `struct ipv6_mc_socklist`, `struct ifmcaddr6`, `struct ip6_sf_socklist`, `struct ip6_sf_list`, and `struct inet6_dev` fields such as `mc_list`, `mc_tomb`, `mc_query_queue`, `mc_report_queue`, `mc_qrv`, `mc_qi`, `mc_qri`, and delayed work items.

Control flow: socket joins validate multicast addresses, resolve an output device, add/increment device membership, then link a socket membership under the socket lock. Device membership allocates `ifmcaddr6`, maps multicast addresses to link-layer filters with `ndisc_mc_map`, notifies rtnetlink, and starts MLD reporting. Query/report receive entry points enqueue skbs and process them on `mld_wq`; workers validate MLDv1/v2 query semantics, update querier timing/version state, mark source-specific query response state, and schedule per-group/general report work. Report builders assemble MLDv2 group records into MTU-sized packets and send through `NF_HOOK(NF_INET_LOCAL_OUT)`. Leave and source-filter paths compute change records, tombstone deleted groups/sources, and repeat change reports according to QRV.

State and persistence: State is in memory per socket, per `inet6_dev`, per net namespace control socket, RCU-protected membership/source lists, tombstone lists for pending MLDv2 change reports, delayed work references, procfs views `igmp6` and `mcfilter6`, and sysctls `sysctl_mld_max_msf`/`sysctl_mld_qrv`. It does not persist across device teardown or namespace destruction.

Dependencies/integration: Depends on IPv6 address configuration, neighbour discovery for multicast MAC mapping, ICMPv6 checksums, routing/dst allocation, rtnetlink notifications, procfs, netfilter local-out hooks, device notifiers, and pernet lifecycle. It shares control socket ownership via `net->ipv6.igmp_sk` and autojoin socket `mc_autojoin_sk`.

Risks and test signals: Highest risk is concurrency: `mc_lock`, queue spinlocks, RCU replacement, delayed-work reference counting, and device-dead transitions must stay paired. Protocol risk is MLDv1 fallback, QRV/QI/QRI clamping, source-list truncation, and malformed query/report handling. Useful tests include join/drop/source-filter socket options, DAD completion reports, device up/down/destruction races, procfs iteration under churn, MLDv1/v2 query fuzzing, net namespace cleanup, and packet captures verifying correct MLD records and checksums.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/mcast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/mcast_snoop.c -->
# sources/distributed-fs/ceph-client/net/ipv6/mcast_snoop.c

Purpose: Provides a reusable validator for bridge or snooping code that needs to identify sane IPv6 MLD packets without running the full IPv6 input stack.

Important APIs/types/functions: The exported API is `ipv6_mc_check_mld(struct sk_buff *skb)`. Helpers validate the IPv6 header, hop-by-hop extension chain, ICMPv6 checksum, MLD message type, MLDv2 report length, and MLD query rules. It uses `struct mld_msg`, `struct mld2_query`, `struct mld2_report`, `ipv6_skip_exthdr`, `ipv6_mc_may_pull`, `skb_checksum_trimmed`, and `ip6_compute_pseudo`.

Control flow: `ipv6_mc_check_mld` first verifies the IPv6 header version, payload length, and transport offset. It then requires a hop-by-hop option chain whose terminal next header is ICMPv6, trims/validates the ICMPv6 checksum, and classifies the ICMPv6 body. Queries must have link-local source addresses; general queries must target link-local all-nodes; v2 queries must have enough bytes for their fixed header. Reports and reductions are accepted after minimum-length checks.

State and persistence: The file is stateless. It mutates only skb header offsets and may allocate/free a temporary checksum-trimmed skb.

Dependencies/integration: Integrates through `EXPORT_SYMBOL(ipv6_mc_check_mld)` for multicast snooping users. It depends on IPv6 header parsing, ICMPv6 checksum helpers, and MLD structure definitions.

Risks and test signals: Risks are off-by-one payload length checks, incorrectly accepting non-hop-by-hop ICMPv6, checksum handling on non-linear skbs, and mismatched return-code semantics. Test signals include malformed extension chains, truncated MLDv1/v2 packets, bad checksums, non-link-local query sources, general queries not sent to ff02::1, and non-MLD ICMPv6 packets returning `-ENODATA`/`-ENOMSG` rather than hard validation errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/mcast_snoop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/mip6.c -->
# sources/distributed-fs/ceph-client/net/ipv6/mip6.c

Purpose: Implements Mobile IPv6 route-optimization support as XFRM extension-header types plus a raw IPv6 Mobility Header filter.

Important APIs/types/functions: Key functions are `mip6_mh_filter`, `mip6_destopt_{input,output,reject,init_state,destroy}`, `mip6_rthdr_{input,output,init_state,destroy}`, and module init/exit. It registers two `struct xfrm_type` instances for `IPPROTO_DSTOPTS` and `IPPROTO_ROUTING`, and registers the rawv6 mobility-header filter with `rawv6_mh_filter_register`.

Control flow: The MH filter validates the fixed mobility header, rejects too-short type-specific messages, and requires `ip6mh_proto == IPPROTO_NONE`, sending ICMPv6 parameter problems for protocol violations. Destination-option output inserts a Home Address Option and rewrites the IPv6 source to the care-of address from `xfrm_state`. Routing-header output inserts Routing Header type 2 and rewrites destination to the care-of address. Input paths verify that packet source/destination matches the XFRM co-address unless the co-address is unspecified. The reject path rate-limits `km_report` notifications and skips MH flows.

State and persistence: Persistent state is limited to XFRM states owned externally and a static spinlock-protected `mip6_report_rate_limiter` keyed by timestamp, interface, source, and destination. Header length is stored in `x->props.header_len`.

Dependencies/integration: Depends on XFRM, raw IPv6 sockets, ICMPv6, Mobile IPv6 structures, and kernel migration reporting. Module aliases expose the XFRM types.

Risks and test signals: Risks include skb header-offset assumptions during push/rewrite, co-address locking, incorrect padding/alignment for HAO, and rate-limiter over/under-suppression. Tests should exercise XFRM state init rejection for nonzero SPI or wrong mode, outbound HAO and RH2 packet formatting, inbound co-address mismatch, malformed MH lengths/proto fields, and unload cleanup ordering after partial registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/mip6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ndisc.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ndisc.c

Purpose: Implements IPv6 Neighbor Discovery: neighbour-cache table operations, NS/NA/RS/RA/Redirect packet construction and receive handling, proxy neighbour behavior, RA-driven route/interface configuration, netlink user-option export, sysctl handling, and netdevice lifecycle hooks.

Important APIs/types/functions: Exports `nd_tbl`, `__ndisc_fill_addr_option`, `ndisc_mc_map`, `ndisc_send_skb`, `ndisc_send_na`, and `ndisc_ns_create`. Core receive functions are `ndisc_recv_ns`, `ndisc_recv_na`, `ndisc_recv_rs`, `ndisc_router_discovery`, `ndisc_redirect_rcv`, and dispatcher `ndisc_rcv`. It defines neighbour ops `ndisc_generic_ops`, `ndisc_hh_ops`, `ndisc_direct_ops`, and `struct neigh_table nd_tbl`.

Control flow: Constructors map multicast/noarp/point-to-point neighbours and clone per-device ND parameters. Outbound builders allocate control skbs, fill ND options, compute ICMPv6 checksums, prepend IPv6 headers with hop-limit 255, and send through `NF_HOOK(NF_INET_LOCAL_OUT)`. Receive dispatch rejects fragmented ND when configured, linearizes, verifies hop-limit 255 and ICMPv6 code 0, then calls per-message handlers. NS handling validates DAD rules, options, proxy/anycast conditions, updates neighbour cache, and may respond with NA. NA handling rejects invalid targets, handles DAD conflicts, optionally accepts untracked router NAs, and updates cache/router flags. RA handling enforces link-local source and accept-ra policy, updates default routers, route prefs, hop limit, neighbour parameters, prefixes, MTU, route-info options, and emits user-option netlink messages. Redirect handling validates router source/options and notifies ICMP routing code.

State and persistence: State is per net namespace `ndisc_sk`, global neighbour table entries, per-device `inet6_dev` configuration/timestamps/RA MTU, default routes in fib6, proxy neighbour entries, sysctl-exposed neighbour parameters, and notifiers. It is memory-resident and torn down through pernet exit and `ndisc_cleanup`.

Dependencies/integration: Integrates with addrconf, fib6 routing, ICMPv6, netfilter local-out, rtnetlink, neighbour core, proc/sysctl neighbour parameters, L3 master/slave devices, and optional node type/route-info features.

Risks and test signals: Highest risks are accepting invalid ND messages, DAD false positives, stale router flag cleanup, RA policy interactions, route lifetime/metric updates, and netdevice event races. Tests should cover malformed options, fragmented ND suppression, DAD nonce loopback, proxy delay enqueue, unsolicited NA policy, RA from local/link-local/non-router sources, route-info/prefix/MTU processing, redirect rate limiting, namespace cleanup, and carrier/address change notifier effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ndisc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter.c

Purpose: Supplies IPv6-specific netfilter core helpers for rerouting modified packets, performing route lookups for netfilter users, and fragmenting bridged IPv6 packets after netfilter processing.

Important APIs/types/functions: Exports `ip6_route_me_harder`, `__nf_ip6_route`, and `br_ip6_fragment`. It uses `flowi6`, `fib6_rules_early_flow_dissect`, `ip6_route_output`, XFRM session decoding/lookup, bridge fragment metadata, and IPv6 fragmentation helpers.

Control flow: `ip6_route_me_harder` builds a route key from the skb IPv6 header, mark, UID, l3mdev, socket binding, flow label, and strict output-interface rules for multicast/link-local destinations; replaces `skb_dst`; optionally applies XFRM; then ensures enough headroom for the new device header. `__nf_ip6_route` wraps `ip6_route_output`, using a fake bound socket for strict interface lookups. `br_ip6_fragment` validates bridge fragment size, finds the first fragmentable option, computes MTU and fragment ID, handles checksum completion, then either uses frag-list fast path or slow linear fragmentation and calls an output callback for each fragment.

State and persistence: No persistent ownership beyond skb route/dst mutation and fragment skb production. It consumes/drops skb ownership on fragmentation paths.

Dependencies/integration: Integrates with netfilter queue/bridge code, IPv6 routing, XFRM, l3mdev, bridge private skb control blocks, and exported netfilter IPv6 helpers.

Risks and test signals: Risks include incorrect strict interface routing, route/XFRM reference handling, headroom expansion failures, blackhole semantics hiding fragmentation errors, and preserving timestamps through fragments. Tests should mutate packet addresses/marks before reroute, cover link-local/multicast output selection, XFRM transformed versus untransformed skbs, bridge frag-list and slow-path fragmentation, invalid MTU/frag sizes, checksum-partial skbs, and output callback errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/Kconfig -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/Kconfig

Purpose: Defines build-time configuration for IPv6 netfilter, including legacy ip6tables, nftables IPv6 support, socket/tproxy helpers, reject/log/dup cores, match modules, and target/table modules.

Important APIs/types/functions: Kconfig symbols include `IP6_NF_IPTABLES_LEGACY`, `NF_SOCKET_IPV6`, `NF_TPROXY_IPV6`, `NF_TABLES_IPV6`, `NFT_REJECT_IPV6`, `NFT_DUP_IPV6`, `NFT_FIB_IPV6`, `NF_DUP_IPV6`, `NF_REJECT_IPV6`, `NF_LOG_IPV6`, `IP6_NF_IPTABLES`, match symbols such as `IP6_NF_MATCH_AH`, `EUI64`, `FRAG`, `OPTS`, `IPV6HEADER`, `MH`, `RPFILTER`, `RT`, `SRH`, and targets/tables such as `IP6_NF_FILTER`, `IP6_NF_TARGET_REJECT`, `SYNPROXY`, `MANGLE`, `RAW`, `SECURITY`, `NAT`, `MASQUERADE`, and `NPT`.

Control flow: The file gates menu visibility on `INET && IPV6 && NETFILTER`, uses nested `if` blocks for nf_tables and ip6tables feature families, selects required common modules, and gives defaults for common non-advanced configurations.

State and persistence: Kconfig state persists as kernel build configuration and determines object inclusion, module availability, aliases, and dependency closure.

Dependencies/integration: Integrates with top-level kbuild, netfilter xtables/nftables, conntrack/NAT, security framework, and module autoload names referenced by ip6tables userspace.

Risks and test signals: Risks are dependency mismatches, symbols enabling objects without required core support, and legacy/nft compatibility confusion. Test signals include `allmodconfig`, `randconfig`, oldconfig migration, building with nft-only versus legacy iptables, and checking that every Makefile object in this subset is reachable from the expected symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/Makefile -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/Makefile

Purpose: Maps IPv6 netfilter Kconfig symbols to object files and composite objects.

Important APIs/types/functions: It builds legacy tables (`ip6_tables.o`, `ip6table_filter.o`, mangle/raw/security/nat), defrag composite `nf_defrag_ipv6.o`, socket/tproxy helpers, reject/dup cores, nftables objects, xtables matches (`ip6t_ah.o`, `ip6t_eui64.o`, `ip6t_frag.o`, `ip6t_ipv6header.o`, `ip6t_mh.o`, `ip6t_hbh.o`, `ip6t_rpfilter.o`, `ip6t_rt.o`, `ip6t_srh.o`) and targets (`ip6t_NPT.o`, `ip6t_REJECT.o`, `ip6t_SYNPROXY.o`).

Control flow: Kbuild includes each object through `obj-$(CONFIG_...)`; the comment notes link order matters, placing `ip6_tables.o` before dependent legacy tables.

State and persistence: No runtime state; it persists build graph ordering and module composition.

Dependencies/integration: Tightly coupled to Kconfig symbol names and module autoload aliases from target/match files.

Risks and test signals: Risks are stale symbols, incorrect link order for table users of `ip6t_do_table`, and missing composite members for defrag. Test with modular and built-in configurations, `modprobe ip6table_filter`, and symbol dependency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6_tables.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6_tables.c

Purpose: Implements legacy IPv6 ip6tables rule evaluation, table registration/replacement, userspace sockopt ABI, counters, compatibility conversion, and built-in standard/error targets.

Important APIs/types/functions: Exports `ip6t_alloc_initial_table`, `ip6t_register_table`, `ip6t_unregister_table_exit`, and `ip6t_do_table`. Core functions include `ip6_packet_match`, `mark_source_chains`, `translate_table`, `find_check_entry`, `cleanup_entry`, `get_info`, `get_entries`, `do_replace`, `do_add_counters`, compat translation helpers, and sockopt handlers `do_ip6t_set_ctl`/`do_ip6t_get_ctl`.

Control flow: Packet evaluation starts at the hook entry, matches IPv6 source/destination/interface/protocol and extension-header location, runs xt matches, updates per-CPU counters, and executes standard or extension targets. Standard positive verdicts jump/goto inside the table with a per-CPU jump stack; negative verdicts accept/drop/return. Userspace replacement copies a table blob, validates entry sizes/hook underflows, computes source-chain reachability and loop safety, resolves match/target modules, then atomically swaps table info and returns old counters. Get paths snapshot counters and translate kernel entries back to userspace. Compat paths adjust entry, match, target, hook, and verdict offsets for 32-bit userspace.

State and persistence: Runtime state includes per-net xtables protocol state, registered tables, `xt_table_info` blobs, per-CPU counters, jump stacks, module references, and sockopt registration. Rules persist only in kernel memory until replaced, table unregistered, module unloaded, or namespace destroyed.

Dependencies/integration: Depends on x_tables core, nf_sockopt, module autoloading, netfilter hook ops, optional trace logging, compat infrastructure, and table modules such as `ip6table_filter`.

Risks and test signals: Highest risks are userspace blob validation, loop detection, offset arithmetic, compat conversion, counter consistency under concurrent packet traversal, module reference leaks, and jumpstack recursion with TEE. Tests should cover malformed replace blobs, invalid hooks/underflows, loops, missing modules, concurrent replace/get/add counters under traffic, 32-bit compat ip6tables, TRACE logging, goto versus jump semantics, and namespace teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6_tables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_NPT.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_NPT.c

Purpose: Implements stateless IPv6 Network Prefix Translation targets `SNPT` and `DNPT` for the mangle table.

Important APIs/types/functions: Uses `struct ip6t_npt_tginfo`, `ip6t_npt_checkentry`, `ip6t_npt_map_pfx`, `icmpv6_bounced_ipv6hdr`, target callbacks `ip6t_snpt_tg` and `ip6t_dnpt_tg`, and an `xt_target` array.

Control flow: Checkentry rejects prefixes longer than /64 and prefixes with nonzero host bits, then precomputes a checksum adjustment. The target rewrites source or destination prefix bits, applies checksum-neutral adjustment into a suitable 16-bit word, sends ICMPv6 parameter problem and drops if all candidate words are unusable, and also rewrites embedded IPv6 headers in bounced ICMPv6 errors when they reference the translated source prefix.

State and persistence: Per-rule target info stores prefixes, lengths, and computed adjustment. No global runtime state.

Dependencies/integration: Registers with xtables for `NFPROTO_IPV6`, table `mangle`, and hooks appropriate to source or destination prefix translation. Uses IPv6 address helpers and ICMPv6 error emission.

Risks and test signals: Risks include checksum-neutrality mistakes, ICMPv6 embedded-header rewrite only affecting local copies when not writable, and prefix validation edge cases. Tests should cover /0-/64 mappings, mangle hook restrictions, all-zero/mangled checksum words, ICMPv6 error translation, and round-trip SNPT/DNPT checksum stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_NPT.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_REJECT.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_REJECT.c

Purpose: Provides the IPv6 `REJECT` xtables target for filter/NFT compatibility, sending ICMPv6 errors or TCP resets before dropping packets.

Important APIs/types/functions: Target callback `reject_tg6`, validator `reject_tg6_check`, `struct ip6t_reject_info`, `nf_send_unreach6`, `nf_send_reset6`, and `xt_target reject_tg6_reg`.

Control flow: Runtime switches on `reject->with`, emits the requested ICMPv6 unreachable/policy/reject-route error or TCP reset using current hook and socket context, then always returns `NF_DROP`. Checkentry rejects unsupported `ECHOREPLY` and enforces that `TCP_RESET` rules explicitly match non-inverted TCP.

State and persistence: Stateless beyond per-rule reject mode.

Dependencies/integration: Depends on `NF_REJECT_IPV6`, xtables table `filter`, hooks local-in/forward/local-out, and protocol constraints from ip6tables.

Risks and test signals: Risks are generating illegal reset/error packets from wrong hooks or malformed TCP rules. Tests should verify checkentry failures, each reject mode on input/forward/output, rate-limited logs, and no response for unsupported echo reply.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_REJECT.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_SYNPROXY.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_SYNPROXY.c

Purpose: Implements IPv6 xtables `SYNPROXY`, intercepting TCP handshakes with syncookies before allowing backend connection tracking.

Important APIs/types/functions: Uses `synproxy_tg6`, `synproxy_tg6_check`, `synproxy_tg6_destroy`, `struct xt_synproxy_info`, `synproxy_parse_options`, `synproxy_send_client_synack_ipv6`, `synproxy_recv_client_ack_ipv6`, conntrack namespace refs, and `nf_synproxy_ipv6_init/fini`.

Control flow: Runtime validates IPv6 TCP checksum, reads the TCP header at `par->thoff`, parses options, and handles pure SYN and pure ACK. Initial SYNs update stats, mask negotiated options by rule config, initialize timestamp cookies if enabled, send SYN+ACK, consume the skb, and return `NF_STOLEN`. Valid ACKs complete cookie validation similarly; invalid ACKs drop. Other packets continue. Checkentry requires an explicit non-inverted TCP match, acquires conntrack namespace support, and initializes IPv6 synproxy state; destroy reverses both.

State and persistence: Per-net synproxy state and conntrack references persist while matching rules are installed; per-CPU stats are updated.

Dependencies/integration: Depends on `NF_CONNTRACK`, `NETFILTER_SYNPROXY`, syncookies, xtables, and IPv6 TCP checksum helpers.

Risks and test signals: Risks include leaked conntrack refs on check failure, wrong handling of non-linear TCP headers, option negotiation errors, and unexpected `NF_STOLEN` ownership. Tests should cover invalid checksum/header/options, TCP-only rule validation, module unload with active rules, SYN/ACK handshakes with timestamp and no timestamp modes, and forward/local-in hook behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_SYNPROXY.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_ah.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_ah.c

Purpose: Implements the IPv6 xtables `ah` match for IPsec Authentication Header fields.

Important APIs/types/functions: Uses `ah_mt6`, `ah_mt6_check`, `spi_match`, `struct ip6t_ah`, `ipv6_find_hdr`, `skb_header_pointer`, and `ipv6_authlen`.

Control flow: The match locates an AH extension header, hotdrops on parse errors other than no-header, safely reads the AH header, computes header length, and checks SPI range, optional header length, inversion flags, and reserved-field policy. Checkentry rejects unknown inversion bits.

State and persistence: Stateless beyond per-rule match data.

Dependencies/integration: Registers one xt match for `NFPROTO_IPV6`; depends on IPv6 extension-header parsing and ip6tables match ABI.

Risks and test signals: Risks include header-length mismatch and hotdrop behavior on malformed extension chains. Tests should cover absent AH, truncated AH, SPI ranges with inversion, reserved bits, auth length matching, and unknown invflags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_ah.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_eui64.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_eui64.c

Purpose: Implements the IPv6 xtables `eui64` match, checking whether the IPv6 source interface identifier corresponds to the Ethernet source MAC converted to EUI-64.

Important APIs/types/functions: Uses `eui64_mt6`, Ethernet header helpers, `ARPHRD_ETHER`, `ETH_P_IPV6`, and a single `xt_match`.

Control flow: Runtime requires an Ethernet device, a present MAC header at least `ETH_HLEN`, and IPv6 ethertype/version. It builds the EUI-64 identifier by inserting `ff:fe` and toggling the universal/local bit, then compares against the low 64 bits of the IPv6 source address.

State and persistence: Stateless.

Dependencies/integration: Valid only on pre-routing/local-in/forward hooks where the ingress L2 header is available.

Risks and test signals: Risks are hotdropping skbs with missing MAC headers, use on non-Ethernet devices, and behavior after L2 header stripping. Tests should cover Ethernet match/mismatch, non-Ethernet devices, short MAC headers, and hook placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_eui64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_frag.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_frag.c

Purpose: Implements the IPv6 xtables `frag` match for Fragment Header fields.

Important APIs/types/functions: Uses `frag_mt6`, `frag_mt6_check`, `id_match`, `struct ip6t_frag`, `ipv6_find_hdr`, and `skb_header_pointer`.

Control flow: The match locates the Fragment Header, hotdrops malformed parse errors, reads the header safely, and evaluates identification range plus flags for reserved bits, first fragment, more fragments, and last fragment. Unknown inversion flags are rejected at checkentry.

State and persistence: Stateless beyond rule parameters.

Dependencies/integration: Registers with xtables for IPv6 and depends on extension-header parsing.

Risks and test signals: Risks include ambiguity around non-first fragments and reserved bit handling. Tests should include no fragment header, truncated header, each flag combination, inverted ID ranges, malformed extension chains, and first/non-first/last fragment packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_frag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_hbh.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_hbh.c

Purpose: Implements IPv6 xtables `hbh` and `dst` matches for Hop-by-Hop and Destination Options headers.

Important APIs/types/functions: Shared callback `hbh_mt6`, validator `hbh_mt6_check`, `struct ip6t_opts`, `ipv6_find_hdr`, `ipv6_optlen`, and two `xt_match` registrations. `MODULE_ALIAS("ip6t_dst")` supports destination-options autoload.

Control flow: Runtime chooses Hop-by-Hop or Destination header based on which registration invoked the match, locates the header, verifies length, optionally matches exact header length, and if requested walks options strictly by type and length. Pad1 is handled as a one-byte option; other options use length+2. Non-strict matching is explicitly unsupported and rejected.

State and persistence: Stateless beyond per-rule option sequence and flags.

Dependencies/integration: Depends on IPv6 extension-header parser and xtables match ABI. The implementation relies on `hbh_mt6_reg` array order.

Risks and test signals: Risks are strict option walk bounds, reliance on registration array order, and unsupported non-strict flags. Tests should cover hbh/dst selection, zero-length or truncated options, Pad1/PadN, wildcard option lengths, length inversion, and checkentry rejection for non-strict/unknown flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_hbh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_ipv6header.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_ipv6header.c

Purpose: Implements the IPv6 xtables `ipv6header` match, classifying which extension/header categories are present in a packet.

Important APIs/types/functions: Uses `ipv6header_mt6`, `ipv6header_mt6_check`, `struct ip6t_ipv6header_info`, `nf_ip6_ext_hdr`, `skb_header_pointer`, `ipv6_authlen`, and `ipv6_optlen`.

Control flow: Starting after the base IPv6 header, it walks extension headers while they are known IPv6 extension types, records masks for hop-by-hop, routing, fragment, AH, destination options, ESP, none, and final protocol, then applies soft mode or hard exact mode with inversion semantics. Checkentry restricts hard-mode `invflags` to all-zero or all-ones.

State and persistence: Stateless.

Dependencies/integration: xtables IPv6 match ABI and IPv6 extension-header definitions.

Risks and test signals: Risks include malformed extension-length handling, ESP/NONE terminal behavior, and hard-mode inversion compatibility with userspace. Tests should cover every extension mask, mixed chains, truncated headers, final upper-layer protocol mask, modeflag behavior, and invalid hard-mode invflags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_ipv6header.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_mh.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_mh.c

Purpose: Implements the IPv6 xtables `mh` match for Mobile IPv6 Mobility Header type ranges.

Important APIs/types/functions: Uses `mh_mt6`, `mh_mt6_check`, `type_match`, `struct ip6_mh`, `struct ip6t_mh`, and registers with `.proto = IPPROTO_MH`.

Control flow: The match refuses nonzero fragment offsets, safely reads the Mobility Header at `par->thoff`, hotdrops tinygrams or headers whose payload proto is not `IPPROTO_NONE`, and matches the type against an inclusive range with optional inversion. Checkentry rejects unknown inversion flags.

State and persistence: Stateless.

Dependencies/integration: Depends on Mobile IPv6 header definitions and xtables protocol-filtered match dispatch.

Risks and test signals: Risks include hotdrop on truncated MH, fragment handling expectations, and invalid payload-proto enforcement. Tests should cover type ranges, inversion, nonzero fragment offsets, truncated headers, bad payload proto, and explicit `-p mh` dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_mh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_rpfilter.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_rpfilter.c

Purpose: Implements the IPv6 xtables `rpfilter` match, checking whether reverse routing for a packet's source would use the ingress interface.

Important APIs/types/functions: Uses `rpfilter_mt`, `rpfilter_check`, `rpfilter_lookup_reverse6`, `struct xt_rpfilter_info`, `ip6_route_lookup`, l3mdev helpers, and route flags.

Control flow: Loopback packets pass subject to inversion. Unspecified source addresses pass because forwarding will drop them later. Otherwise, it builds a reverse `flowi6` from packet source, optional destination source constraint, flow label, nexthdr, mark if enabled, link-local/strict interface constraints, and l3mdev context. It rejects route errors, reject/anycast routes, and local routes unless `ACCEPT_LOCAL`; it accepts if the route device or master matches ingress or loose mode is set. Checkentry allows only raw or mangle tables and known option bits.

State and persistence: Stateless beyond per-rule flags.

Dependencies/integration: Depends on IPv6 FIB lookup, netdevice/l3mdev, and xtables pre-routing hook.

Risks and test signals: Risks include policy routing mark behavior, l3mdev matching, local/anycast route handling, and table restriction regressions. Tests should cover strict/loose modes, valid-mark, accept-local, invert, link-local sources, VRF/l3mdev ingress, raw/mangle checkentry, and asymmetric route topologies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_rpfilter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_rt.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_rt.c

Purpose: Implements the IPv6 xtables `rt` match for Routing Header fields and type-0 address lists.

Important APIs/types/functions: Uses `rt_mt6`, `rt_mt6_check`, `segsleft_match`, `struct ip6t_rt`, `ipv6_find_hdr`, `ipv6_optlen`, `skb_header_pointer`, and `struct rt0_hdr`.

Control flow: Runtime locates a routing header, validates full length, matches segments-left range, optional header length and routing type, optional reserved field zero for type 0, and optionally address lists. Address list matching supports strict full-list equality or non-strict subsequence matching depending on flags. Checkentry rejects unknown inversion flags, too many addresses, and type-0-only options unless an uninverted `--rt-type 0` is present.

State and persistence: Stateless.

Dependencies/integration: xtables IPv6 extension-header parsing and legacy ip6tables routing-header ABI.

Risks and test signals: Risks are deprecated type-0 semantics, address-list bounds, and correct hotdrop on truncated skbs. Tests should cover no routing header, malformed length, segleft range/inversion, type mismatch, reserved field checks, strict/non-strict address lists, and checkentry type-0 constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_rt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_srh.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_srh.c

Purpose: Implements the IPv6 xtables `srh` match for Segment Routing Header revision 0 and revision 1 fields.

Important APIs/types/functions: Uses `srh_mt6`, `srh1_mt6`, `srh_mt6_check`, `srh1_mt6_check`, `struct ip6t_srh`, `struct ip6t_srh1`, `struct ipv6_sr_hdr`, `NF_SRH_INVF`, and `ipv6_masked_addr_cmp`.

Control flow: Both revisions locate a routing header, read and length-check it, require SRH type 4, and reject inconsistent `segments_left > first_segment`. Revision 0 matches next header, header length comparisons, segments-left comparisons, last-entry comparisons, and tag. Revision 1 repeats those and adds previous SID, next SID, and last SID masked-address matching with offset calculations based on `segments_left` and `first_segment`. Checkentry rejects unknown match and inversion flags.

State and persistence: Stateless beyond per-rule match data.

Dependencies/integration: Depends on IPv6 segment-routing definitions and xtables revisioned match registration.

Risks and test signals: Risks include SID offset arithmetic, insufficient validation that requested SID slots fit within `hdrlen`, inversion macro readability, and draft-field naming (`first_segment` as last-entry). Tests should cover revision negotiation, malformed/truncated SRH, non-type-4 routing headers, invalid `segments_left`, each comparison operator and inversion, masked SID matching, and boundary values at first/last segment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_srh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6table_filter.c -->
# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6table_filter.c

Purpose: Registers the legacy IPv6 `filter` table and its local-in, forward, and local-out hooks.

Important APIs/types/functions: Defines `packet_filter`, `filter_ops`, module parameter `forward`, `ip6table_filter_table_init`, pernet ops, `ip6table_filter_init`, and `ip6table_filter_fini`. It calls `ip6t_alloc_initial_table`, `ip6t_register_table`, `ip6t_unregister_table_exit`, `xt_hook_ops_alloc`, and xt template registration.

Control flow: Init allocates hook ops using `ip6t_do_table`, registers pernet state, then registers a template so namespaces get the filter table lazily or at init. Table init creates the standard initial table and sets the default FORWARD verdict from module parameter `forward`. Net pre-exit unregisters the table from hooks before final exit frees it. Module exit unregisters template/pernet ops and frees hook ops.

State and persistence: Per-net registered filter table and static hook ops persist while module is loaded. The `forward` parameter is read at table creation and controls initial FORWARD policy.

Dependencies/integration: Depends on legacy ip6tables core and x_tables hook/template APIs. Built by `CONFIG_IP6_NF_FILTER`.

Risks and test signals: Risks include hook-op allocation failure cleanup, namespace lifecycle ordering, default policy surprises from `forward`, and template registration rollback. Tests should load/unload module, create/destroy net namespaces, inspect initial policies with `forward=0/1`, replace rules under traffic, and verify pre-exit prevents hook use after table teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6table_filter.c -->
