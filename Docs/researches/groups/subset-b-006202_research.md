# subset-b-006202 research

## sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_nat_pptp.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_nat_pptp.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_nat_pptp.c

## Purpose
This module is the IPv4 NAT side of the PPTP conntrack helper. PPTP uses a TCP control channel plus GRE data flows whose call IDs must be translated consistently when the control session is NATed. The file installs an `nf_nat_pptp_hook` callback table so the conntrack PPTP helper can ask NAT code to mangle control messages, rewrite GRE expectations, and NAT expected GRE connections.

## Important APIs, types, and functions
Key integration types are `struct nf_nat_pptp_hook`, `struct nf_conntrack_expect`, `struct nf_ct_pptp_master`, and `struct nf_nat_pptp` stored under the NAT extension. `pptp_outbound_pkt()` handles PNS-to-PAC control messages and rewrites call IDs with `nf_nat_mangle_tcp_packet()`. `pptp_inbound_pkt()` handles PAC-to-PNS peer call ID fields. `pptp_exp_gre()` adjusts original and reply GRE expectations. `pptp_nat_expected()` applies NAT setup to GRE child connections created from expectations. Module init/fini publish and clear `nf_nat_pptp_hook` using RCU.

## Control flow
When the PPTP helper parses a TCP control packet, it calls the outbound or inbound hook according to direction. Outbound `PPTP_OUT_CALL_REQUEST` stores the original PNS call ID, derives the NATed call ID from the reply tuple destination TCP port, updates conntrack PPTP state, and rewrites the control payload. Other outbound messages either rewrite their call ID fields or pass unchanged. Inbound messages rewrite peer call ID fields back to the saved NAT-side PNS call ID when applicable. When GRE expectations are created, `pptp_exp_gre()` patches GRE keys and directions for both traffic directions. When an expected GRE connection materializes, `pptp_nat_expected()` removes the opposite stale expectation if present, then applies source and destination NAT ranges based on the master control connection tuple and saved GRE key.

## State and persistence
State is per-connection, not persistent. The module stores original and translated PNS/PAC call IDs in conntrack helper/NAT extension data. GRE expectations live in conntrack expectation tables and are removed with the master connection or explicitly by `nf_ct_unexpect_related()`. The global hook pointer is RCU-protected for module lifetime.

## Dependencies and integration points
The file depends on conntrack helper data, GRE conntrack tuple fields, NAT helper mangle support, expectation lookup, conntrack zones, and `nf_nat_setup_info()`. It integrates with the separate PPTP conntrack parser through `nf_nat_pptp_hook`, and with module autoloading via `MODULE_ALIAS_NF_NAT_HELPER("pptp")`.

## Risks
The code documents a protocol limitation: it uses the TCP source port as a translated call ID instead of reserving a unique GRE tuple, so multiple calls inside one control session can break. Payload mangling can fail if the TCP skb cannot be rewritten, causing drops. Correctness is sensitive to direction, saved protocol fields, and conntrack helper state being initialized; missing NAT extension is treated as a warning and drop/return. RCU hook replacement must synchronize on unload to avoid use-after-free.

## Test signals
Useful signals include PPTP control sessions through NAT, GRE expectation creation in both directions, simultaneous or repeated calls within one control connection, packet mangling failure paths, and module load/unload races. Kernel selftests or packetdrill-style tests should verify rewritten call IDs in control payloads and resulting GRE tuples under SNAT, DNAT, and bridged/NAT topologies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_nat_pptp.c -->

## sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_nat_snmp_basic_main.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_nat_snmp_basic_main.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_nat_snmp_basic_main.c

## Purpose
This file implements the basic SNMP NAT application-layer gateway. It scans SNMPv1/SNMPv2 UDP payloads at ASN.1/BER level and rewrites embedded IPv4 address values so SNMP management traffic remains coherent across static NAT boundaries. It is intentionally MIB-agnostic and handles tagged four-byte IP address objects rather than semantic SNMP objects.

## Important APIs, types, and functions
`struct snmp_ctx` carries the payload base, UDP checksum pointer, old address, and new address for ASN.1 callbacks. `snmp_version()` validates supported SNMP versions. `snmp_helper()` is called by the generated ASN.1 decoder when an IP address value is found. `fast_csum()` adjusts a nonzero UDP checksum incrementally after rewriting an address. `snmp_translate()` computes direction-dependent old/new addresses from conntrack tuples and invokes `asn1_ber_decoder()`. `help()` is the conntrack helper callback and exported NAT hook target. `snmp_trap_helper` registers a conntrack helper for UDP SNMP traps.

## Control flow
`help()` receives candidate UDP packets from conntrack. It only mangles SNMP replies and originating traps in the expected directions, exits early when the conntrack entry is not NATed, verifies the UDP length matches the skb length, makes the whole skb writable, then serializes parser/mangle work under `snmp_lock`. `snmp_translate()` selects the address mapping from the original or reply tuple, skips no-op mappings, and asks the generated BER decoder to traverse the payload. When `snmp_helper()` sees a four-byte value equal to `ctx.from`, it fixes the UDP checksum if present and writes `ctx.to`.

## State and persistence
The module keeps no persistent per-flow state beyond conntrack NAT state. `snmp_lock` is global serialization around BER parsing and payload mutation. The conntrack helper policy has `max_expected = 0`; this ALG does not create expectations. The global `nf_nat_snmp_hook` pointer is RCU-published at module init and cleared on exit.

## Dependencies and integration points
Dependencies include IPv4/UDP headers, NAT and conntrack helper APIs, the generated `nf_nat_snmp_basic.asn1.h` decoder, checksum helpers, and module aliases for `ip_nat_snmp_basic` and `snmp_trap`. It integrates with the conntrack helper registry through `nf_conntrack_helper_register()` and with NAT helper users through `nf_nat_snmp_hook`.

## Risks
The parser drops packets on malformed or unsupported BER payloads, which is conservative but can affect unusual SNMP encodings. Only SNMPv1/v2 are accepted. Whole-skb writability is required before decode. Checksum delta handling depends on payload offset parity. Because the decoder scans generic tagged IP address values, it may rewrite any matching address field, not only MIB fields known to require translation.

## Test signals
Tests should cover SNMP replies from port 161, traps to port 162, NATed and non-NATed flows, bad UDP length, unsupported SNMP version, malformed BER, zero checksum, nonzero checksum at odd/even offsets, and unchanged payloads when embedded addresses do not match conntrack tuple addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_nat_snmp_basic_main.c -->

## sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_reject_ipv4.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_reject_ipv4.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_reject_ipv4.c

## Purpose
This file is the IPv4 reject core used by netfilter front ends to synthesize TCP resets and ICMP destination-unreachable errors. It offers both skb-building helpers that return a reply skb and send helpers that route and transmit the rejection directly.

## Important APIs, types, and functions
Exported APIs are `nf_reject_skb_v4_tcp_reset()`, `nf_reject_skb_v4_unreach()`, `nf_send_reset()`, and `nf_send_unreach()`. Internal helpers validate IPv4 headers (`nf_reject_iphdr_validate()`), reject ICMP-unreach loops (`nf_skb_is_icmp_unreach()`), extract valid TCP headers (`nf_reject_ip_tcphdr_get()`), build IPv4 headers (`nf_reject_iphdr_put()`), build TCP reset headers (`nf_reject_ip_tcphdr_put()`), and populate missing dst entries (`nf_reject_fill_skb_dst()`).

## Control flow
TCP reset generation validates the incoming IPv4 header, rejects fragments/non-TCP/RST/checksum-failed packets, allocates an skb, reverses addresses and ports, computes sequence/acknowledgment fields according to TCP reset rules, and marks the checksum as partial. ICMP unreachable generation validates the IP header, rejects non-first fragments and ICMP-unreach-to-ICMP-unreach replies, trims/pulls the original packet, verifies checksum where needed, then embeds as much original data as fits under the RFC 576-byte ceiling. The direct send path additionally obtains a route, blocks broadcast/multicast resets, attaches conntrack, marks the original flow closing, handles bridge-netfilter direct Ethernet transmission, or calls `ip_local_out()`.

## State and persistence
There is no durable state. The file mutates skb metadata, may attach conntrack state to generated replies, and may set the original conntrack entry closing through `nf_ct_set_closing()`. It uses the network namespace default IPv4 TTL and route/dst metadata available on the input skb.

## Dependencies and integration points
The module depends on IPv4 routing, TCP/IP checksum helpers, ICMP, dst and route APIs, netfilter reject checksum utilities, conntrack attachment, and optional bridge netfilter. It is consumed by nftables/xtables reject expressions and exported with GPL symbols.

## Risks
Reject generation is safety-sensitive: replying to fragments, invalid checksums, broadcast/multicast destinations, or ICMP errors can create protocol violations or amplification. The bridge fast path must construct Ethernet headers correctly to avoid confusing adjacent routers. `nf_reject_fill_skb_dst()` mutates the input skb by setting dst when absent. Packet-size and MTU assumptions are defensive but should remain aligned with routing behavior.

## Test signals
Cover TCP SYN and established packet resets, no reset for RST or invalid checksum, ICMP unreachable embedding length, no ICMP-unreach response to ICMP unreachable, fragment rejection behavior, route-missing cases, broadcast/multicast suppression, bridge-netfilter behavior, and nft/iptables reject rules at different hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_reject_ipv4.c -->

## sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_socket_ipv4.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_socket_ipv4.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_socket_ipv4.c

## Purpose
This module provides slow-path IPv4 socket lookup for netfilter socket matching and transparent proxy users. Given an skb and input device, it extracts the relevant 5-tuple, handles quoted ICMP errors, optionally reverses SNAT for established replies, and returns a matching TCP or UDP socket.

## Important APIs, types, and functions
The exported entry point is `nf_sk_lookup_slow_v4()`. `extract_icmp4_fields()` parses ICMP error payloads to recover the inner TCP/UDP tuple. `nf_socket_get_sock_v4()` dispatches lookups to `inet_lookup()` for TCP or `udp4_lib_lookup()` for UDP. With conntrack enabled, it uses `nf_ct_get()`, `IP_CT_ESTABLISHED_REPLY`, `IP_CT_RELATED_REPLY`, and `IPS_SRC_NAT_DONE`.

## Control flow
The lookup rejects non-initial fragments. For TCP/UDP packets it reads the transport header, records source/destination addresses and ports, and computes data offset for TCP. For ICMP packets it only accepts ICMP error messages that quote an inner TCP or UDP header, then treats the quoted packet as the tuple to look up. If conntrack says the packet is a reply from an SNATed connection, it rewrites the local destination address/port to the original pre-SNAT source. Finally it calls the protocol-specific socket lookup with the input device index.

## State and persistence
The file owns no persistent state. It borrows skb, conntrack, and namespace state, returning sockets with the reference semantics of the underlying lookup helpers.

## Dependencies and integration points
It integrates with netfilter socket infrastructure (`<net/netfilter/nf_socket.h>`), TCP/UDP/ICMP parsing, inet socket lookup tables, and optionally conntrack. Consumers include xt_socket, nft socket expressions, and TPROXY-related rules that need to decide whether traffic belongs to a local socket.

## Risks
The tuple extraction path is fragile around truncated headers and ICMP quote lengths, but uses `skb_header_pointer()` to avoid unsafe direct access. Conntrack NAT reversal currently handles SNAT reply cases; other NAT states must be validated by consumers. Returning wildcard-bound sockets is left to higher-level filters, so callers must apply their own policy.

## Test signals
Exercise direct TCP/UDP lookup, fragmented packets, ICMP errors with valid and truncated inner headers, SNATed established replies, related ICMP replies, no-conntrack builds, device-bound sockets, wildcard sockets, and namespace isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_socket_ipv4.c -->

## sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_tproxy_ipv4.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_tproxy_ipv4.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_tproxy_ipv4.c

## Purpose
This file provides IPv4 transparent proxy socket helpers. It locates listener or established sockets for redirected TCP/UDP traffic, chooses a local address when the rule did not specify one, and handles TCP TIME_WAIT sockets so new SYNs can be redirected to listeners.

## Important APIs, types, and functions
Exported symbols are `nf_tproxy_handle_time_wait4()`, `nf_tproxy_laddr4()`, and `nf_tproxy_get_sock_v4()`. It uses `inet_lookup_listener()`, `inet_lookup_established()`, `udp4_lib_lookup()`, `inet_twsk_put()`, and `nf_tproxy_twsk_deschedule_put()`. `enum nf_tproxy_lookup_t` selects listener versus established lookup mode.

## Control flow
For TIME_WAIT TCP sockets, `nf_tproxy_handle_time_wait4()` parses the TCP header. If the packet is a pure SYN, it looks for a listener at the requested local address/port or original destination and replaces the TIME_WAIT socket with that listener, descheduling the time-wait entry. `nf_tproxy_laddr4()` returns the user-specified local address or the first primary IPv4 address on the ingress device, falling back to the original destination. `nf_tproxy_get_sock_v4()` performs TCP listener/established or UDP lookup and filters UDP results according to requested mode, connected state, and wildcard binding.

## State and persistence
The module has no persistent state. It manipulates socket references returned by lookup functions and may deschedule a TIME_WAIT socket. Address selection reads RCU-protected in-device address lists.

## Dependencies and integration points
It integrates with netfilter TPROXY, IPv4 device address management, TCP/UDP socket tables, and TIME_WAIT handling. It is used by transparent proxy rule implementations that need a local socket while preserving the original destination semantics.

## Risks
Reference handling is central: listener lookup requires `refcount_inc_not_zero()`, UDP rejected sockets must be `sock_put()`, and TIME_WAIT sockets must be released/descheduled exactly once. Wildcard listener behavior intentionally differs by consumer and must be filtered by callers that do not want `0.0.0.0` matches. Header truncation must return NULL without leaking the TIME_WAIT reference.

## Test signals
Test TCP established lookup, listener lookup with wildcard and specific binds, SYN to TIME_WAIT redirection, malformed TCP headers, UDP connected versus wildcard sockets, device-bound lookup, user-specified local address, and ingress-device primary-address fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_tproxy_ipv4.c -->

## sources/distributed-fs/ceph-client/net/ipv4/netfilter/nft_dup_ipv4.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nft_dup_ipv4.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nft_dup_ipv4.c

## Purpose
This file implements the IPv4 nftables `dup` expression. The expression duplicates a packet to a configured IPv4 gateway and optional output interface while normal packet evaluation continues.

## Important APIs, types, and functions
`struct nft_dup_ipv4` stores source register numbers for the gateway address and optional device index. `nft_dup_ipv4_init()` validates and records register loads using `nft_parse_register_load()`. `nft_dup_ipv4_eval()` reads the gateway and output interface from nft registers and calls `nf_dup_ipv4()`. `nft_dup_ipv4_dump()` serializes register configuration. Module init/fini register `nft_dup_ipv4_type`.

## Control flow
At rule installation, nftables requires `NFTA_DUP_SREG_ADDR` and optionally accepts `NFTA_DUP_SREG_DEV`. At evaluation time, the expression reads `regs->data` at the stored register offsets, builds an `in_addr`, chooses `-1` for unspecified oif, and invokes the IPv4 duplication helper with the current net namespace, skb, and hook.

## State and persistence
Expression state is per-rule private data containing only register selectors. There is no runtime mutable state in the module. Duplicated packet routing and allocation are delegated to `nf_dup_ipv4()`.

## Dependencies and integration points
The file depends on nf_tables expression APIs, netlink attribute policy handling, register load/dump helpers, and IPv4 duplicate packet support in `nf_dup_ipv4`. It registers under family `NFPROTO_IPV4` with name `dup`.

## Risks
Incorrect register size validation could cause bad gateway or oif reads, but init requests `sizeof(struct in_addr)` and `sizeof(int)`. Runtime failure behavior is delegated to `nf_dup_ipv4()` and does not affect the expression verdict. Tests should ensure optional device register zero is treated as unset.

## Test signals
Install nft rules with and without `sreg_dev`, dump rules and compare register attributes, duplicate packets at multiple hooks, invalid missing gateway attribute, invalid register size, and route failures in the duplication helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nft_dup_ipv4.c -->

## sources/distributed-fs/ceph-client/net/ipv4/netfilter/nft_fib_ipv4.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nft_fib_ipv4.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nft_fib_ipv4.c

## Purpose
This file implements IPv4 nftables `fib` expression evaluation. It can return route output interface, output interface name, or address type for source/destination address lookups, honoring nft flags such as input/output interface and packet mark.

## Important APIs, types, and functions
Exported evaluators are `nft_fib4_eval_type()` for address type results and `nft_fib4_eval()` for route lookup results. `get_saddr()` suppresses multicast, limited broadcast, and zeronet source addresses for FIB queries. `nft_fib4_select_ops()` chooses operation tables based on `NFTA_FIB_RESULT`. The module reuses generic `nft_fib_init()`, `nft_fib_dump()`, `nft_fib_validate()`, `nft_fib_store_result()`, and `nft_fib_can_skip()` helpers.

## Control flow
The type evaluator reads the IPv4 header safely with `skb_header_pointer()`, selects source or destination address according to flags, and queries either interface-specific or device-table address type. The route evaluator initializes a `flowi4`, handles shortcut cases, selects the relevant oif/iif constraint, accounts for l3mdev, reads the IPv4 header, handles zeronet broadcast/multicast special cases, copies mark and DSCP when requested, chooses daddr/saddr based on direction flags, performs `fib_lookup()`, filters unacceptable results, verifies requested output interface usage, and stores the requested result in nft registers.

## State and persistence
Expression state is the generic `struct nft_fib` private data. Runtime evaluation is stateless and writes only nft registers or `NFT_BREAK` on malformed packet headers.

## Dependencies and integration points
The code depends on IPv4 FIB lookup, route and flow APIs, nft packet metadata, l3mdev handling, inet address-type helpers, and generic nft fib infrastructure. It registers the IPv4 `fib` expression and exports evaluator symbols for related modules.

## Risks
Route lookup semantics are subtle around `OIF`/`IIF`, forward hook source lookups, l3mdev masters, mark/DSCP inclusion, and special source addresses. Header access must break evaluation on truncated skbs. The code intentionally does not set `flowi4_oif` because that would constrain FIB results incorrectly; regressions here can change firewall behavior.

## Test signals
Test nft fib expressions for daddr/saddr, iif/oif, mark-aware routes, VRF/l3mdev setups, local/multicast/broadcast/zeronet traffic, forward hook source lookups, malformed IPv4 headers, `ADDRTYPE` results, and rule dump/restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nft_fib_ipv4.c -->

## sources/distributed-fs/ceph-client/net/ipv4/netfilter/nft_reject_ipv4.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nft_reject_ipv4.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nft_reject_ipv4.c

## Purpose
This module implements the IPv4 nftables `reject` expression. It translates nft reject configuration into IPv4 ICMP unreachable or TCP reset transmission and then drops the original packet.

## Important APIs, types, and functions
`nft_reject_ipv4_eval()` is the evaluator. It reads `struct nft_reject` private data and calls `nf_send_unreach()` for `NFT_REJECT_ICMP_UNREACH` or `nf_send_reset()` for `NFT_REJECT_TCP_RST`. It uses generic reject init/dump/validate helpers and registers `nft_reject_ipv4_type`.

## Control flow
At evaluation time, the expression selects the configured reject type, sends the appropriate IPv4 rejection using the current skb, net namespace, socket, and hook, then sets `regs->verdict.code = NF_DROP`. Unsupported types do not send a reply but still drop because the verdict assignment is unconditional.

## State and persistence
State is per-rule `struct nft_reject` data created by the generic nft reject initializer. The module itself has no mutable runtime state.

## Dependencies and integration points
It depends on nf_tables expression registration, generic nft reject policy/validation, and the IPv4 reject core in `nf_reject_ipv4.c`. It registers as family `NFPROTO_IPV4`, name `reject`.

## Risks
Reply correctness relies on the lower-level IPv4 reject core handling fragments, checksums, routes, bridge paths, and invalid packets. Because the expression always drops, validation must prevent unsupported configurations from being installed. Hook-specific routing behavior should be tested through nftables rather than this file alone.

## Test signals
Install reject rules for ICMP unreachable codes and TCP reset, verify original packets are dropped, verify generated replies at input/forward/output-relevant hooks, test invalid reject attributes, and cover interactions with conntrack and bridge netfilter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netfilter/nft_reject_ipv4.c -->

## sources/distributed-fs/ceph-client/net/ipv4/netlink.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netlink.c -->
# sources/distributed-fs/ceph-client/net/ipv4/netlink.c

## Purpose
This small file validates the optional IP protocol selector for rtnetlink route-get requests. It centralizes accepted protocol values for route lookup parsing.

## Important APIs, types, and functions
The only exported function is `rtm_getroute_parse_ip_proto(struct nlattr *attr, u8 *ip_proto, u8 family, struct netlink_ext_ack *extack)`. It reads a `u8` netlink attribute and accepts TCP, UDP, IPv4 ICMP for `AF_INET`, and ICMPv6 for `AF_INET6` when IPv6 is enabled.

## Control flow
The function stores `nla_get_u8(attr)` in the caller-provided output and switches on the value. Valid protocol/family combinations return zero. Unsupported combinations set an extended ack message `"Unsupported ip proto"` and return `-EOPNOTSUPP`.

## State and persistence
There is no state. The function only writes the output byte and optional extack.

## Dependencies and integration points
It depends on netlink attributes, rtnetlink route get handlers, IPv4/IPv6 protocol constants, and `netlink_ext_ack`. It exports a GPL symbol so route lookup code can reuse validation without duplicating protocol/family checks.

## Risks
The allowlist is intentionally narrow. Adding route-get support for another transport requires updating this validator. Family mismatches are rejected, so callers must pass the effective address family, not merely the netlink message protocol.

## Test signals
Validate TCP/UDP for IPv4 and IPv6 families, ICMP only with IPv4, ICMPv6 only with IPv6-enabled AF_INET6, unsupported values, extack content, and boundary values for the `u8` attribute.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/netlink.c -->

## sources/distributed-fs/ceph-client/net/ipv4/nexthop.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/nexthop.c -->
# sources/distributed-fs/ceph-client/net/ipv4/nexthop.c

## Purpose
This file implements generic nexthop objects for IPv4 and IPv6 routing. It provides netlink CRUD and dump operations, shared nexthop lifetime management, nexthop groups, resilient groups with bucket migration, hardware offload notifications/statistics, FIB compatibility checks, route update notifications, device event cleanup, and per-network-namespace storage.

## Important APIs, types, and functions
Core exported APIs include `nexthop_find_by_id()`, `nexthop_select_path()`, `fib_check_nexthop()`, `fib6_check_nexthop()`, `nexthop_for_each_fib6_nh()`, notifier registration functions, `nexthop_set_hw_flags()`, `nexthop_bucket_set_hw_flags()`, and `nexthop_res_grp_activity_update()`. Major internal structures are `struct nexthop`, `struct nh_info`, `struct nh_group`, `struct nh_grp_entry`, `struct nh_res_table`, and `struct nh_res_bucket`. Netlink handlers include `rtm_new_nexthop()`, `rtm_del_nexthop()`, `rtm_get_nexthop()`, `rtm_dump_nexthop()`, `rtm_get_nexthop_bucket()`, and `rtm_dump_nexthop_bucket()`.

## Control flow
Creation parses netlink attributes into `struct nh_config`, validates group or single-nexthop constraints, performs RTNL-only device validation, allocates a single nexthop or group, initializes IPv4/IPv6 FIB nexthop data, and inserts into the per-net red-black tree. Replacement first validates all existing IPv4/IPv6 routes and parent groups, then swaps group or single internals under RCU, sends notifiers, flushes route caches, and tears down the temporary new object. Deletion sends delete notifiers, removes the rb-tree node, flushes routes linked through `fi_list` and `f6i_list`, removes group memberships, cancels resilient upkeep, deletes device-hash entries, increments the sequence, and drops the object reference.

Path selection dispatches single nexthops directly, hash-threshold groups by weighted upper bounds, FDB groups without neighbor-good filtering, and resilient groups by hash bucket. Hash-threshold selection prefers reachable neighbors and falls back to the first usable entry. Resilient groups maintain bucket-to-nexthop mappings; upkeep migrates buckets from overweight entries to underweight entries when buckets are idle or when forced by the unbalanced timer. Bucket replacement can notify hardware listeners and emit netlink bucket notifications.

Netlink dump uses continuation contexts in `cb->ctx`, walking the rb-tree from the last id rather than restarting linearly. Bucket dump either targets one resilient group or walks all resilient groups and filters by nexthop id, device, master, FDB flag, family, and bucket nexthop id.

## State and persistence
All state is in memory and scoped to `struct net`. `net->nexthop.rb_root` indexes nexthops by id, `devhash` indexes single nexthops by device for device events, `seq` supports dump consistency, and `last_id_allocated` supports automatic ids. Nexthops are RCU-freed via `nexthop_free_rcu()`. Groups keep references to member nexthops and per-cpu packet stats. Resilient tables keep delayed work, bucket state, timers, underweight lists, hardware flags, and activity timestamps. No state persists across net namespace teardown.

## Dependencies and integration points
The file integrates with rtnetlink message registration, netdevice notifier events, IPv4 FIB (`fib_nh_init`, `fib_check_nh`, route cache flush), IPv6 FIB (`fib6_nh_init`, `ip6_del_rt`, `fib6_rt_update`), lwtunnel encapsulation, neighbor reachability, l3mdev/VRF, notifier chains used by hardware offload drivers, and pernet subsystem init/exit. It emits `RTM_NEWNEXTHOP`, `RTM_DELNEXTHOP`, and `RTM_NEWNEXTHOPBUCKET`.

## Risks
The largest risks are concurrency and rollback. The file mixes RTNL, RCU readers, delayed work, per-cpu stats, notifier callbacks, and route lists; replacement failures must restore pointers, parent links, protocol/flag fields, and hardware notifications. Resilient bucket migration allows hardware veto unless forced, so bucket flags may diverge from software expectations. Group validation forbids nested groups, mixed FDB/non-FDB semantics, invalid weights, unsupported blackhole combinations, and IPv4/IPv6 route mismatches; missed validation can corrupt route behavior. Device-down cleanup and netns exit must avoid stale device pointers and delayed work.

## Test signals
Test single IPv4/IPv6 nexthop add/replace/delete/get/dump, auto id allocation, blackhole nexthops, lwt encap validation, FDB nexthops, hash-threshold groups with weights, resilient group bucket creation/migration/timers, dump continuation after partial skb fills, bucket get/dump filters, hardware notifier veto and rollback, hardware stats dumps, route cache invalidation after replacement, route checks for host scope and IPv6 source routes, device down/unregister/MTU change handling, net namespace teardown, and concurrent path selection during replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/nexthop.c -->

## sources/distributed-fs/ceph-client/net/ipv4/ping.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ping.c -->
# sources/distributed-fs/ceph-client/net/ipv4/ping.c

## Purpose
This file implements Linux ping sockets, allowing ICMP echo traffic without raw socket privileges for users in the configured ping group range. It covers socket permission checks, identifier allocation, bind/connect/send/receive paths, ICMP error delivery, IPv4 and partial IPv6 shared support, and `/proc/net/icmp` listing.

## Important APIs, types, and functions
Core globals are `ping_table` and `pingv6_ops`. `ping_get_port()` allocates or binds ICMP identifiers and hashes sockets. `ping_lookup()` finds sockets by namespace, identifier, bound address, family, and device. `ping_init_sock()` enforces `ping_group_range`. `ping_bind()`, `ping_v4_sendmsg()`, `ping_recvmsg()`, `ping_rcv()`, and `ping_err()` implement the main socket behavior. `ping_prot` is the protocol operations table. Proc helpers implement the seq_file view for `/proc/net/icmp`.

## Control flow
Socket initialization checks whether the effective or supplementary group is within the namespace ping group range. Bind validates IPv4/IPv6 addresses, rejects multicast/broadcast bind addresses, may adjust scoped IPv6 device binding, allocates the ICMP identifier, stores local address, and resets destination cache. Send consumes the user-provided ICMP header, accepts only echo and extended echo request types with code zero, applies cmsg/IP options, routes the packet, checks broadcast permission, builds a fake ICMP header using `inet_sport` as echo id, appends payload through `ip_append_data()`, finalizes checksum, and pushes pending frames. Receive dequeues datagrams, copies payload and control messages, and fills source address. Input `ping_rcv()` restores the ICMP header, looks up the identifier, and queues the skb or drops with no-socket reason. Error handling maps ICMP and ICMPv6 errors to socket errors and optional error queue entries.

## State and persistence
State is in per-net `ping_port_rover`, the global ping hash table, socket inet fields, and per-socket receive queues. No disk persistence exists. Hash-table access is spinlock protected for writers and RCU for lookup. Proc initialization randomizes the namespace port rover.

## Dependencies and integration points
The file integrates with ICMP receive/error paths, IPv4 route output, cgroup BPF connect hooks, socket memory accounting, inet datagram connect/disconnect helpers, IP options/cmsg handling, IPv6 operations through `pingv6_ops`, and procfs seq_file infrastructure.

## Risks
Identifier allocation and reuse semantics are security-sensitive because ping sockets rely on ICMP id rather than privileged ports. Permission checks must correctly handle group ranges. Bind may temporarily modify `sk_bound_dev_if` for scoped IPv6 and must restore it on port allocation failure. Send modifies the msghdr iterator by consuming the ICMP header. Error reporting differs depending on `RECVERR` and connected state. Input lookup must respect namespace, bound address, and device to avoid cross-socket delivery.

## Test signals
Cover ping group permission allow/deny, automatic and explicit identifiers, reuse behavior, IPv4 bind to local/nonlocal/broadcast/multicast addresses, cgroup connect hook rejection, echo and extended echo sends, invalid ICMP types/codes, broadcast permission, PMTU/error queue behavior, receive truncation/control messages, no-socket drops, `/proc/net/icmp`, and IPv6 paths when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ping.c -->

## sources/distributed-fs/ceph-client/net/ipv4/proc.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/proc.c -->
# sources/distributed-fs/ceph-client/net/ipv4/proc.c

## Purpose
This file implements IPv4-related procfs statistics files for each network namespace: `/proc/net/sockstat`, `/proc/net/snmp`, and `/proc/net/netstat`. It formats socket usage and SNMP-style protocol counters for user-space monitoring.

## Important APIs, types, and functions
`sockstat_seq_show()` prints socket allocation and memory usage. Static `snmp_mib` arrays map visible counter names to IP, TCP, UDP, ICMP, and Linux extended MIB indexes. `icmpmsg_put()`, `icmp_put()`, `snmp_seq_show_ipstats()`, `snmp_seq_show_tcp_udp()`, `snmp_seq_show()`, and `netstat_seq_show()` format the proc files. `ip_proc_init_net()` and `ip_proc_exit_net()` create/remove proc entries per namespace; `ip_misc_proc_init()` registers the pernet subsystem.

## Control flow
On namespace init, the file creates `sockstat`, `netstat`, and `snmp` entries with rollback on partial failure. Reads invoke seq_file single-show callbacks. SNMP output prints header lines and matching value lines, using batched per-cpu counter collection where possible. ICMP message type counters are printed only for nonzero values, batched in groups of sixteen. Netstat allocates a temporary buffer for batched TCP extended and IP extended counters, falling back to folded per-counter reads on allocation failure, and appends MPTCP statistics.

## State and persistence
The file owns no counters; it reads live per-net MIB structures, protocol memory accounting, socket in-use counters, TCP timewait counts, and fragment table state. Proc entries are per-net namespace and removed at namespace exit.

## Dependencies and integration points
It integrates with procfs, seq_file, pernet operations, TCP/UDP/RAW protocol accounting, ICMP/IP SNMP counters, MPTCP stats, fragment reassembly memory accounting, and namespace-local proc roots.

## Risks
Output format is user ABI for tools like netstat, ss, monitoring agents, and SNMP exporters, so counter names/order are compatibility-sensitive. Counter batching must respect per-cpu synchronization. Partial proc creation rollback must remove only entries already created. Large MIB list changes can break parsers if not coordinated.

## Test signals
Read `/proc/net/sockstat`, `/proc/net/snmp`, and `/proc/net/netstat` in init and non-init namespaces; verify header/value alignment; exercise allocation fallback in `netstat_seq_show()`; generate TCP/UDP/ICMP/IP traffic and confirm counters move; test proc cleanup on netns deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/proc.c -->

## sources/distributed-fs/ceph-client/net/ipv4/protocol.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/protocol.c -->
# sources/distributed-fs/ceph-client/net/ipv4/protocol.c

## Purpose
This file owns the IPv4 protocol and offload dispatch tables. It provides small registration helpers used by transport protocols and offload implementations to install or remove handlers by IP protocol number.

## Important APIs, types, and functions
Global exported arrays are `inet_protos[MAX_INET_PROTOS]` and `inet_offloads[MAX_INET_PROTOS]`. Exported functions are `inet_add_protocol()`, `inet_del_protocol()`, `inet_add_offload()`, and `inet_del_offload()`. Entries are `struct net_protocol` and `struct net_offload` pointers protected by RCU-style publication and removal.

## Control flow
Add functions use `cmpxchg()` to install a handler only if the slot is currently NULL, returning zero on success and `-1` on collision. Delete functions use `cmpxchg()` to clear the slot only if it still points at the caller-provided handler, then call `synchronize_net()` before returning so in-flight network readers complete.

## State and persistence
The dispatch arrays are global kernel state and persist for the lifetime of registered modules. There is no per-namespace state. Handlers are stored as RCU pointers and are expected to remain valid until after deletion synchronization.

## Dependencies and integration points
This file integrates with the IPv4 receive path and protocol modules such as TCP, UDP, ICMP, raw, GRE, and offload/GRO handlers. It depends on atomic compare-exchange and network RCU synchronization.

## Risks
The API returns `-1` rather than a conventional errno, so callers must handle that contract. Incorrect deletion pointer arguments leave stale registrations in place. Missing `synchronize_net()` would cause use-after-free for module unload, so removal ordering is critical.

## Test signals
Exercise duplicate registration failure, deletion with matching and nonmatching pointers, module unload after traffic, offload registration collisions, and receive-path behavior before and after protocol registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/protocol.c -->

## sources/distributed-fs/ceph-client/net/ipv4/raw.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/raw.c -->
# sources/distributed-fs/ceph-client/net/ipv4/raw.c

## Purpose
This file implements IPv4 raw sockets. It provides protocol hash registration, inbound packet fanout, ICMP error reporting, send paths with and without `IP_HDRINCL`, receive, bind, ICMP filter socket option, ioctls, proc listing, and raw socket sysctl initialization.

## Important APIs, types, and functions
Exported state/API includes `raw_v4_hashinfo`, `raw_hash_sk()`, `raw_unhash_sk()`, `raw_v4_match()`, `raw_local_deliver()`, `raw_icmp_error()`, `raw_rcv()`, `raw_abort()`, seq helpers, and `raw_prot`. Major send helpers are `raw_send_hdrinc()`, `raw_probe_proto_opt()`, `raw_getfrag()`, and `raw_sendmsg()`. Receive and control helpers include `icmp_filter()`, `raw_v4_input()`, `raw_err()`, `raw_recvmsg()`, `raw_bind()`, `raw_setsockopt()`, `raw_getsockopt()`, and `raw_ioctl()`.

## Control flow
Inbound delivery hashes by protocol, walks matching raw sockets under RCU, enforces receive-buffer capacity, applies ICMP filter and multicast source-filter checks, clones the skb, and queues it through `raw_rcv()`. `raw_rcv()` performs XFRM policy checks, resets conntrack, adjusts skb data to include the IP header, and queues it. ICMP errors look up matching raw sockets using reversed addresses and convert ICMP types/codes into socket errors and optional error queue entries.

Send validates length and flags, resolves destination from message name or connected state, processes cmsgs/IP options, builds a `flowi4`, probes ICMP type/code for route policy when not `IP_HDRINCL`, routes, checks broadcast permission, and either sends a user-supplied IP header via `raw_send_hdrinc()` or appends payload via `ip_append_data()` and pushes pending frames. `IP_HDRINCL` validates user IP header length, fills missing source/id/checksum fields, and sends through local-out netfilter.

## State and persistence
Raw sockets are stored in `raw_v4_hashinfo` hash buckets and accounted in protocol in-use counters. Per-socket state includes inet addresses, protocol number, IP options, ICMP filter, queues, and pending frames. Proc entries are per-net namespace; `sysctl_raw_l3mdev_accept` is initialized per net when configured. No disk state exists.

## Dependencies and integration points
The file integrates with IPv4 input delivery, ICMP error handling, IP route output, IP options/cmsg, XFRM policy, netfilter local-out hook, multicast source filters, MROUTE ioctls, procfs, inet diag via exported hash/match helpers, and inet protocol operations.

## Risks
Raw sockets expose low-level packet control, so header validation, broadcast permission, checksum behavior, and `IP_HDRINCL` semantics are sensitive user ABI. Inbound fanout clones packets while walking an RCU hash; receive-buffer overflow must account drops without blocking. Send must avoid leaking routes/options on error and maintain compatibility for odd legacy behavior such as protocol from sockaddr port not being used.

## Test signals
Cover raw bind/connect/send/receive, `IP_HDRINCL` with missing source/id and malformed IHL, cmsgs and source-route options, ICMP_FILTER, MSG_ERRQUEUE, broadcast permission, PMTU errors, XFRM policy drops, multicast source filters, proc listing, MROUTE ioctls, and namespace/l3mdev behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/raw.c -->

## sources/distributed-fs/ceph-client/net/ipv4/raw_diag.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/raw_diag.c -->
# sources/distributed-fs/ceph-client/net/ipv4/raw_diag.c

## Purpose
This module adds SOCK_DIAG/INET_DIAG support for raw sockets. It lets users dump, query, inspect queues, and optionally destroy IPv4 and IPv6 raw sockets through netlink diagnostics.

## Important APIs, types, and functions
`raw_get_hashinfo()` selects IPv4 or IPv6 raw hash tables. `raw_lookup()` matches a raw socket using raw protocol and inet diag id fields. `raw_sock_get()` finds and references one socket. `raw_diag_dump_one()` replies to single-socket requests. `raw_diag_dump()` streams all matching raw sockets. `raw_diag_get_info()` fills queue sizes. Optional `raw_diag_destroy()` aborts a socket. `raw_diag_handler` registers with inet_diag.

## Control flow
Single lookup selects the hash table, scans buckets under RCU, applies family/protocol/address/interface matching, and increments the socket refcount before returning. Dumping resumes from `cb->args[0]` bucket and `cb->args[1]` socket index, filters namespace, family, source and destination pseudo-ports, optional bytecode, and calls `inet_sk_diag_fill()` for each match. Init registers the handler for `IPPROTO_RAW`; exit unregisters it.

## State and persistence
The module owns no socket state. It reads raw hash tables exported by `raw.c` and `rawv6`, uses netlink callback args for dump cursors, and holds temporary socket references while building replies.

## Dependencies and integration points
It integrates with `NETLINK_SOCK_DIAG`, inet_diag, raw IPv4/IPv6 socket hash tables, raw match helpers, netlink capability checks, and optional diag destroy support. Build-time checks ensure `inet_diag_req_v2` and `inet_diag_req_raw` layouts remain compatible except for the repurposed pad field.

## Risks
Dump cursor correctness and socket refcounting are key. The ABI compatibility trick that maps `pad` to `sdiag_raw_protocol` is layout-sensitive and guarded by `BUILD_BUG_ON()`. Capability checks control how much socket detail is exposed. Destroy support must not race socket teardown.

## Test signals
Use `ss`/inet_diag to dump IPv4 and IPv6 raw sockets, query one socket by protocol/address/interface, apply bytecode filters, validate queue sizes, test non-admin detail differences, exercise dump continuation with many sockets, and destroy sockets when `CONFIG_INET_DIAG_DESTROY` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/raw_diag.c -->
