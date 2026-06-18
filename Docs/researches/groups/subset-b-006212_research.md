# Research: subset-b-006212

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ila/ila_xlat.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ila/ila_xlat.c

Purpose: implements IPv6 Identifier-Locator Addressing translation for one network namespace. It stores locator-match mappings in an rhashtable, registers an IPv6 prerouting netfilter hook lazily on first mapping, and rewrites destination locators with `ila_update_ipv6_locator()` when a packet matches.

Important APIs, types, and functions: `struct ila_xlat_params` combines `struct ila_params` with an input ifindex discriminator; `struct ila_map` is the rhashtable object plus per-key RCU chain. `ila_xlat_nl_cmd_add_mapping()`, `ila_xlat_nl_cmd_del_mapping()`, `ila_xlat_nl_cmd_get_mapping()`, `ila_xlat_nl_cmd_flush()`, and dump start/done/dump implement generic-netlink control. `ila_xlat_init_net()`, `ila_xlat_pre_exit_net()`, and `ila_xlat_exit_net()` own per-net hash table, hook, and bucket-lock lifetime.

Control flow: netlink add parses locator, locator_match, checksum mode, identifier type, and ifindex; registers the prerouting hook if needed; allocates an `ila_map`; inserts it as either a new rhashtable head or an ordered per-key chain entry. Lookup uses `locator_match` as hash key and then filters by ifindex wildcard semantics. Packet flow enters `ila_nf_input()`, calls `ila_xlat_addr()`, looks up the destination locator under RCU, and rewrites in place if a mapping exists.

State and persistence: state is per-netns and memory-resident only. Mutations are serialized by per-bucket spinlocks plus a global mutex for hook registration. Readers are RCU-protected. Deletions use `kfree_rcu()`, and namespace teardown unregisters hooks before destroying the table and lock array.

Dependencies and integration points: depends on `ila.h`, rhashtable, generic netlink, netns generic storage, netfilter IPv6 prerouting, and ILA checksum/update helpers. It integrates with the ILA generic-netlink family defined elsewhere.

Risks: mapping ordering currently only scores ifindex specificity, so future wildcard dimensions must update `ila_order()` and comparison together. Flush walks and removes rhashtable entries while each per-locator lock is taken; iterator restart handling is important. Lazy hook registration means first add can fail due to netfilter registration errors. Packet rewrite assumes a pulled, valid IPv6 header.

Test signals: add/get/dump/delete/flush mappings through generic netlink; verify per-ifindex wildcard precedence; inject IPv6 packets with matching and non-matching locators; test namespace teardown with mappings present; run with RCU/debug lockdep to catch chain mutation issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ila/ila_xlat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/inet6_connection_sock.c -->
# sources/distributed-fs/ceph-client/net/ipv6/inet6_connection_sock.c

Purpose: provides IPv6 helpers for connection-oriented sockets, mainly route construction for requests and established sockets plus the common transmit path used by TCP-like IPv6 connection sockets.

Important APIs, types, and functions: `inet6_csk_route_req()` builds a `flowi6` for a request socket; `inet6_csk_route_socket()` builds and caches a route for an established socket; `inet6_csk_xmit()` transmits a corked skb via `ip6_xmit()`. `inet_request_sock`, `ipv6_pinfo`, `inet_sock`, and `flowi6` are the central data structures.

Control flow: route helpers zero and fill `flowi6` with protocol, addresses, ports, mark, output interface, uid, flowlabel, ECN, and security classification. They call `fl6_update_dst()` under RCU to account for routing-header final destinations, then call `ip6_dst_lookup_flow()`. `inet6_csk_xmit()` first checks the cached dst cookie, refreshes routing on miss, attaches the dst without taking another ref, and calls `ip6_xmit()` with socket options and traffic class.

State and persistence: no long-lived state is defined here; it uses socket route cache state through `ip6_dst_store()` and `__sk_dst_check()`. Soft route errors are persisted into `sk_err_soft`, and route caps are cleared when lookup fails.

Dependencies and integration points: integrates with IPv6 route lookup, security hooks, flowlabel/extension options, ECN, sock reuseport headers, and the generic inet connection-socket layer. `inet6_csk_xmit()` is exported GPL for protocol users.

Risks: incorrect `fl6_update_dst()` handling can route to a final destination but must restore `fl6->daddr` for later socket use. Route lookup errors free the skb and return a negative errno, so callers must not reuse it. Cached dst correctness depends on `np->dst_cookie`.

Test signals: request-socket SYN/ACK routing with source routing options, established TCP transmit after route invalidation, bound-device and mark-based routing, security classification hooks, and error-path tests where route lookup fails and skb ownership is consumed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/inet6_connection_sock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/inet6_hashtables.c -->
# sources/distributed-fs/ceph-client/net/ipv6/inet6_hashtables.c

Purpose: implements IPv6 transport socket hash operations for established lookups, listener selection, reuseport, BPF sk_lookup redirection, and active-connect port hashing.

Important APIs, types, and functions: `inet6_init_ehash_secret()`, `inet6_ehashfn()`, `__inet6_lookup_established()`, `inet6_lookup_listener()`, `inet6_lookup()`, `inet6_lookup_reuseport()`, `inet6_lookup_run_sk_lookup()`, and `inet6_hash_connect()`. Internal helpers include `compute_score()`, `inet6_lhash2_lookup()`, `__inet6_check_established()`, and `inet6_sk_port_offset()`.

Control flow: established lookup computes the ehash over local/remote IPv6 addresses, ports, and net hash mix; it walks the nulls hlist under RCU, validates `inet6_match()`, takes a ref, and revalidates after ref acquisition. Listener lookup first gives BPF sk_lookup a chance to redirect, then searches address-specific and wildcard listener buckets, choosing the highest score for address/device/CPU affinity and optionally applying SO_REUSEPORT selection. Active connect initializes hash secrets, derives an ephemeral-port offset from secure IPv6 port hashing, precomputes the zero-local-port hash, and delegates range probing to `__inet_hash_connect()`.

State and persistence: global hash secrets are initialized once. Socket state lives in shared inet hashinfo tables owned by the TCP death row. The check-established path mutates `inet_num`, `inet_sport`, `sk_hash`, the ehash bucket, timewait recycling stats, and protocol in-use counters under bucket locks.

Dependencies and integration points: relies on `net->ipv4.tcp_death_row.hashinfo` for IPv6 TCP hash tables, reuseport core, BPF sk_lookup, secure sequence/port hashing, l3mdev-bound-device matching, and TCP timewait uniqueness logic.

Risks: nulls-list restarts are required when concurrent mutations move entries. RCU-only duplicate checks in `__inet6_check_established()` are intentionally advisory and must be followed by locked insertion. Listener scoring must keep wildcard fallback and bound-device semantics compatible with IPv4 behavior. Reuseport selection requires stable hash parity with UDP/TCP fallback paths.

Test signals: high-concurrency connect bind collisions, TIME_WAIT reuse, SO_REUSEPORT distribution with BPF and without BPF, VRF/l3mdev-bound sockets, wildcard vs address-specific listeners, and RCU/hash debug tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/inet6_hashtables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ioam6.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ioam6.c

Purpose: implements IPv6 In-situ OAM namespace/schema management, generic-netlink events, and trace-data filling. It owns per-net namespace/schema rhashtables and exposes helpers used by IOAM Hop-by-Hop processing and lightweight tunnels.

Important APIs, types, and functions: `ioam6_namespace()`, `ioam6_trace_compute_nodelen()`, `ioam6_fill_trace_data()`, `ioam6_event()`, `ioam6_init()`, and `ioam6_exit()` are externally relevant. Netlink operations add/delete/dump namespaces, add/delete/dump schemas, and bind/unbind a schema to a namespace. Core objects are `struct ioam6_namespace`, `struct ioam6_schema`, and `struct ioam6_pernet_data`.

Control flow: per-net init allocates the data object, initializes a mutex and two rhashtables, and stores it in `net->ipv6.ioam6_data`. Netlink add/del operations validate required attributes, serialize under the per-net mutex, and mutate rhashtables with RCU freeing. Schema binding updates both sides of the namespace-schema relationship with RCU assignments. Trace filling computes the data insertion pointer from remaining length, node length, and optional schema length, then writes selected IOAM fields such as hop limit/node id, ingress/egress ids, timestamps, namespace data, queue backlog, wide fields, and opaque schema data.

State and persistence: namespace and schema state is per-net and memory-only. Relationships are one-to-one: assigning a schema detaches any previous namespace using that schema and detaches the namespace's previous schema. Trace data is packet-local. Netlink multicast events are transient.

Dependencies and integration points: depends on generic netlink, rhashtable, `net/ioam6.h`, IPv6 addrconf per-device IOAM ids, qdisc queue stats, skb timestamps, pernet subsystem registration, and optional `ioam6_iptunnel_init()`.

Risks: this snapshot contains a duplicated `err = rhashtable_remove_fast(&nsdata->schemas, &sc->head,` line in `ioam6_genl_delsc()`, which is a compile-break signal unless it is intentional source corruption. Trace field writes are pointer arithmetic over packed protocol data and depend on correct `remlen`/`nodelen` validation. Queue-depth sampling locks the qdisc in softirq context. Undefined trace bits are filled with unavailable values, so spec changes need mask updates.

Test signals: netlink add/delete/dump namespace and schema operations, schema reassignment races under lockdep/RCU, trace filling for every supported bit including overflow, namespace data endian checks, qdisc backlog sampling, multicast listener events, and build coverage with `CONFIG_IPV6_IOAM6_LWTUNNEL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ioam6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ioam6_iptunnel.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ioam6_iptunnel.c

Purpose: implements the IOAM6 lightweight tunnel encapsulation type. It builds lwtunnel state from netlink route attributes, inserts IOAM Hop-by-Hop options either inline or by IPv6-in-IPv6 encapsulation, fills trace data, caches routes, and serializes state back to netlink.

Important APIs, types, and functions: `struct ioam6_lwt`, `struct ioam6_lwt_encap`, `ioam6_build_state()`, `ioam6_output()`, `ioam6_destroy_state()`, `ioam6_fill_encap_info()`, `ioam6_encap_cmp()`, `ioam6_iptunnel_init()`, and `ioam6_iptunnel_exit()`.

Control flow: build-state parses frequency `k/n`, mode, optional source, required destination for non-inline modes, and a trace header. It validates trace type/remlen, allocates lwtunnel state with aligned trace storage, initializes a dst cache and a fake `null_dst`, and constructs the Hop-by-Hop IOAM option blob. Output applies frequency sampling, retrieves or resolves a cached route, performs inline insertion if no Hop-by-Hop header already exists or encap insertion for tunnel/auto modes, fills IOAM data through `ioam6_do_fill()`, then either redirects to the new dst output or calls the original output to avoid lwtunnel reentry.

State and persistence: route-attached lwtunnel state persists with the route. It contains frequency counters, route cache, mode, tunnel endpoints, and immutable tunnel option template. `pkt_cnt` is atomic and per-state. The fake `null_dst` marks the case where transformed packets still use the original route.

Dependencies and integration points: integrates with lwtunnel encap ops, IPv6 route output, dst_cache, skb headroom/csum helpers, IOAM namespace lookup and trace fill, route netlink attribute validation, and IPv6 source address selection.

Risks: inline insertion refuses packets that already have Hop-by-Hop headers, so policy must expect skipped insertion. The fake dst-cache sentinel relies on careful refcount balancing and must not escape into normal routing. Frequency `pkt_cnt % n` behavior depends on validation preventing zero. Trace validation rejects undefined bits but future IOAM bits require updates.

Test signals: route add/dump/delete with IOAM lwt attributes, inline/encap/auto mode output, k-over-n sampling, route-cache invalidation, same-dst sentinel behavior, source selection with and without explicit source, insufficient headroom failure paths, and trace overflow cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ioam6_iptunnel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_checksum.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ip6_checksum.c

Purpose: provides generic IPv6 pseudo-header checksum support when an architecture does not override it, plus a helper for setting UDP checksums on IPv6 UDP tunnel packets.

Important APIs, types, and functions: `csum_ipv6_magic()` folds source address, destination address, length, protocol, and an existing checksum into an IPv6 pseudo-header checksum. `udp6_set_csum()` sets `struct udphdr.check` for nocheck, GSO, CHECKSUM_PARTIAL, and software-prepared partial checksum cases.

Control flow: `csum_ipv6_magic()` accumulates each 32-bit address word and pseudo-header field with explicit carry handling, then folds the sum. `udp6_set_csum()` either writes zero for nocheck, writes the complemented pseudo-header checksum for GSO or newly partial skbs, or combines an existing LCO checksum for `CHECKSUM_PARTIAL`, converting zero to `CSUM_MANGLED_0`.

State and persistence: no persistent state. It mutates skb checksum metadata (`ip_summed`, `csum_start`, `csum_offset`) and UDP header checksum fields.

Dependencies and integration points: used by IPv6 UDP, tunnel, and checksum-offload paths. Depends on `udp_hdr()`, `udp_v6_check()`, `lco_csum()`, and architecture checksum primitives.

Risks: checksum mode transitions are subtle; callers must have transport headers set correctly. `nocheck` creates zero UDP checksums, which is only valid where upper-layer policy permits it. Incorrect length or address inputs silently produce bad checksums.

Test signals: checksum unit tests against known pseudo-header vectors, UDP tunnel packets with GSO and non-GSO skbs, CHECKSUM_PARTIAL paths with LCO, zero-checksum mangling, and architecture builds with and without `_HAVE_ARCH_IPV6_CSUM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_checksum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_fib.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ip6_fib.c

Purpose: implements the IPv6 Forwarding Information Database radix tree, per-net FIB table lifecycle, route add/delete/lookup/walk/dump, route garbage collection, notifier integration, and `/proc/net/ipv6_route` iteration.

Important APIs, types, and functions: exported or cross-module functions include `fib6_info_alloc()`, `fib6_info_destroy_rcu()`, `fib6_new_table()`, `fib6_get_table()`, `fib6_lookup()`, `fib6_tables_dump()`, `fib6_metric_set()`, `fib6_add()`, `fib6_node_lookup()`, `fib6_locate()`, `fib6_del()`, `fib6_clean_all()`, `fib6_run_gc()`, `fib6_init()`, and `fib6_gc_cleanup()`. Core types are `fib6_node`, `fib6_info`, `fib6_table`, `fib6_walker`, and `fib6_cleaner`.

Control flow: per-net init creates stats, table hash, main/local tables, walker locks, and GC timer. Adds descend or split the radix tree with `fib6_add_1()`, optionally enter source-specific subtrees, then insert or replace `fib6_info` in metric order with ECMP sibling handling and notifier emission. Deletes unlink a route, rebalance siblings, adjust active walkers, repair empty intermediate nodes, purge cached routes/exceptions, and notify listeners. Lookups descend by destination and optional source prefix then backtrack to the longest valid route node. Dumps and proc iteration use reentrant walkers that can suspend and resume after skb fill or tree serial changes. GC scans per-table gc lists for expiring routes and exceptions and reschedules the per-net timer if more work remains.

State and persistence: all state is per network namespace and memory-resident: FIB table hash, radix nodes from `fib6_node_kmem`, route entries, peer bases, route stats, serial numbers, walker list, and GC timer. RCU protects readers; table locks protect mutations. `fn_sernum` and table `fib_seq` signal route changes to caches, dumps, and notifiers.

Dependencies and integration points: integrates with IPv6 route lookup/output code, rtnetlink `RTM_GETROUTE`, fib notifier chains, nexthop objects, lightweight tunnels, addrconf routes, dst metrics, exception caches, BPF iterators, procfs, and optional multiple-table/source-subtree configs.

Risks: this snapshot shows duplicated or malformed source fragments around `call_fib6_multipath_entry_notifiers()` and a duplicated comment terminator near tree insertion, which are compile-risk signals. Algorithmically, radix tree repair and active walker adjustment are high-risk because deletion can occur during dumps/GC. ECMP sibling counters use `BUG_ON()` for invariant breaks. Per-cpu cached route cleanup must be synchronized with `fib6_destroying` and memory barriers.

Test signals: route add/replace/delete with and without `NLM_F_CREATE`/`NLM_F_REPLACE`, source-specific routes, ECMP append/replace/delete, nexthop object deletion, concurrent route dumps while mutating routes, GC of expiring addrconf routes and exceptions, namespace teardown, proc/BPF route iteration, and lockdep/RCU coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_fib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_flowlabel.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ip6_flowlabel.c

Purpose: manages IPv6 flow labels, including global label allocation, per-socket label references, option merging, renewal/release semantics, procfs listing, and per-net cleanup.

Important APIs, types, and functions: `__fl6_sock_lookup()`, `fl6_free_socklist()`, `fl6_merge_options()`, `ipv6_flowlabel_opt_get()`, `ipv6_flowlabel_opt()`, `ip6_flowlabel_init()`, and `ip6_flowlabel_cleanup()`. Internal lifecycle functions include `fl_create()`, `fl_intern()`, `fl_release()`, `ip6_fl_gc()`, `ip6_fl_purge()`, `ipv6_flowlabel_get()`, `ipv6_flowlabel_put()`, and `ipv6_flowlabel_renew()`.

Control flow: GET validates a user request, optionally enables TCP reflected flow labels, creates a candidate `ip6_flowlabel`, checks sharing and ownership rules, interns or reuses a global label, and links it into the socket list. PUT removes a socket reference or disables reflected flow labels. RENEW updates linger and expiration on an owned label or, with admin capability, a global label. GC walks hash buckets and frees unused labels after linger/expiration.

State and persistence: `fl_ht` is a global RCU hash table of labels, `fl_size` tracks total count, each net namespace tracks `flowlabel_count`, and each socket has an RCU list of `ipv6_fl_socklist` references. Timed lifetime is controlled by `ip6_fl_gc_timer`, `lastuse`, `linger`, and `expires`. A deferred static key tracks labels that require exclusive/option consistency checks.

Dependencies and integration points: integrates with socket options, IPv6 datagram control parsing, raw/transport IPv6, procfs seq_file, pid namespaces, capabilities, network namespace teardown, and static branch infrastructure.

Risks: this snapshot contains duplicated `label &= IPV6_FLOWLABEL_MASK;` and duplicated `inet6_clear_bit(REPFLOW, sk);` lines; those are likely harmless but indicate source hygiene issues. Lock ordering between global label lock and socket-list lock is important. User-provided control options are copied and parsed; failures must clean up partially allocated options and pid refs. Limits differ for privileged and unprivileged users, so mem_check coverage matters.

Test signals: socket option GET/PUT/RENEW for every share mode, random and explicit label allocation, exclusive/process/user sharing enforcement, unprivileged resource-limit failures, reflected TCP flow labels, proc output across pid namespaces, GC after linger/expires, and netns purge with outstanding references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_flowlabel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_gre.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ip6_gre.c

Purpose: implements GRE, GRETAP, and ERSPAN tunneling over IPv6. It registers the IPv6 GRE protocol handler, rtnetlink link kinds, per-net fallback devices, tunnel lookup tables, xmit/receive paths, ioctl compatibility, and netdevice lifecycle.

Important APIs, types, and functions: core helpers include `ip6gre_tunnel_lookup()`, `ip6gre_tunnel_link()`, `ip6gre_tunnel_unlink()`, `ip6gre_tunnel_find()`, `ip6gre_tunnel_locate()`, `gre_rcv()`, `ip6gre_rcv()`, `ip6erspan_rcv()`, `ip6gre_tunnel_xmit()`, `ip6erspan_tunnel_xmit()`, `ip6gre_newlink()`, `ip6gre_changelink()`, `ip6erspan_newlink()`, `ip6erspan_changelink()`, `ip6gre_init()`, and `ip6gre_fini()`. Main state is `struct ip6gre_net` and `struct ip6_tnl`.

Control flow: receive parses GRE headers, strips the GRE header, dispatches ERSPAN or normal GRE, looks up a tunnel by local/remote/key/device type/link specificity, attaches collect-metadata dst info when configured, and hands the skb to `ip6_tnl_rcv()`. Transmit validates the payload, prepares flowi6/tclass/encap-limit from IPv4, IPv6, other payload, or metadata, builds GRE or ERSPAN headers, handles offloads, and calls `ip6_tnl_xmit()`, sending ICMP errors on MTU failures. Netlink create/change parses attributes, validates GRE/ERSPAN constraints, registers netdevices, configures MTU/headroom/features, and links tunnels into per-net hash buckets.

State and persistence: per-net state stores four hash tables for exact/wildcard remote/local matching, collect-metadata tunnel pointers, and fallback device. Tunnel devices hold parameters, dst cache, gro cells, sequence counter, encapsulation settings, and cached flow template. Module init registers pernet ops, protocol handler, and link ops; exit unregisters them.

Dependencies and integration points: depends on IPv6 tunnel core, GRE helpers, ERSPAN helpers, rtnetlink, netdevice ops, dst metadata, XFRM/route/PMTU helpers, ICMPv4/v6 error senders, GRO/GSO offload helpers, and namespace generic storage.

Risks: this snapshot includes duplicate declarations in `ip6gre_rcv()` and duplicate `.flags = INET6_PROTO_FINAL`, suggesting compile-risk source corruption. Normal operation is sensitive to tunnel lookup precedence, collect-metadata uniqueness, ERSPAN version-specific metadata length, and sequence/key flag validation. Teardown must unlink devices from hash/metadata pointers before dst cache cleanup. MTU/headroom calculations vary by GRE, GRETAP, ERSPAN, encap-limit, and metadata modes.

Test signals: module load/unload, creation/change/deletion of `ip6gre`, `ip6gretap`, and `ip6erspan` links; ioctl add/change/delete; keyed and keyless receive lookup precedence; collect-metadata RX/TX; IPv4/IPv6/other payload transmit; ERSPAN v1/v2 metadata; PMTU and ICMP error paths; fallback tunnel behavior; namespace teardown with moved tunnel devices; and offload/GSO tests with checksum and sequence flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_gre.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_icmp.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ip6_icmp.c

Purpose: provides `icmpv6_ndo_send()` for network-device style IPv6 ICMP error sending when NAT connection tracking may require source-address restoration.

Important APIs, types, and functions: `icmpv6_ndo_send()` is exported when IPv6 and NF NAT are enabled. It uses `nf_ct_get()`, conntrack NAT status, `skb_clone()`, `skb_ensure_writable()`, and `icmp6_send()`.

Control flow: if no conntrack entry exists or NAT is not active, the helper sends ICMPv6 directly. For NATed packets it clones shared skbs, validates that the IPv6 header is writable and in bounds, temporarily replaces the source address with the original conntrack tuple source for the packet direction, sends ICMPv6, restores the address, and consumes any clone.

State and persistence: no persistent state. It temporarily mutates an skb IPv6 source address and restores it before return.

Dependencies and integration points: used by tunnel/device transmit paths that need ICMPv6 errors in ndo context. Integrates with nf_conntrack/NAT and core ICMPv6 send logic.

Risks: compiled only under `CONFIG_IPV6` and `CONFIG_NF_NAT`; callers need fallback awareness when unavailable. Writable-header checks must remain strict to avoid corrupting malformed skbs. Temporary header mutation makes clone/writeability correctness critical.

Test signals: NATed tunnel PMTU/error generation, non-NAT direct ICMPv6 send, shared skb clone path, malformed/truncated skb rejection, and build matrix with NAT enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_icmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_input.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ip6_input.c

Purpose: implements IPv6 packet ingress from L2 handoff through header validation, early demux, netfilter prerouting/local-in hooks, route input, protocol delivery, and multicast local/forward split.

Important APIs, types, and functions: `ipv6_rcv()`, `ipv6_list_rcv()`, `ip6_rcv_finish()`, `ip6_input()`, `ip6_mc_input()`, and `ip6_protocol_deliver_rcu()`. Internal helpers include `ip6_rcv_core()`, `tcp_v6_early_demux()`, `ip6_list_rcv_finish()`, and `ip6_input_finish()`.

Control flow: `ip6_rcv_core()` drops otherhost packets, checks device IPv6 state, clears IP6CB, records ingress ifindex, validates header version, ECN stats, loopback/multicast-source/scope rules, payload length, and Hop-by-Hop options, then orphans prefetched sockets as needed. Single-packet receive enters `NF_INET_PRE_ROUTING`, finishes with route input and `dst_input()`. List receive batches by device/net and route destination hints to reduce repeated lookups. Local input enters `NF_INET_LOCAL_IN`, clears delivery time, and delivers by walking extension-header protocol handlers until a final protocol is reached. Multicast input updates stats, optionally clones for multicast routing, and locally delivers only subscribed or MLD packets.

State and persistence: no persistent state, but it updates per-net/per-device IPv6 MIB counters, skb control block fields, skb dst/sk ownership, and drop reasons. It consumes or frees skbs on most paths.

Dependencies and integration points: integrates with netfilter IPv6 hooks, XFRM policy, raw IPv6 sockets, TCP/UDP handlers, early-demux socket lookup, IPv6 routing, l3mdev/VRF, addrconf, multicast routing, dst metadata, and ICMPv6 parameter-problem generation.

Risks: packet ownership is complex: handlers may consume skb, return a next protocol, or require discard. Extension-header recursion is bounded by `IP6_MAX_EXT_HDRS_CNT`; missing bounds would permit pathological packets. Multicast forwarding clone decisions must not double-free. The discard path increments `IPSTATS_MIB_INDISCARDS` twice in this snapshot, which may be intentional in this tree or a stats bug worth checking.

Test signals: malformed header/payload length/drop-reason tests, early demux for TCP/UDP with cached dst, netfilter prerouting/local-in order, extension-header chains and unknown protocols, XFRM policy rejects, multicast subscription and MLD router-alert handling, list receive batching, and VRF/l3mdev ingress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_offload.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ip6_offload.c

Purpose: registers and implements IPv6 GSO/GRO packet offload handling, including extension-header parsing and offload support for IPv6-in-IPv4/SIT, IPv6-in-IPv6, and IPv4-in-IPv6 tunnels.

Important APIs, types, and functions: `ipv6_gso_segment()`, `ipv6_gro_receive()`, `ipv6_gro_complete()`, `ipv6_offload_init()`, and tunnel callbacks `sit_*`, `ip4ip6_*`, and `ip6ip6_*`. It includes `tcpv6_offload.c` and initializes TCP and extension-header offloads.

Control flow: GSO resets headers, pulls the IPv6 header and registered extension headers marked `INET6_PROTO_GSO_EXTHDR`, delegates segmentation to the next protocol offload, then fixes payload lengths and fragment headers for UDP fragmentation. GRO reads the IPv6 header from the GRO cursor, compares flow keys across the GRO list ignoring length and traffic class, pulls extension headers, sets transport offsets, and delegates to TCP, UDP, or generic protocol offload. GRO complete updates payload length, skips extension headers, and completes the inner protocol, marking encapsulation for tunnel callbacks.

State and persistence: initialization stores an IPv6 `packet_offload` in `net_hotdata.ipv6_packet_offload`, adds it to device offload lists, and registers inet/inet6 tunnel offloads. Runtime state is skb/GRO/GSO metadata only.

Dependencies and integration points: depends on global `inet6_offloads`, `net_hotdata` TCP/UDP offload structs, device offload registration, GRO/GSO helpers, TCPv6 and UDPv6 offload code, and extension-header offload init.

Risks: extension-header parsing assumes registered offload flags accurately identify headers safe to skip. Fragment offset fixups for UDP GSO are sensitive to payload length calculations. The file directly includes `tcpv6_offload.c`, so build ordering and symbol visibility differ from normal separate compilation. Encapsulation feature masking must respect hardware offload capabilities.

Test signals: TCPv6/UDPv6 GRO and GSO, packets with Hop-by-Hop/Destination/Routing extension headers, UDP fragmentation GSO, nested IPv6 tunnels, SIT/ip4ip6/ip6ip6 GRO complete, hardware feature masking for encapsulation, and failure paths for missing protocol offloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_offload.h -->
# sources/distributed-fs/ceph-client/net/ipv6/ip6_offload.h

Purpose: declares IPv6 offload initialization/exit hooks shared by the IPv6 offload compilation units.

Important APIs, types, and functions: declares `ipv6_exthdrs_offload_init()`, `udpv6_offload_init()`, `udpv6_offload_exit()`, and `tcpv6_offload_init()`.

Control flow: no runtime control flow is implemented here. The header is included by `ip6_offload.c`, which calls TCP and extension-header initialization during `fs_initcall`.

State and persistence: none.

Dependencies and integration points: bridges `ip6_offload.c` with TCPv6, UDPv6, and extension-header offload implementation files. Include guards prevent repeated declarations.

Risks: declarations must match implementations exactly, especially return type for `udpv6_offload_exit()` which is declared `int`. Missing declarations for exit paths can hide unregister asymmetry in module or init error handling.

Test signals: compile coverage with IPv6 offload enabled, symbol mismatch checks, and init/exit path coverage for UDP/TCP/extension-header offloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ip6_offload.h -->
