# Research Group: subset-b-006198

This grouped report covers the requested IPv4 networking sources in `sources/distributed-fs/ceph-client/net/ipv4`. Each section is source-path aligned for reconciliation into one per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/fib_trie.c -->
# sources/distributed-fs/ceph-client/net/ipv4/fib_trie.c

## Purpose
`fib_trie.c` implements the IPv4 FIB table backing store using a level-compressed trie. It is the route insertion, deletion, lookup, flush, notification, dump, and procfs inspection engine behind IPv4 routing tables. The implementation optimizes longest-prefix match with compressed path traversal and adaptive tnode resizing.

## Important APIs, Types, And Functions
Core data structures are `struct key_vector`, `struct tnode`, `struct trie`, `struct fib_alias`, and `struct fib_table`. Leaves hold hlist chains of aliases sorted by suffix length, table id, DSCP, and priority; internal tnodes hold child vectors plus parent, empty-child, and full-child accounting.

External entry points include `fib_table_insert`, `fib_table_delete`, `fib_table_lookup`, `fib_table_dump`, `fib_table_flush`, `fib_table_flush_external`, `fib_trie_unmerge`, `fib_trie_table`, `fib_free_table`, `fib_notify`, `fib_info_notify_update`, `fib_alias_hw_flags_set`, `fib_proc_init`, and `fib_proc_exit`. `fib_table_lookup` and `fib_lookup_good_nhc` are exported for route resolution. Initialization creates `ip_fib_alias` and `ip_fib_trie` slab caches in `fib_trie_init`.

Internal maintenance revolves around `fib_find_node`, `fib_find_alias`, `fib_insert_node`, `fib_insert_alias`, `fib_remove_alias`, `leaf_walk_rcu`, `resize`, `inflate`, `halve`, `collapse`, `node_push_suffix`, and `node_pull_suffix`.

## Control Flow
Insert starts by building a `fib_info`, locating the leaf for `cfg->fc_dst`, then finding the insertion point for the prefix suffix length, DSCP, table id, and priority. Existing exact entries honor `NLM_F_EXCL`, `NLM_F_REPLACE`, and `NLM_F_APPEND`. Replacements allocate a new alias, swap it with `hlist_replace_rcu`, notify listeners if it is the effective route, emit `RTM_NEWROUTE`, and release the old `fib_info`. Creates allocate a `fib_alias`, insert it into an existing leaf or create a new leaf/tnode path, update default-route count, flush route cache, and emit netlink notifications.

Lookup descends by key from the trie root, checks compressed-prefix mismatches, then backtracks through candidate prefixes until a semantic match succeeds. Alias filtering checks prefix coverage, DSCP mask, dead `fib_info`, scope, route type error, nexthop object state, link-down policy, requested output interface, and nexthop selection. On success it fills `struct fib_result`; on miss it backtracks until no candidate remains and returns `-EAGAIN`.

Delete finds the leaf and alias matching route config, sends delete or replace notifier semantics based on the next visible alias, emits `RTM_DELROUTE`, removes the alias, possibly removes the leaf, rebalances the trie, releases `fib_info`, and frees alias memory through RCU.

Flush walks the trie in reverse order, removing dead or error aliases, updating suffixes, resizing tnodes, and emitting notifications when needed. Dump and notification paths use `leaf_walk_rcu` to produce netlink rows or notifier events without changing trie structure. Procfs iterators render `/proc/net/fib_trie`, `/proc/net/fib_triestat`, and `/proc/net/route`.

## State And Persistence
State is in memory per network namespace as `fib_table` objects in `net->ipv4.fib_table_hash`. Tables may share trie data for local/main aliasing until `fib_trie_unmerge` clones local entries. Memory is RCU protected for readers and RTNL protected for writers. Freed tnodes and aliases are deferred through `call_rcu`; bulk dirty trie memory is throttled by `sysctl_fib_sync_mem`. Optional per-CPU trie stats persist for table lifetime when `CONFIG_IP_FIB_TRIE_STATS` is enabled.

## Dependencies And Integration Points
This file integrates with route netlink (`rtmsg_fib`, `fib_dump_info`), FIB notifier chains (`call_fib4_notifier(s)`), nexthop and `fib_info` management, route cache flushing, IPv4 sysctls, procfs seq files, tracepoints, RCU, RTNL, slab/vmalloc allocation, and network namespace table hashes. Consumers depend on the lookup contract and on dump/notify ordering for route monitoring.

## Risks
The riskiest areas are RCU/list lifetime, tnode resize correctness, alias ordering, and semantic lookup backtracking. A wrong suffix update can lose longest-prefix matches. Replacement notification rollback must preserve alias ordering and references. Shared trie aliasing between local and main tables makes flush/unmerge behavior subtle. Procfs and dump iterators must not dereference freed nodes while walking under RCU.

## Test Signals
Useful signals include route add/replace/delete coverage through rtnetlink, DSCP route lookup tests, multipath and nexthop link-state lookup tests, local/main table unmerge tests, route flush tests with dead nexthops and error routes, notifier behavior for first-visible alias changes, `/proc/net/route` compatibility checks, `/proc/net/fib_trie` traversal under concurrent updates, and stress tests with route churn under RCU debugging and KASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/fib_trie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/fou_bpf.c -->
# sources/distributed-fs/ceph-client/net/ipv4/fou_bpf.c

## Purpose
`fou_bpf.c` exposes unstable TC-BPF kfunc helpers for configuring and reading FOU/GUE tunnel encapsulation metadata on sk_buffs that use collect-metadata IP tunnel devices.

## Important APIs, Types, And Functions
The local `struct bpf_fou_encap` carries UDP source and destination ports. `enum bpf_fou_encap_type` selects FOU or GUE. The kfuncs are `bpf_skb_set_fou_encap` and `bpf_skb_get_fou_encap`, registered through `register_fou_bpf` using a `btf_kfunc_id_set` for `BPF_PROG_TYPE_SCHED_CLS`.

## Control Flow
`bpf_skb_set_fou_encap` treats the BPF context as `struct sk_buff`, retrieves `skb_tunnel_info`, validates that metadata exists and is TX metadata, maps the requested type to `TUNNEL_ENCAP_FOU`, `TUNNEL_ENCAP_GUE`, or `TUNNEL_ENCAP_NONE`, mirrors checksum intent from `IP_TUNNEL_CSUM_BIT`, and stores UDP ports in `info->encap`. `bpf_skb_get_fou_encap` validates tunnel info and copies the stored ports back to BPF memory.

## State And Persistence
The file does not own persistent state. It mutates per-packet tunnel metadata inside `struct ip_tunnel_info`. Registration persists only as module-owned BTF kfunc metadata and depends on the FOU module lifetime.

## Dependencies And Integration Points
It depends on BPF kfunc/BTF infrastructure, `dst_metadata` tunnel metadata, `net/fou.h`, and the FOU core module that calls `register_fou_bpf` during initialization. It is intended for TC classifier programs after `bpf_skb_set_tunnel_key` has already populated IP tunnel key fields.

## Risks
This is explicitly unstable API surface. Main behavioral risks are accepting packets without TX tunnel metadata, stale encap flags if type is invalid, and verifier or BTF registration regressions. Since BPF programs supply `encap`, NULL checking is essential.

## Test Signals
Test with TC-BPF programs on collect-metadata IPIP tunnels that set FOU and GUE ports, verify generated tunnel packets, verify checksum flag propagation, reject missing tunnel metadata, reject NULL encap pointers, and ensure kfunc registration appears only for scheduler classifier programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/fou_bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/fou_core.c -->
# sources/distributed-fs/ceph-client/net/ipv4/fou_core.c

## Purpose
`fou_core.c` implements Foo-over-UDP and Generic UDP Encapsulation support for IPv4 and optionally IPv6 sockets. It creates UDP tunnel sockets, receives and decapsulates FOU/GUE traffic, provides GRO/GSO integration, exposes generic netlink control, exports tunnel header builders, and registers IP tunnel encapsulation operations.

## Important APIs, Types, And Functions
`struct fou` is the per-port object with socket, protocol, flags, port, address family, encap type, list node, and RCU head. `struct fou_cfg` contains parsed netlink/UDP socket configuration. Per-net state is `struct fou_net`, a list plus mutex.

Receive paths are `fou_udp_recv` and `gue_udp_recv`. GRO paths are `fou_gro_receive`, `fou_gro_complete`, `gue_gro_receive`, and `gue_gro_complete`. Configuration paths are `parse_nl_config`, `fou_nl_add_doit`, `fou_nl_del_doit`, `fou_nl_get_doit`, and `fou_nl_get_dumpit`. Tunnel export functions include `fou_encap_hlen`, `gue_encap_hlen`, `__fou_build_header`, and `__gue_build_header`. Optional IP tunnel operations are registered by `ip_tunnel_encap_add_fou_ops`.

## Control Flow
Netlink add parses address family, local/peer ports, local/peer addresses, interface binding, encap type, IP protocol, and remcsum flag into `fou_cfg`. `fou_create` opens a UDP socket, allocates `struct fou`, installs UDP tunnel callbacks, sets `sk_user_data`, marks allocation atomic, and inserts the object into the per-net list after duplicate detection. Delete parses the same identity and calls `fou_destroy`, which removes the list entry, releases the UDP tunnel socket, and frees the object with RCU.

FOU direct receive removes the UDP header, updates IPv4 total length or IPv6 payload length, pulls checksum state, resets transport header, calls `iptunnel_pull_offloads`, and returns negative protocol to the UDP tunnel core. GUE receive validates the base header, supports version 1 direct IPv4/IPv6 encapsulation, validates optional flags for version 0, handles private remote-checksum data, drops unsupported control messages, pulls GUE/UDP headers, and returns the encapsulated protocol.

GRO mirrors the decapsulation logic without fully linearizing the packet. It identifies the next protocol's `net_offload`, marks FOU state in `NAPI_GRO_CB`, validates GUE headers and optional fields, handles remote checksum offload, compares GUE headers across candidate packets, and delegates to the inner protocol GRO callbacks. Completion delegates to the inner offload and sets inner MAC headers.

Transmit header builders prepare tunnel offload state with `iptunnel_handle_offloads`, choose a UDP source port from flow hash if not configured, optionally build a GUE private remcsum option, push the GUE header, then optional IP tunnel ops push the UDP header and set checksum.

## State And Persistence
FOU state is per network namespace. Each `struct fou` persists until netlink deletion or namespace teardown. It owns a UDP socket and is discoverable by list under `fou_lock`. Socket `sk_user_data` points to the FOU object and is read under socket/RCU conventions. Module init registers pernet state, generic netlink family, BPF kfuncs, and tunnel encap ops; module exit reverses these and closes all sockets.

## Dependencies And Integration Points
The file depends on UDP tunnel socket infrastructure, generic netlink policy/ops from `fou_nl.c`, BPF registration from `fou_bpf.c`, GUE helpers, IP tunnel encap registration, inet and inet6 offload tables, ICMP error dispatch through `inet_protos`, and network namespace generic storage. User space configures it through the `fou` generic netlink family defined by UAPI `linux/fou.h`.

## Risks
Header length and checksum manipulation are the main risk. GUE option validation, remote checksum offsets, and GRO remcsum state must remain consistent with skb pulls. Duplicate detection must include family, local/peer ports, addresses, and bound interface. The netlink parser allows partial identities, so add/delete/get must reject ambiguous cases where required peer or bind information is missing. Error handlers must avoid recursion for UDP-in-GUE.

## Test Signals
Test netlink add/get/dump/delete for IPv4, IPv6, peer-bound, and device-bound sockets; duplicate add should return `-EALREADY`. Exercise FOU direct and GUE v0/v1 receive, malformed GUE option drops, remote checksum offload, GRO aggregation and flush decisions, tunnel transmit with checksum and remcsum flags, ICMP error propagation, namespace teardown cleanup, and module init failure unwind after each registration step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/fou_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/fou_nl.c -->
# sources/distributed-fs/ceph-client/net/ipv4/fou_nl.c

## Purpose
`fou_nl.c` is generated generic-netlink glue for the FOU family. It defines attribute validation policy and operation dispatch entries used by `fou_core.c`.

## Important APIs, Types, And Functions
The file exports `fou_nl_policy[FOU_ATTR_IFINDEX + 1]` and `fou_nl_ops[3]`. Policy entries type-check local port, address family, IP protocol, encap type, remote checksum flag, IPv4/IPv6 local and peer addresses, peer port, and interface index. Operations map `FOU_CMD_ADD`, `FOU_CMD_DEL`, and `FOU_CMD_GET` to `fou_nl_add_doit`, `fou_nl_del_doit`, `fou_nl_get_doit`, and `fou_nl_get_dumpit`.

## Control Flow
Generic netlink validates incoming attributes against `fou_nl_policy` and dispatches commands through `fou_nl_ops`. Add and delete require admin permission. Get supports both single-object `doit` and dump iteration. Strict validation is disabled for compatibility with the generated YNL policy flags used here.

## State And Persistence
This file owns no runtime state beyond read-only policy and operation tables. The tables persist for the module lifetime and are referenced by the `fou_nl_family` in `fou_core.c`.

## Dependencies And Integration Points
It depends on `<uapi/linux/fou.h>`, netlink/genetlink kernel APIs, and declarations from `fou_nl.h`. It is generated from `Documentation/netlink/specs/fou.yaml`, so manual edits should be avoided.

## Risks
The main risk is drift from the YAML spec or from the handlers in `fou_core.c`. A wrong attribute type can allow invalid configuration or reject valid user space requests. Operation count and command ordering must remain aligned with `fou_nl_family`.

## Test Signals
Validate YNL regeneration diffs, generic netlink family introspection, add/delete permission enforcement, malformed attribute rejection, IPv6 exact-length enforcement, and GET dump behavior against `fou_core.c` parser expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/fou_nl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/fou_nl.h -->
# sources/distributed-fs/ceph-client/net/ipv4/fou_nl.h

## Purpose
`fou_nl.h` is the generated kernel header for FOU generic-netlink glue. It shares policy/operation declarations and handler prototypes between generated netlink code and the FOU core implementation.

## Important APIs, Types, And Functions
The header declares `extern const struct nla_policy fou_nl_policy[FOU_ATTR_IFINDEX + 1]`, `extern const struct genl_small_ops fou_nl_ops[3]`, and the four handlers implemented in `fou_core.c`: `fou_nl_add_doit`, `fou_nl_del_doit`, `fou_nl_get_doit`, and `fou_nl_get_dumpit`.

## Control Flow
There is no executable control flow. Inclusion by `fou_nl.c` and `fou_core.c` allows the generated ops table to reference handlers while the core family registration references generated policy and ops.

## State And Persistence
The header owns no state. It contributes compile-time declarations only.

## Dependencies And Integration Points
It includes netlink/genetlink headers and UAPI `linux/fou.h`. Its generated-source comment ties it to `Documentation/netlink/specs/fou.yaml` and `tools/net/ynl/ynl-regen.sh`.

## Risks
Prototype drift between generated header and core handlers will break builds. Array size drift for ops or policy would desynchronize family registration. Since the file is generated, local manual patches are likely to be overwritten.

## Test Signals
Build coverage is the primary signal. Also verify YNL regeneration, module load, family registration, and that generated declarations match `fou_core.c` symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/fou_nl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/gre_demux.c -->
# sources/distributed-fs/ceph-client/net/ipv4/gre_demux.c

## Purpose
`gre_demux.c` registers IPv4 GRE as an inet protocol and demultiplexes GRE packets to version-specific GRE protocol handlers. It also exports the common GRE header parser used by tunnel implementations.

## Important APIs, Types, And Functions
`gre_proto[GREPROTO_MAX]` stores RCU-protected version handlers. Exported APIs are `gre_add_protocol`, `gre_del_protocol`, and `gre_parse_header`. Runtime callbacks are `gre_rcv` and `gre_err`, installed through `net_gre_protocol` with `inet_add_protocol(IPPROTO_GRE)`.

## Control Flow
Modules register a `struct gre_protocol` for a GRE version with `gre_add_protocol`; cmpxchg prevents duplicate registration. Removal uses cmpxchg and then `synchronize_rcu` before returning. Receive checks that enough packet data exists, extracts the low 7 bits of the GRE version byte, looks up the handler under RCU, and either delegates or drops while updating no-handler/drop stats. Error handling similarly extracts the GRE version from the embedded packet and invokes the registered `err_handler`.

`gre_parse_header` validates base header presence, rejects unsupported version/routing flags, converts GRE flags to tunnel flags, calculates full header length, validates checksum when present, extracts optional key and sequence fields, handles WCCP protocol quirks, stores final header length, and for ERSPAN derives the session id into `tpi->key`.

## State And Persistence
The only persistent state is the global RCU handler array. It is module-wide rather than per-netns. Registration lasts until the owning GRE tunnel module removes its protocol.

## Dependencies And Integration Points
The file integrates with inet protocol dispatch, GRE tunnel modules, ERSPAN helpers, skb checksum helpers, route/ICMP error handling, netdevice stats, and module init/exit. It exports parser functionality to other GRE users.

## Risks
Header parsing is sensitive to short packets and option length calculations. A handler registration race could send packets to the wrong module if RCU synchronization were missing. WCCP and ERSPAN special cases can alter protocol/key interpretation and need compatibility coverage. Error path version extraction assumes enough embedded header data for the calling context.

## Test Signals
Exercise GRE version registration conflicts, deregistration under traffic, receive with no handler, malformed short headers, checksum pass/fail, GRE key/sequence parsing, WCCP v1/v2 adjustment, ERSPAN key derivation, and ICMP error callback routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/gre_demux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/gre_offload.c -->
# sources/distributed-fs/ceph-client/net/ipv4/gre_offload.c

## Purpose
`gre_offload.c` provides GRE GSO and GRO support for IPv4 and, when enabled, IPv6 offload tables. It lets encapsulated GRE traffic be segmented and coalesced while preserving GRE checksum, key, and inner protocol semantics.

## Important APIs, Types, And Functions
The main callbacks are `gre_gso_segment`, `gre_gro_receive`, and `gre_gro_complete`, grouped in `gre_offload`. `gre_offload_init` registers the callbacks with `inet_add_offload(IPPROTO_GRE)` and optionally `inet6_add_offload`.

## Control Flow
GSO validates that the skb is encapsulated and has at least a GRE header, pulls outer tunnel headers, converts skb context to the inner packet, filters hardware features, segments the inner packet with `skb_mac_gso_segment`, then pushes outer headers back onto each segment. If GRE checksum is required it computes or sets up hardware checksum offload, including special adjustment for GSO partial.

GRO rejects already marked encapsulation, reads the GRE header from GRO offsets, supports only version 0 with key and checksum flags, rejects GRE checksum under FOU/GUE because the GRE header location is not trackable there, finds the inner protocol GRO handler, validates header length, optionally validates checksum, compares flags/protocol/key against existing packets in the GRO list, pulls GRE bytes, updates checksum state, and delegates to the inner GRO callback.

GRO completion marks encapsulation, sets `SKB_GSO_GRE`, derives GRE header length from key/checksum flags, delegates completion to the inner protocol, and sets the inner MAC header.

## State And Persistence
No per-flow state is owned by this file. Persistent state is the registered `net_offload` callback table. Per-packet state is carried in skb headers, `skb_shinfo`, and `NAPI_GRO_CB`.

## Dependencies And Integration Points
It depends on skb GSO/GRO helpers, GRE header definitions, inet/inet6 offload registration, device hardware feature flags, IPsec dst state, FOU/GUE GRO markers, and inner protocol offload callbacks found by ethertype.

## Risks
Risks include corrupting skb header offsets during GSO unwind, incorrect GRE checksum handling with partial GSO, over-aggregation packets with different GRE keys or flags, and unsupported sequence/routing flags. FOU/GUE interaction is intentionally conservative for GRE checksum.

## Test Signals
Test GRE GSO with and without GRE checksum, hardware checksum offload, GSO partial, IPsec destinations, GRO aggregation with matching and mismatching keys, unsupported sequence flag rejection, FOU/GUE-encapsulated GRE checksum rejection, IPv6 registration failure unwind, and packet header offsets after segmentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/gre_offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/icmp.c -->
# sources/distributed-fs/ceph-client/net/ipv4/icmp.c

## Purpose
`icmp.c` implements IPv4 ICMP send, receive, error delivery, echo/timestamp replies, rate limiting, RFC 4884/5837 extensions, ping socket delivery, NAT-aware error sends, and per-net ICMP sysctl defaults.

## Important APIs, Types, And Functions
`struct icmp_bxm` carries reply build state. `icmp_err_convert` maps destination-unreachable codes to socket errno/fatal behavior. `struct icmp_control` and `icmp_pointers` dispatch received ICMP types.

Important exported or externally used functions include `__icmp_send`, `icmp_ndo_send`, `icmp_rcv`, `icmp_err`, `icmp_out_count`, `icmp_global_allow`, `icmp_global_consume`, `icmp_build_probe`, `ip_icmp_error_rfc4884`, and `icmp_init`. Internal helpers include `icmp_xmit_lock`, `icmpv4_global_allow`, `icmpv4_xrlim_allow`, `icmp_route_lookup`, `icmp_ext_append`, `icmp_socket_deliver`, `icmp_unreach`, `icmp_redirect`, `icmp_echo`, and `icmp_timestamp`.

## Control Flow
Outgoing errors through `__icmp_send` validate route/device context, reject replies to non-host, broadcast/multicast, non-initial fragments, and ICMP errors about ICMP errors, then apply global and peer rate limits. It selects source address, echoes IP options, builds route lookup state, runs XFRM-aware route lookup, caps payload to the RFC 576-byte limit, optionally appends ICMP extensions, and emits the packet through a per-CPU raw ICMP control socket. Echo and timestamp replies use `icmp_reply`, which performs similar routing and rate limiting for replies.

Incoming `icmp_rcv` first performs XFRM policy checks, validates checksum, pulls the ICMP header, updates SNMP counters, handles extended echo separately, enforces broadcast/multicast rules, delivers echo replies to ping sockets, discards unknown types, and dispatches known types through `icmp_pointers`. Destination unreachable, time exceeded, source quench, and parameter problem messages are handled by `icmp_unreach`, which validates embedded IP header, handles PMTU update policy, rejects bogus broadcast errors, and delivers the error to raw sockets and protocol error handlers. Redirects are delivered through `icmp_socket_deliver`; echo and timestamp requests build replies.

RFC 4884 parsing reports extension offsets and invalid checksums to sockets. RFC 5837 interface information objects can be appended to generated errors when enabled by sysctl. Extended echo probe support resolves devices by name, index, IPv4, or IPv6 address and returns interface status bits.

## State And Persistence
The file owns one per-CPU raw ICMP socket in `ipv4_icmp_sk`, initialized once for init net and temporarily rebound to the target net namespace while sending. Per-net ICMP sysctls, token bucket stamp/credit, and peer rate limiting state govern emission. No packet state persists beyond skb lifetime except socket error delivery and PMTU/redirect updates in routing subsystems.

## Dependencies And Integration Points
It integrates with IPv4 routing, XFRM, netfilter/NAT conntrack, raw sockets, ping sockets, protocol `err_handler`s in `inet_protos`, PMTU and redirect handlers, SNMP MIB counters, tracepoints, L3 master devices, IP options, security flow classification, netdevice lookup, IPv6 helpers for extended echo address queries, and per-net sysctl storage.

## Risks
ICMP has many RFC and security guardrails. Risks include replying when forbidden, rate-limit bypass or over-throttling, route lookup with stale or local routes, nested ICMP error loops, insufficient embedded-header validation before protocol delivery, checksum/extension length errors, and per-CPU socket locking recursion during link failures. Extended echo has device reference and input validation risks.

## Test Signals
Signals include ICMP send suppression for multicast, broadcast, fragments, and ICMP-error loops; PMTU behavior for all `ip_no_pmtu_disc` modes; global and peer rate-limit counters; echo ignore sysctls; broadcast ping rules; timestamp replies; ping socket delivery; raw/protocol error delivery to TCP/UDP; NAT-adjusted `icmp_ndo_send`; RFC 4884 extension validation; RFC 5837 interface extension emission; XFRM policy handling; and per-net sysctl default checks at namespace creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/icmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/igmp.c -->
# sources/distributed-fs/ceph-client/net/ipv4/igmp.c

## Purpose
`igmp.c` implements IPv4 Internet Group Management Protocol and socket multicast membership management. It handles IGMPv1/v2/v3 query/report processing, multicast group join/leave APIs, source filters for SSM/MSF, device multicast filters, netlink multicast-address notifications, procfs reporting, and netdevice rejoin events.

## Important APIs, Types, And Functions
Primary state types are `struct ip_mc_list` for per-interface multicast group membership, `struct ip_sf_list` for per-interface source filters, and `struct ip_mc_socklist` plus `struct ip_sf_socklist` for per-socket memberships and filters. The helper declaration for `inet_fill_ifmcaddr` lives in `igmp_internal.h`.

External functions include `igmp_rcv`, `ip_mc_check_igmp`, `__ip_mc_inc_group`, `ip_mc_inc_group`, `__ip_mc_dec_group`, `ip_mc_join_group`, `ip_mc_join_group_ssm`, `ip_mc_leave_group`, `ip_mc_source`, `ip_mc_msfilter`, `ip_mc_msfget`, `ip_mc_gsfget`, `ip_mc_sf_allow`, `ip_mc_drop_socket`, `ip_check_mc_rcu`, `ip_mc_init_dev`, `ip_mc_up`, `ip_mc_down`, `ip_mc_destroy_dev`, `ip_mc_unmap`, `ip_mc_remap`, `inet_fill_ifmcaddr`, and `igmp_mc_init`.

Internal report machinery includes `igmpv3_newpack`, `add_grec`, `igmpv3_send_report`, `igmpv3_send_cr`, `igmp_send_report`, `igmp_heard_query`, `igmp_heard_report`, timers for group query/interface change/group reports, and deleted-record handling through `igmpv3_add_delrec`, `igmpv3_del_delrec`, and `igmpv3_clear_delrec`.

## Control Flow
Incoming IGMP packets enter `igmp_rcv`, which resolves L3 master devices, validates an `in_device`, verifies header pull and checksum, then dispatches by IGMP type. Queries call `igmp_heard_query`: v1/v2 queries update seen timers and clear v3 change state, while v3 queries parse QRV/QQIC/source lists, start general-query timers, or mark group/source-specific query state before scheduling report timers. Reports from other hosts call `igmp_heard_report` to suppress local pending reports for the group. PIM v1 can be delegated when configured.

Group join through `ip_mc_join_group` or `ip_mc_join_group_ssm` selects an interface, checks duplicate socket membership and membership limits, links a socket membership, increments or creates the interface group, updates device multicast filters, emits rtnetlink multicast-address notifications, and starts the appropriate unsolicited report/change-report path. Leave removes socket source filters, decrements interface users, sends leave or v3 change records when applicable, removes filters, notifies rtnetlink, and frees objects through RCU.

IGMPv3 reporting builds one or more packets with router-alert IP option, TTL 1, control priority, and group records selected by current filter mode, source change state, deleted group records, and query response state. Change-report timers repeat according to QRV. For v1/v2, `igmp_send_report` emits fixed IGMP report or leave messages.

Source filter APIs update both socket-side and interface-side counts. `ip_mc_source` adds/removes individual source entries. `ip_mc_msfilter` replaces a full filter list. `ip_mc_sf_allow` and `ip_check_mc_rcu` enforce receive-side source-filter delivery decisions.

## State And Persistence
State is per network namespace, per device, and per socket. `in_device` owns `mc_list`, optional `mc_hash`, tomb records, query version timers, QRV/QI/QRI values, and timers. Sockets own `inet->mc_list`. Memberships and source filters persist until explicit leave, socket close, device down/destroy, or namespace teardown. RCU protects readers; RTNL protects membership mutation; per-group spinlocks protect source and timer fields.

## Dependencies And Integration Points
The file depends on IPv4 device configuration sysctls, routing for IGMP packet output, ARP multicast address mapping, netdevice multicast filter APIs, rtnetlink notifications, procfs, netdevice notifier events, multicast routing/PIM when enabled, checksum helpers, socket memory accounting, and namespace pernet ops. It creates proc entries `igmp` and `mcfilter` and an autojoin control socket when procfs is enabled.

## Risks
The hardest risks are timer/reference lifetime, RCU plus RTNL list mutation, source-filter count consistency, and IGMPv3 deleted-record handling. Incorrect query parsing can cause missed or excessive reports. Join/leave edge cases can leak socket memory accounting or leave device multicast filters installed. Procfs source-filter iteration holds group spinlocks while walking and must release them on all paths.

## Test Signals
Test ASM and SSM joins/leaves, duplicate joins, membership and source-filter limits, INCLUDE/EXCLUDE mode transitions, v1/v2 querier fallback, v3 general/group/source-specific queries, report suppression by heard reports, device down/up/remap/destroy, socket close cleanup, rtnetlink `RTM_NEW/DELMULTICAST`, `/proc/net/igmp` and `/proc/net/mcfilter`, checksum and packet validation via `ip_mc_check_igmp`, and receive filtering through `ip_mc_sf_allow` and `ip_check_mc_rcu`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/igmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/igmp_internal.h -->
# sources/distributed-fs/ceph-client/net/ipv4/igmp_internal.h

## Purpose
`igmp_internal.h` provides the small internal interface needed to fill IPv4 multicast-address rtnetlink messages from IGMP membership state.

## Important APIs, Types, And Functions
`struct inet_fill_args` carries netlink port id, sequence number, event type, netlink flags, namespace id, and interface index for address message generation. `inet_fill_ifmcaddr` is declared for filling a multicast address message for a given `net_device` and `ip_mc_list`.

## Control Flow
The header has no executable logic. `igmp.c` implements `inet_fill_ifmcaddr`, using this argument bundle when constructing `RTM_NEWMULTICAST` or `RTM_DELMULTICAST` notifications.

## State And Persistence
No state is owned by the header. It defines a call contract for stack or caller-owned arguments.

## Dependencies And Integration Points
It depends on forward-declared kernel networking types from includers: `struct sk_buff`, `struct net_device`, and `struct ip_mc_list`. Its integration point is rtnetlink multicast address notification generation in `igmp.c`.

## Risks
Risk is low and mostly contractual. Field changes must stay synchronized with `inet_fill_ifmcaddr` callers and any future users. Missing include context can break compilation because this header does not include all type declarations itself.

## Test Signals
Build coverage and multicast address notification tests are sufficient. Validate that `inet_fill_ifmcaddr` messages include expected event, flags, interface index, multicast address, and cacheinfo fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/igmp_internal.h -->
