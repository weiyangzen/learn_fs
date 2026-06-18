# subset-b-005897 research

Grouped research for Linux netfilter, netfs, netlink, NFS, NUMA, NLS, NMI, and speculation-mitigation headers under `sources/distributed-fs/ceph-client/include/linux`. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_pptp.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_pptp.h

Purpose: Defines the in-kernel PPTP connection-tracking helper contract: PPTP control-session/call states, wire-format control messages, GRE call-id NAT side state, and the RCU-published NAT callback table used by the helper.

Important APIs, types, and functions: Key exports are `pptp_msg_name()`, `struct nf_ct_pptp_master`, `struct nf_nat_pptp`, all `Pptp*` control message structs, `union pptp_ctrl_union`, and `struct nf_nat_pptp_hook` with callbacks for outbound/inbound calls and packet mangling. Detected source surface: 321 lines; includes `linux/netfilter.h`, `linux/netfilter/nf_conntrack_common.h`, `linux/skbuff.h`, `linux/types.h`, `net/netfilter/nf_conntrack_expect.h`, `uapi/linux/netfilter/nf_conntrack_tuple_common.h`; macros `PPTP_ANALOG_TYPE`, `PPTP_ASYNC_FRAMING`, `PPTP_BAD_CALLID`, `PPTP_BAD_FORMAT`, `PPTP_BAD_VALUE`, `PPTP_BEARER_CAP_ANALOG`, `PPTP_BEARER_CAP_DIGITAL`, `PPTP_CALL_CLEAR_REQUEST`, `PPTP_CALL_DISCONNECT_NOTIFY`, `PPTP_CONTROL_PORT`, `PPTP_DIGITAL_TYPE`, `PPTP_DONT_CARE_BEARER_TYPE`, `PPTP_DONT_CARE_FRAMING`, `PPTP_ECHO_GENERAL_ERROR`, `PPTP_ECHO_OK`, `PPTP_ECHO_REPLY`, `PPTP_ECHO_REQUEST`, `PPTP_ERROR_CODE_NONE`, and 42 more; structs `PptpCallDisconnectNotify`, `PptpClearCallRequest`, `PptpControlHeader`, `PptpEchoReply`, `PptpEchoRequest`, `PptpInCallConnected`, `PptpInCallReply`, `PptpInCallRequest`, `PptpOutCallReply`, `PptpOutCallRequest`, `PptpSetLinkInfo`, `PptpStartSessionReply`, `PptpStartSessionRequest`, `PptpStopSessionReply`, `PptpStopSessionRequest`, `PptpWanErrorNotify`, `nf_conn`, `nf_conntrack_expect`, and 5 more; enums `pptp_ctrlcall_state`, `pptp_ctrlsess_state`; typedefs none; function-like declarations/helpers none.

Control flow: Runtime code parses TCP port 1723 control packets, validates the PPTP header and magic cookie, switches on message type, updates master connection state, and installs expectations for GRE data flows. NAT code is optional and reached through the RCU hook table.

State and persistence behavior: The header defines persistent per-connection helper extension state: session/call states, peer/server call IDs, packet sequence fields, and translated call IDs. The wire structs are ABI-shaped and must match network byte order and PPTP message lengths.

Dependencies and integration points: Includes netfilter core, sk_buff, conntrack common state, expectation support, and conntrack tuple direction definitions. It integrates the TCP control helper, GRE conntrack helper, and NAT PPTP module.

Risks and test signals: Risks are malformed control length parsing, call-id confusion between original/reply directions, stale expectations, and RCU misuse around NAT hooks. Test with PPTP control handshakes, GRE data setup, NAT enabled/disabled, call teardown, and fuzzed/truncated control packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_pptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_proto_gre.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_proto_gre.h

Purpose: Declares GRE conntrack state and keymap helpers used to associate PPTP/GRE flows with conntrack tuples.

Important APIs, types, and functions: Important pieces are `struct nf_ct_gre`, `struct nf_ct_gre_keymap`, `nf_ct_gre_keymap_add()`, `nf_ct_gre_keymap_destroy()`, and `gre_pkt_to_tuple()`. Detected source surface: 30 lines; includes `net/netfilter/nf_conntrack_tuple.h`; macros `_CONNTRACK_PROTO_GRE_H`; structs `list_head`, `net`, `nf_conn`, `nf_conntrack_tuple`, `nf_ct_gre`, `nf_ct_gre_keymap`, `rcu_head`; enums none; typedefs none; function-like declarations/helpers `gre_pkt_to_tuple`, `nf_ct_gre_keymap_add`, `nf_ct_gre_keymap_destroy`.

Control flow: GRE packet handling extracts tuple keys from skb data, maps packet keys to conntrack tuple endpoints, and tears keymaps down when the owning connection is destroyed.

State and persistence behavior: Per-connection GRE state stores original/reply keys, while keymap entries are hlist nodes linked into lookup tables. Persistence is limited to conntrack lifetime.

Dependencies and integration points: Depends on conntrack tuple types and generic skb parsing. PPTP conntrack/NAT is the main higher-level integration point.

Risks and test signals: Risks are key collisions, endian mistakes in GRE keys, and missing cleanup on conntrack destruction. Test simultaneous PPTP calls, NAT-rewritten call IDs, and no-key GRE packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_proto_gre.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_sane.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_sane.h

Purpose: Defines the SANE scanner protocol helper state for tracking control/data negotiation on TCP port 6566.

Important APIs, types, and functions: Exports `SANE_PORT`, `enum sane_state`, and `struct nf_ct_sane_master` with state and data port fields. Detected source surface: 18 lines; includes none; macros `SANE_PORT`, `_NF_CONNTRACK_SANE_H`; structs `nf_ct_sane_master`; enums `sane_state`; typedefs none; function-like declarations/helpers none.

Control flow: The helper watches the control stream, transitions through normal and start-request states, and records the negotiated data port for expectation creation.

State and persistence behavior: Per-master conntrack state records a compact protocol phase and port. No global state is defined here.

Dependencies and integration points: Consumed by the SANE conntrack helper and expectation code. It relies on the generic conntrack extension layout outside this header.

Risks and test signals: Risks are incomplete TCP stream parsing and accepting bogus data ports. Test normal scan setup, fragmented control commands, and teardown without a data channel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_sane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_sctp.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_sctp.h

Purpose: Defines SCTP-specific conntrack state storage for SCTP association verification tags.

Important APIs, types, and functions: Exports `struct ip_ct_sctp` and includes the UAPI SCTP conntrack state definitions. Detected source surface: 17 lines; includes `uapi/linux/netfilter/nf_conntrack_sctp.h`; macros `_NF_CONNTRACK_SCTP_H`; structs `ip_ct_sctp`; enums `sctp_conntrack`; typedefs none; function-like declarations/helpers none.

Control flow: The SCTP conntrack implementation uses this header to store original/reply verification tags and the protocol state while packets advance association state.

State and persistence behavior: State is per conntrack entry and persists for the lifetime of the association in the conntrack table.

Dependencies and integration points: Integrates with `uapi/linux/netfilter/nf_conntrack_sctp.h`, conntrack protocol dispatch, and SCTP packet parsing code.

Risks and test signals: Risks are accepting packets with wrong verification tags or mishandling multihoming paths. Test INIT/COOKIE paths, shutdown, abort, and tag mismatch cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_sctp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_sip.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_sip.h

Purpose: Declares the SIP conntrack helper interface: SIP/SDP header descriptors, parser entry points, expectation classes, and NAT hook callbacks for SIP payload rewriting.

Important APIs, types, and functions: Key types include `struct nf_ct_sip_master`, `struct sdp_media_type`, `struct sip_handler`, `struct sip_header`, `enum sip_header_types`, `enum sdp_header_types`, and `struct nf_nat_sip_hooks`. Parser APIs include `ct_sip_parse_request()`, `ct_sip_get_header()`, URI/address/numerical parameter parsers, and SDP header lookup. Detected source surface: 198 lines; includes `linux/skbuff.h`, `linux/types.h`, `net/netfilter/nf_conntrack_expect.h`; macros `SDP_HDR`, `SDP_MEDIA_TYPE`, `SIP_EXPECT_MAX`, `SIP_HANDLER`, `SIP_HDR`, `SIP_PORT`, `SIP_TIMEOUT`, `__NF_CONNTRACK_SIP_H__`, `__SIP_HDR`; structs `nf_conntrack_expect`, `nf_ct_sip_master`, `nf_nat_sip_hooks`, `sdp_media_type`, `sip_handler`, `sip_header`; enums `sdp_header_types`, `sip_expectation_classes`, `sip_header_types`; typedefs none; function-like declarations/helpers `ct_sip_get_header`, `ct_sip_get_sdp_header`, `ct_sip_parse_address_param`, `ct_sip_parse_header_uri`, `ct_sip_parse_numerical_param`, `ct_sip_parse_request`, `int`.

Control flow: The helper parses SIP control messages on port 5060, finds request/response methods, extracts headers and SDP media addresses, creates media expectations, and optionally calls NAT hooks to rewrite addresses, ports, Via/Contact records, SDP owners, and content length.

State and persistence behavior: Master state keeps direct media and signaling expectations. NAT hooks are RCU-protected and protocol header descriptors are static metadata used by parsers.

Dependencies and integration points: Depends on skb data, type definitions, and conntrack expectations. It integrates tightly with SIP NAT, UDP/TCP conntrack, and RTP/RTCP expectation handling.

Risks and test signals: SIP is text-heavy and ambiguous, so risks include parser desync, folded headers, short payloads, IPv6 literal handling, content-length mismatch after NAT, and expectation leaks. Test UDP/TCP SIP, SDP media negotiation, NAT rewriting, fragmented payloads, and malformed headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_sip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_snmp.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_snmp.h

Purpose: Declares the optional SNMP NAT helper hook used to translate embedded addresses in SNMP payloads.

Important APIs, types, and functions: Exports `nf_nat_snmp_hook_fn` and the RCU pointer `nf_nat_snmp_hook`. Detected source surface: 16 lines; includes `linux/netfilter.h`, `linux/skbuff.h`; macros `_NF_CONNTRACK_SNMP_H`; structs `nf_conn`; enums `ip_conntrack_info`; typedefs none; function-like declarations/helpers `nf_nat_snmp_hook_fn`.

Control flow: Conntrack/NAT code checks the hook under RCU and calls it with skb, hook state, direction, and manipulation type when SNMP payload rewriting is needed.

State and persistence behavior: The only state in this header is the global RCU hook pointer; module load/unload controls whether NAT support is active.

Dependencies and integration points: Depends on netfilter hook state and sk_buff. Integrates with the SNMP conntrack/NAT helper implementation.

Risks and test signals: Risks are RCU lifetime bugs and payload rewriting that changes packet checksums incorrectly. Test with NATed SNMP queries/traps and module unload while traffic is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_snmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_tcp.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_tcp.h

Purpose: Defines TCP conntrack per-direction window tracking and aggregate TCP connection state.

Important APIs, types, and functions: Important types are `struct ip_ct_tcp_state` for td_end/td_maxend/window/scale/flags and `struct ip_ct_tcp` for two directions, retransmission counters, last packet metadata, and last window. Detected source surface: 33 lines; includes `uapi/linux/netfilter/nf_conntrack_tcp.h`; macros `_NF_CONNTRACK_TCP_H`; structs `ip_ct_tcp`, `ip_ct_tcp_state`; enums none; typedefs none; function-like declarations/helpers none.

Control flow: The TCP conntrack implementation feeds parsed TCP headers into this state to validate sequence windows, infer connection state, detect retransmits, and apply liberal/strict tracking policy.

State and persistence behavior: State is per conntrack entry and persists across packets until timeout or destruction. It mirrors the TCP stream from a firewall perspective rather than owning socket state.

Dependencies and integration points: Pulls UAPI TCP conntrack enums and is consumed by net/netfilter TCP protocol tracking code.

Risks and test signals: Risks are sequence arithmetic overflow, incorrect window scaling, false invalid drops, and stale retransmission counters. Test handshake, FIN/RST, retransmits, out-of-window packets, and asymmetric routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_tcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_tftp.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_tftp.h

Purpose: Defines TFTP helper constants, minimal packet header, opcodes, and the optional NAT callback for dynamic data-port expectations.

Important APIs, types, and functions: Exports `TFTP_PORT`, `struct tftphdr`, opcode constants, `nf_nat_tftp_hook_fn`, and RCU pointer `nf_nat_tftp_hook`. Detected source surface: 29 lines; includes `linux/netfilter.h`, `linux/skbuff.h`, `linux/types.h`, `net/netfilter/nf_conntrack_expect.h`; macros `TFTP_OPCODE_ACK`, `TFTP_OPCODE_DATA`, `TFTP_OPCODE_ERROR`, `TFTP_OPCODE_READ`, `TFTP_OPCODE_WRITE`, `TFTP_PORT`, `_NF_CONNTRACK_TFTP_H`; structs `nf_conntrack_expect`, `tftphdr`; enums `ip_conntrack_info`; typedefs none; function-like declarations/helpers `nf_nat_tftp_hook_fn`.

Control flow: The conntrack helper parses read/write requests on UDP port 69, creates expectations for server-selected data ports, and calls the NAT hook when address or port rewriting is required.

State and persistence behavior: The header itself has only the RCU NAT hook; per-flow state is held by conntrack expectations outside the header.

Dependencies and integration points: Depends on netfilter, skb, types, and conntrack expectation support. Integrates with UDP conntrack and NAT helpers.

Risks and test signals: Risks are accepting malformed opcodes, failing to constrain expected data flows, and hook lifetime races. Test RRQ/WRQ, DATA/ACK flows, NAT translation, retransmissions, and invalid opcodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_tftp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_zones_common.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_zones_common.h

Purpose: Defines common conntrack zone identifiers, direction masks, and zone metadata used to partition conntrack state.

Important APIs, types, and functions: Exports default zone constants, direction bit masks, `NF_CT_FLAG_MARK`, `struct nf_conntrack_zone`, and `nf_ct_zone_dflt`. Detected source surface: 24 lines; includes `uapi/linux/netfilter/nf_conntrack_tuple_common.h`; macros `NF_CT_DEFAULT_ZONE_DIR`, `NF_CT_DEFAULT_ZONE_ID`, `NF_CT_FLAG_MARK`, `NF_CT_ZONE_DIR_ORIG`, `NF_CT_ZONE_DIR_REPL`, `_NF_CONNTRACK_ZONES_COMMON_H`; structs `nf_conntrack_zone`; enums none; typedefs none; function-like declarations/helpers none.

Control flow: Conntrack code combines zone id, direction mask, and mark flag when hashing or matching tuples so otherwise identical flows can be isolated by namespace, ruleset, or mark.

State and persistence behavior: A zone is immutable metadata attached to a lookup or connection. The default zone is a shared constant.

Dependencies and integration points: Depends on conntrack tuple direction UAPI. Used by core conntrack, nftables/iptables ct zone targets, and net namespace rules.

Risks and test signals: Risks are default-zone leakage, direction mask mismatch, and mark-based zone confusion. Test same tuple in separate zones and original/reply direction restrictions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_zones_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nfnetlink.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter/nfnetlink.h

Purpose: Declares the kernel-side nfnetlink subsystem registration and message dispatch interface for netfilter families.

Important APIs, types, and functions: Key types are `struct nfnl_info`, `enum nfnl_callback_type`, `struct nfnl_callback`, `enum nfnl_abort_action`, and `struct nfnetlink_subsystem`. APIs include subsystem register/unregister, send/unicast/broadcast/set_err, `nfnl_msg_type()`, `nfnl_fill_hdr()`, `nfnl_msg_put()`, and per-subsystem locking. Detected source surface: 108 lines; includes `linux/capability.h`, `linux/netlink.h`, `net/netlink.h`, `uapi/linux/netfilter/nfnetlink.h`; macros `MODULE_ALIAS_NFNL_SUBSYS`, `_NFNETLINK_H`; structs `module`, `net`, `netlink_ext_ack`, `nfgenmsg`, `nfnetlink_subsystem`, `nfnl_callback`, `nfnl_info`, `nlmsghdr`, `sock`; enums `nfnl_abort_action`, `nfnl_callback_type`; typedefs none; function-like declarations/helpers `lockdep_nfnl_is_held`, `nfnetlink_broadcast`, `nfnetlink_has_listeners`, `nfnetlink_send`, `nfnetlink_set_err`, `nfnetlink_subsys_register`, `nfnetlink_subsys_unregister`, `nfnetlink_unicast`, `nfnl_fill_hdr`, `nfnl_lock`, `nfnl_msg_type`, `nfnl_unlock`.

Control flow: Subsystems register callback arrays keyed by message type. nfnetlink receives netlink messages, checks policy and privileges, dispatches callbacks, supports batch commit/abort, and emits replies or multicast notifications.

State and persistence behavior: Registered subsystem tables, callback arrays, and locks are global kernel state; skb messages are transient. Batch callbacks use abort actions to unwind partial transactions.

Dependencies and integration points: Depends on netlink, capabilities, net namespaces, and UAPI nfnetlink IDs. Used by conntrack, queue, log, accounting, osf, and nftables-style netfilter subsystems.

Risks and test signals: Risks are policy gaps, missing capability checks, lock ordering bugs, and malformed nested attributes. Test strict netlink validation, listener multicast, batch abort, and namespace isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nfnetlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nfnetlink_acct.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter/nfnetlink_acct.h

Purpose: Declares nfnetlink accounting object lookup, reference, update, and quota helpers.

Important APIs, types, and functions: Exports accounting use flags, opaque `struct nf_acct`, `nfnl_acct_find_get()`, `nfnl_acct_put()`, `nfnl_acct_update()`, and `nfnl_acct_overquota()`. Detected source surface: 20 lines; includes `net/net_namespace.h`, `uapi/linux/netfilter/nfnetlink_acct.h`; macros `_NFNL_ACCT_H_`; structs `nf_acct`; enums none; typedefs none; function-like declarations/helpers `nfnl_acct_overquota`, `nfnl_acct_put`, `nfnl_acct_update`.

Control flow: Rule evaluation obtains an accounting object, updates byte/packet counters from skb traffic, checks quota state, and drops the reference when done.

State and persistence behavior: Accounting objects are named, reference-counted net namespace state whose counters persist until userspace deletes or resets them.

Dependencies and integration points: Depends on nfnetlink acct UAPI and net namespace types. Integrated by xt/nft accounting matches and targets.

Risks and test signals: Risks are reference leaks, counter wrap expectations, quota race behavior, and namespace lookup confusion. Test object creation/deletion under traffic, quota crossing, and concurrent readers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nfnetlink_acct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nfnetlink_osf.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter/nfnetlink_osf.h

Purpose: Declares passive OS fingerprint matching structures and lookup APIs for nfnetlink OSF.

Important APIs, types, and functions: Exports match-state enum, global `nf_osf_fingers`, `struct nf_osf_finger`, `struct nf_osf_data`, `nf_osf_match()`, and `nf_osf_find()`. Detected source surface: 38 lines; includes `uapi/linux/netfilter/nfnetlink_osf.h`; macros `_NFOSF_H`; structs `list_head`, `nf_osf_data`, `nf_osf_finger`, `nf_osf_user_finger`, `rcu_head`; enums `osf_fmatch_states`; typedefs none; function-like declarations/helpers `nf_osf_find`, `nf_osf_match`.

Control flow: OSF code compares TCP/IP header characteristics from skb data against loaded fingerprint lists, optionally fills match data, and reports whether a signature matches.

State and persistence behavior: Fingerprint lists are global loaded rule data indexed by generation/family; per-call `nf_osf_data` stores the result view.

Dependencies and integration points: Depends on the nfnetlink OSF UAPI fingerprint format and packet parsing. Integrated with netfilter matches that classify remote OSes.

Risks and test signals: Risks are stale signatures, list concurrency, overbroad wildcard matches, and malformed TCP option parsing. Test known OS fingerprints, unknown packets, IPv4/IPv6 families, and dynamic fingerprint updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/nfnetlink_osf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/x_tables.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter/x_tables.h

Purpose: Defines the core in-kernel x_tables framework interface used by iptables, ip6tables, arptables, and ebtables matches, targets, tables, counters, compatibility translation, and hook allocation.

Important APIs, types, and functions: Key types are `struct xt_action_param`, match/target check and destroy parameter structs, `struct xt_match`, `struct xt_target`, `struct xt_table`, `struct xt_table_info`, compatibility entry types, and per-cpu counter helpers. APIs register/unregister matches and targets, validate entries and hooks, copy counters, register/replace/unregister tables, find modules/revisions/tables, allocate table info, manage recursive sequence counters, compare interface names, allocate counters, and allocate hook ops. Detected source surface: 537 lines; includes `linux/netdevice.h`, `linux/netfilter.h`, `linux/netfilter_ipv4.h`, `linux/static_key.h`, `net/compat.h`, `uapi/linux/netfilter/x_tables.h`; macros `COMPAT_XT_ALIGN`, `NF_INVF`, `_X_TABLES_H`; structs `_compat_xt_align`, `compat_xt_counters`, `compat_xt_counters_info`, `compat_xt_entry_match`, `compat_xt_entry_target`, `list_head`, `module`, `net`, `nf_hook_ops`, `xt_action_param`, `xt_counters`, `xt_counters_info`, `xt_entry_match`, `xt_entry_target`, `xt_match`, `xt_mtchk_param`, `xt_mtdtor_param`, `xt_percpu_counter_alloc_state`, and 5 more; enums none; typedefs none; function-like declarations/helpers `ifname_compare_aligned`, `int`, `per_cpu_ptr`, `this_cpu_ptr`, `xt_check_entry_offsets`, `xt_check_hooks_match`, `xt_check_hooks_target`, `xt_check_match`, `xt_check_proc_name`, `xt_check_table_hooks`, `xt_check_target`, `xt_compat_add_offset`, `xt_compat_calc_jump`, `xt_compat_check_entry_offsets`, `xt_compat_flush_offsets`, `xt_compat_init_offsets`, `xt_compat_lock`, `xt_compat_match_from_user`, and 34 more.

Control flow: Packet traversal calls table-specific `*_do_table()` code, which walks entries, invokes registered match callbacks, and executes target callbacks. Control-plane replacement validates offsets, hooks, revisions, and compat layout before swapping table info under synchronization.

State and persistence behavior: State includes global match/target registries, per-net tables, per-cpu counters, sequence counts for recursive writers, static keys, and compat offset state. Table replacement is persistent until userspace changes or unregisters it.

Dependencies and integration points: Depends on netdevice, static keys, netfilter core, IPv4 helpers, UAPI x_tables, and compat support. It is the shared substrate for IPv4, IPv6, ARP, and bridge table headers.

Risks and test signals: Risks are userspace offset validation bugs, compat size mismatches, counter races, module reference lifetime, and hook-mask mistakes. Test rule insertion/replacement/deletion, 32-bit compat tools on 64-bit kernels, per-cpu counter reads, and concurrent packet traversal during table swaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter/x_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter_arp/arp_tables.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter_arp/arp_tables.h

Purpose: Declares ARP-specific x_tables wrappers and initial table helpers for arptables.

Important APIs, types, and functions: Exports `struct arpt_standard`, `struct arpt_error`, initialization macros, table allocation/register/unregister/evaluation APIs, and compat ARP entry helpers. Detected source surface: 78 lines; includes `linux/if.h`, `linux/if_arp.h`, `linux/in.h`, `linux/skbuff.h`, `net/compat.h`, `uapi/linux/netfilter_arp/arp_tables.h`; macros `ARPT_ENTRY_INIT`, `ARPT_ERROR_INIT`, `ARPT_STANDARD_INIT`, `_ARPTABLES_H`; structs `arpt_arp`, `arpt_entry`, `arpt_error`, `arpt_standard`, `compat_arpt_entry`, `compat_xt_counters`, `xt_error_target`, `xt_standard_target`; enums none; typedefs none; function-like declarations/helpers `arpt_do_table`, `arpt_register_table`, `arpt_unregister_table`, `compat_arpt_get_target`.

Control flow: ARP packets enter `arpt_do_table()`, which evaluates x_tables entries with ARP-specific UAPI entry layout. Registration installs per-net ARP tables backed by xt_table data.

State and persistence behavior: Runtime table state is owned by x_tables per network namespace; this header contributes ARP initial entries and compat layout definitions.

Dependencies and integration points: Depends on interface, IP, ARP, skb, UAPI arptables, x_tables, and optional compat support.

Risks and test signals: Risks are wrong ARP entry sizing, target verdict encoding errors, and compat alignment drift. Test arptables rule load, error target fallback, packet match behavior, and 32-bit userspace compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter_arp/arp_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter_bridge.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter_bridge.h

Purpose: Defines bridge netfilter helpers for sk_buff bridge metadata, fake route cleanup, physical in/out device queries, and prerouting state checks.

Important APIs, types, and functions: Key exports are `struct nf_bridge_frag_data`, `br_handle_frame_finish()`, `br_drop_fake_rtable()`, `nf_bridge_info_get()`, `nf_bridge_info_exists()`, physical interface accessors, and `nf_bridge_in_prerouting()`. Detected source surface: 88 lines; includes `linux/skbuff.h`, `uapi/linux/netfilter_bridge.h`; macros `__LINUX_BRIDGE_NETFILTER_H`, `br_drop_fake_rtable`; structs `dst_entry`, `nf_bridge_frag_data`; enums none; typedefs none; function-like declarations/helpers `br_drop_fake_rtable`, `br_handle_frame_finish`, `nf_bridge_get_physindev`, `nf_bridge_get_physinif`, `nf_bridge_get_physoutdev`, `nf_bridge_get_physoutif`, `nf_bridge_in_prerouting`, `nf_bridge_info_exists`, `nf_bridge_info_get`, `skb_ext_exist`, `skb_ext_find`.

Control flow: Bridge netfilter attaches metadata to bridged skbs, carries fragmentation state when IPv4/IPv6 bridge hooks fragment packets, and later resumes bridge frame handling or drops fake route entries.

State and persistence behavior: State is per-skb bridge info plus optional frag data; no persistent global state is owned by the header.

Dependencies and integration points: Depends on bridge netfilter UAPI and sk_buff. Integrated by bridge, IPv4/IPv6 netfilter, ebtables, and nf_bridge forwarding paths.

Risks and test signals: Risks are stale physical device pointers, fake dst leaks, and wrong prerouting detection after skb clones. Test bridged IPv4/IPv6 traffic through netfilter hooks, fragmentation, and bridge device teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter_bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter_bridge/ebtables.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter_bridge/ebtables.h

Purpose: Declares the ebtables bridge filtering framework types for bridge matches, watchers, targets, tables, stack handling, and registration.

Important APIs, types, and functions: Important types are `struct ebt_match`, `struct ebt_watcher`, `struct ebt_target`, `struct ebt_chainstack`, `struct ebt_table_info`, and `struct ebt_table`. APIs register/unregister tables/templates and run `ebt_do_table()`. Detected source surface: 127 lines; includes `linux/if.h`, `linux/if_ether.h`, `uapi/linux/netfilter_bridge/ebtables.h`; macros `BASE_CHAIN`, `CLEAR_BASE_CHAIN_BIT`, `EBT_ALIGN`, `__LINUX_BRIDGE_EFF_H`; structs `ebt_chainstack`, `ebt_counter`, `ebt_entries`, `ebt_entry`, `ebt_match`, `ebt_replace_kernel`, `ebt_table`, `ebt_table_info`, `ebt_target`, `ebt_watcher`, `list_head`, `module`, `nf_hook_ops`; enums none; typedefs none; function-like declarations/helpers `ebt_do_table`, `ebt_invalid_target`, `ebt_register_table`, `ebt_register_template`, `ebt_unregister_table`, `ebt_unregister_table_pre_exit`, `ebt_unregister_template`, `int`.

Control flow: Bridge packets traverse ebtables chains, invoking match callbacks, watcher callbacks for side effects, and target callbacks for verdicts. Table registration installs initial entries and private table info.

State and persistence behavior: Per-net table state includes entries, counters, hook entry offsets, underflow pointers, chain stack, and initial entries. Module registration state tracks matches, watchers, and targets.

Dependencies and integration points: Depends on network interface, Ethernet, UAPI ebtables, x_tables alignment, and bridge hook definitions.

Risks and test signals: Risks are invalid target verdicts, chain stack overflow, counter races, and compat/layout mismatch with userspace ebtables. Test bridge filter/nat/broute tables, watcher side effects, base-chain underflows, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter_bridge/ebtables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter_defs.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter_defs.h

Purpose: Provides small shared netfilter hook-count constants over the UAPI netfilter definitions.

Important APIs, types, and functions: Exports `NF_ARP_NUMHOOKS` and `NF_MAX_HOOKS`. Detected source surface: 12 lines; includes `uapi/linux/netfilter.h`; macros `NF_ARP_NUMHOOKS`, `NF_MAX_HOOKS`, `__LINUX_NETFILTER_CORE_H_`; structs none; enums none; typedefs none; function-like declarations/helpers none.

Control flow: There is no runtime flow; macros are consumed at compile time for array sizing and hook iteration bounds.

State and persistence behavior: No state is stored. The constants are compile-time ABI assumptions for hook arrays.

Dependencies and integration points: Depends on UAPI netfilter hook numbering and is included by netfilter core users.

Risks and test signals: Risks are hook-count drift if UAPI families change. Test by building all netfilter families and running hook registration selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter_ipv4.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter_ipv4.h

Purpose: Declares IPv4-specific netfilter route and checksum helpers used after packet mangling or queue reinjection.

Important APIs, types, and functions: Important types/APIs are `struct ip_rt_info`, `ip_route_me_harder()`, `nf_ip_route()`, and `nf_ip_checksum()`. Detected source surface: 41 lines; includes `uapi/linux/netfilter_ipv4.h`; macros `__LINUX_IP_NETFILTER_H`; structs `flowi`, `ip_rt_info`, `nf_queue_entry`; enums none; typedefs none; function-like declarations/helpers `ip_route_me_harder`, `nf_ip_checksum`, `nf_ip_route`.

Control flow: After a hook modifies an IPv4 packet, callers reroute it with `ip_route_me_harder()` or `nf_ip_route()` and recompute/check checksums with `nf_ip_checksum()` as needed.

State and persistence behavior: The header owns no persistent state; route results are dst entries attached to skbs or returned through pointers.

Dependencies and integration points: Depends on UAPI IPv4 netfilter, routing flow keys, sk_buff, and IP checksum helpers.

Risks and test signals: Risks are stale route cache after NAT/mark changes and checksum coverage mistakes. Test DNAT/SNAT, policy routing, local output reroute, and fragmented packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter_ipv4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter_ipv4/ip_tables.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter_ipv4/ip_tables.h

Purpose: Declares IPv4 iptables wrappers around x_tables, including initial entry macros, table registration, packet evaluation, and compat entry layout.

Important APIs, types, and functions: Exports `ipt_register_table()`, `ipt_unregister_table_exit()`, `ipt_alloc_initial_table()`, `ipt_do_table()`, `struct ipt_standard`, `struct ipt_error`, init macros, and compat entry helpers. Detected source surface: 90 lines; includes `linux/if.h`, `linux/in.h`, `linux/init.h`, `linux/ip.h`, `linux/skbuff.h`, `net/compat.h`, `uapi/linux/netfilter_ipv4/ip_tables.h`; macros `IPT_ENTRY_INIT`, `IPT_ERROR_INIT`, `IPT_STANDARD_INIT`, `_IPTABLES_H`; structs `compat_ipt_entry`, `compat_xt_counters`, `ipt_entry`, `ipt_error`, `ipt_ip`, `ipt_standard`, `sk_buff`, `xt_error_target`, `xt_standard_target`; enums none; typedefs none; function-like declarations/helpers `compat_ipt_get_target`, `ipt_do_table`, `ipt_register_table`, `ipt_unregister_table_exit`.

Control flow: IPv4 hook ops call `ipt_do_table()` with hook state and table private data. Control-plane code allocates and registers xt_table-backed IPv4 tables.

State and persistence behavior: Per-net IPv4 table state is owned by x_tables; this header fixes IPv4 entry and compat layouts.

Dependencies and integration points: Depends on IPv4, skb, UAPI ip_tables, x_tables, and compat support.

Risks and test signals: Risks are entry offset mistakes, verdict encoding errors, and compat target alignment issues. Test filter/nat/mangle table traversal, rule replacement, and 32-bit iptables userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter_ipv4/ip_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter_ipv6.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter_ipv6.h

Purpose: Declares IPv6-specific netfilter helpers for address checks, routing, bridge fragmentation, route repair, TCP syncookie sequence helpers, and hop-by-hop length validation.

Important APIs, types, and functions: Key exports are `nf_ipv6_chk_addr()`, `__nf_ip6_route()`, `nf_ip6_route()`, `br_ip6_fragment()`, `nf_br_ip6_fragment()`, `ip6_route_me_harder()`, `nf_ip6_route_me_harder()`, `nf_ipv6_cookie_init_sequence()`, `nf_cookie_v6_check()`, and `nf_ip6_check_hbh_len()`. Detected source surface: 121 lines; includes `net/addrconf.h`, `net/netfilter/ipv6/nf_defrag_ipv6.h`, `net/tcp.h`, `uapi/linux/netfilter_ipv6.h`; macros `__LINUX_IP6_NETFILTER_H`; structs `flowi`, `in6_addr`, `ip6_rt_info`, `nf_bridge_frag_data`, `nf_queue_entry`, `sk_buff`; enums none; typedefs none; function-like declarations/helpers `__cookie_v6_check`, `__cookie_v6_init_sequence`, `__nf_ip6_route`, `br_ip6_fragment`, `ip6_route_me_harder`, `ipv6_chk_addr`, `nf_br_ip6_fragment`, `nf_cookie_v6_check`, `nf_ip6_check_hbh_len`, `nf_ip6_checksum`, `nf_ip6_ext_hdr`, `nf_ip6_route`, `nf_ip6_route_me_harder`, `nf_ipv6_chk_addr`, `nf_ipv6_cookie_init_sequence`.

Control flow: Netfilter users call these helpers after modifying IPv6 packets, when routing queued packets, when bridge hooks need fragmentation, or when validating TCP syncookies through IPv6 headers.

State and persistence behavior: No global state is defined; helpers operate on net namespaces, dst pointers, sockets, skbs, and parsed headers.

Dependencies and integration points: Depends on IPv6 UAPI, TCP helpers, addrconf, defrag, bridge fragments, and route APIs.

Risks and test signals: Risks are extension header length errors, reroute failures after NAT/mark changes, and fragmentation behavior across bridge hooks. Test IPv6 NAT/mangle paths, HBH headers, syncookies, fragmented bridged traffic, and disabled IPv6 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter_ipv6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter_ipv6/ip6_tables.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter_ipv6/ip6_tables.h

Purpose: Declares IPv6 iptables wrappers around x_tables.

Important APIs, types, and functions: Exports `ip6t_alloc_initial_table()`, `ip6t_register_table()`, `ip6t_unregister_table_exit()`, `ip6t_do_table()`, and compat IPv6 entry helpers. Detected source surface: 54 lines; includes `linux/if.h`, `linux/in6.h`, `linux/init.h`, `linux/ipv6.h`, `linux/skbuff.h`, `net/compat.h`, `uapi/linux/netfilter_ipv6/ip6_tables.h`; macros `_IP6_TABLES_H`; structs `compat_ip6t_entry`, `compat_xt_counters`, `ip6t_ip6`; enums none; typedefs none; function-like declarations/helpers `compat_ip6t_get_target`, `ip6t_do_table`, `ip6t_register_table`, `ip6t_unregister_table_exit`.

Control flow: IPv6 netfilter hooks invoke `ip6t_do_table()` to evaluate table entries, while control-plane code registers xt_table-backed IPv6 tables.

State and persistence behavior: Per-net table state and counters are managed by x_tables; this header fixes IPv6 entry layout and compat conversion.

Dependencies and integration points: Depends on IPv6 headers, skb, UAPI ip6_tables, x_tables, and compat support.

Risks and test signals: Risks are IPv6 address/mask layout errors, compat offsets, and hook-mask mismatches. Test ip6tables rule load, extension-header matches, concurrent replacement, and 32-bit compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter_ipv6/ip6_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter_netdev.h -->
# sources/distributed-fs/ceph-client/include/linux/netfilter_netdev.h

Purpose: Defines ingress and egress netdev netfilter hook helpers that bridge net_device packet paths to `nf_hook()`.

Important APIs, types, and functions: Exports `nf_hook_ingress_active()`, `nf_hook_ingress()`, `nf_hook_egress_active()`, `nf_hook_egress()`, `nf_skip_egress()`, and `nf_hook_netdev_init()` with configuration-dependent stubs. Detected source surface: 151 lines; includes `linux/netdevice.h`, `linux/netfilter.h`; macros `_NETFILTER_NETDEV_H_`; structs `net_device`, `nf_hook_entries`, `nf_hook_state`; enums none; typedefs none; function-like declarations/helpers `nf_hook_egress_active`, `nf_hook_ingress`, `nf_hook_ingress_active`, `nf_hook_netdev_init`, `nf_skip_egress`, `rcu_access_pointer`.

Control flow: The network device receive/transmit paths check static keys and per-device hook lists, initialize hook state with netdev family and hook number, and pass skbs through ingress or egress hooks. Egress code may consume/drop/return a replacement skb and supports skip marking to avoid recursion.

State and persistence behavior: State lives in static keys, per-device hook lists, skb extension flags, and net namespace hook arrays. The header defines inline control decisions but not backing storage.

Dependencies and integration points: Depends on netfilter core and netdevice structures. Used by tc/nftables netdev family integration and driver-facing packet paths.

Risks and test signals: Risks are recursion on egress reinjection, wrong return convention for consumed skbs, and static-key/config stub mismatches. Test ingress drop/accept, egress redirect/drop, disabled CONFIG_NETFILTER_INGRESS/EGRESS, and device unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfilter_netdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfs.h -->
# sources/distributed-fs/ceph-client/include/linux/netfs.h

Purpose: Declares the netfs helper library used by network filesystems to share buffered, direct, readahead, writeback, local-cache, and subrequest orchestration.

Important APIs, types, and functions: Core types are `struct netfs_inode`, `struct netfs_group`, `struct netfs_folio`, `struct netfs_io_stream`, `struct netfs_cache_resources`, `struct netfs_io_subrequest`, `struct netfs_io_request`, `struct netfs_request_ops`, and `struct netfs_cache_ops`. APIs cover read/write iterators, single-object I/O, address-space operations, page_mkwrite, subrequest lifecycle, iterator extraction, I/O start/end, folio queues, and buffer allocation. Detected source surface: 554 lines; includes `linux/fs.h`, `linux/pagemap.h`, `linux/rolling_buffer.h`, `linux/uio.h`, `linux/workqueue.h`; macros `NETFS_FOLIO_COPY_TO_CACHE`, `NETFS_FOLIO_INFO`, `NETFS_ICTX_MODIFIED_ATTR`, `NETFS_ICTX_ODIRECT`, `NETFS_ICTX_SINGLE_NO_UPLOAD`, `NETFS_ICTX_UNBUFFERED`, `NETFS_ROLLBUF_PAGECACHE_MARK`, `NETFS_ROLLBUF_PUT_MARK`, `NETFS_RREQ_ALL_QUEUED`, `NETFS_RREQ_FAILED`, `NETFS_RREQ_FOLIO_COPY_TO_CACHE`, `NETFS_RREQ_IN_PROGRESS`, `NETFS_RREQ_NO_UNLOCK_FOLIO`, `NETFS_RREQ_OFFLOAD_COLLECTION`, `NETFS_RREQ_PAUSE`, `NETFS_RREQ_RETRYING`, `NETFS_RREQ_SHORT_TRANSFER`, `NETFS_RREQ_UPLOAD_TO_SERVER`, and 13 more; structs `address_space`, `bio_vec`, `folio`, `folio_queue`, `fscache_cookie`, `inode`, `iov_iter`, `kiocb`, `list_head`, `mutex`, `netfs_cache_ops`, `netfs_cache_resources`, `netfs_folio`, `netfs_group`, `netfs_inode`, `netfs_io_request`, `netfs_io_stream`, `netfs_io_subrequest`, and 6 more; enums `netfs_io_origin`, `netfs_io_source`, `netfs_read_from_hole`, `netfs_sreq_ref_trace`; typedefs `mempool_t`, `void`; function-like declarations/helpers `__netfs_folio_info`, `container_of`, `folio_start_private_2`, `netfs_alloc_folioq_buffer`, `netfs_buffered_read_iter`, `netfs_buffered_write_iter_locked`, `netfs_clear_inode_writeback`, `netfs_dirty_folio`, `netfs_end_io_direct`, `netfs_end_io_read`, `netfs_end_io_write`, `netfs_extract_user_iter`, `netfs_file_read_iter`, `netfs_file_write_iter`, `netfs_folioq_free`, `netfs_free_folioq_buffer`, `netfs_get_subrequest`, `netfs_inode_init`, and 31 more.

Control flow: High-level VFS reads/writes allocate a netfs request, split it into subrequests for server/cache streams, issue filesystem/cache callbacks, collect completions, retry or fail streams, update folios, and finish AIO/writeback state.

State and persistence behavior: Per-inode state tracks remote size, zero-point optimization, outstanding I/O, flags, optional fscache cookie, and writeback lock. Per-request/subrequest state persists while asynchronous I/O is active and is reference counted.

Dependencies and integration points: Depends on workqueues, VFS inode/pagecache, uio iterators, rolling buffers, folio queues, optional fscache, and filesystem-provided ops. Ceph, AFS, NFS, and other network filesystems are expected consumers.

Risks and test signals: Risks are refcount leaks, folio private flag misuse, cache/server divergence, retry deadlocks, and direct-I/O lifetime bugs. Test buffered reads, readahead, writeback, DIO, cache hits/misses, short reads, EOF, retries, invalidation, and inode eviction waiting for outstanding I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netlink.h -->
# sources/distributed-fs/ceph-client/include/linux/netlink.h

Purpose: Declares the kernel netlink socket API, skb control block layout, extended ack helpers, dump controls, multicast, tap, capability checks, and large skb allocation.

Important APIs, types, and functions: Important exports include `NETLINK_CB`, `struct netlink_kernel_cfg`, `struct netlink_ext_ack`, extended-ack macros, kernel socket create/release, group changes, ack/unicast/broadcast APIs, notifier registration, dump callbacks/control, tap registration, and capability helpers. Detected source surface: 361 lines; includes `linux/capability.h`, `linux/export.h`, `linux/skbuff.h`, `net/scm.h`, `uapi/linux/netlink.h`; macros `NETLINK_CB`, `NETLINK_CREDS`, `NETLINK_CTX_SIZE`, `NETLINK_MAX_COOKIE_LEN`, `NETLINK_MAX_FMTMSG_LEN`, `NLMSG_DEFAULT_SIZE`, `NLMSG_GOODSIZE`, `NL_ASSERT_CTX_FITS`, `NL_CFG_F_NONROOT_RECV`, `NL_CFG_F_NONROOT_SEND`, `NL_REQ_ATTR_CHECK`, `NL_SET_BAD_ATTR`, `NL_SET_BAD_ATTR_POLICY`, `NL_SET_ERR_ATTR_MISS`, `NL_SET_ERR_MSG`, `NL_SET_ERR_MSG_ATTR`, `NL_SET_ERR_MSG_ATTR_FMT`, `NL_SET_ERR_MSG_ATTR_POL`, and 7 more; structs `list_head`, `module`, `net`, `net_device`, `netlink_callback`, `netlink_dump_control`, `netlink_ext_ack`, `netlink_kernel_cfg`, `netlink_notify`, `netlink_skb_parms`, `netlink_tap`, `nlattr`, `nlmsghdr`, `scm_creds`, `sk_buff`, `sock`, `user_namespace`; enums `netlink_skb_flags`; typedefs `int`; function-like declarations/helpers `__netlink_change_ngroups`, `__netlink_clear_multicast_users`, `__netlink_dump_start`, `__netlink_kernel_create`, `__netlink_ns_capable`, `__nlmsg_put`, `do_trace_netlink_extack`, `int`, `netlink_ack`, `netlink_add_tap`, `netlink_attachskb`, `netlink_broadcast`, `netlink_broadcast_filtered`, `netlink_capable`, `netlink_change_ngroups`, `netlink_detachskb`, `netlink_dump_start`, `netlink_has_listeners`, and 15 more.

Control flow: Kernel subsystems create a netlink socket with input/bind hooks, receive skbs annotated through `NETLINK_CB`, validate attributes and privileges, reply with acks/extacks, and optionally run dump callbacks over multiple messages.

State and persistence behavior: Netlink socket tables, multicast group membership, dump cursors, tap lists, and skb credentials are runtime state. Extended ack fields are per-request diagnostic state.

Dependencies and integration points: Depends on capabilities, sk_buff, SCM credentials, UAPI netlink, net namespaces, and generic netlink/nfnetlink/rtnetlink users.

Risks and test signals: Risks are privilege bypass, missing extack context, dump cursor races, unbounded message sizes, and listener group leaks. Test strict validation, malformed attrs, dump interruption/resume, multicast delivery, and user namespace capability checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netpoll.h -->
# sources/distributed-fs/ceph-client/include/linux/netpoll.h

Purpose: Declares netpoll support for emergency UDP network I/O from constrained contexts such as console, panic, and crash paths.

Important APIs, types, and functions: Key types are `union inet_addr`, `struct netpoll`, and `struct netpoll_info`; APIs include poll disable/enable, `netpoll_send_udp()`, setup/free/cleanup helpers, poll locking, and TX-running checks. Detected source surface: 121 lines; includes `linux/interrupt.h`, `linux/list.h`, `linux/netdevice.h`, `linux/rcupdate.h`, `linux/refcount.h`; macros `_LINUX_NETPOLL_H`, `np_err`, `np_info`, `np_notice`; structs `delayed_work`, `in6_addr`, `napi_struct`, `net_device`, `netpoll`, `netpoll_info`, `rcu_head`, `semaphore`, `sk_buff_head`, `work_struct`; enums none; typedefs none; function-like declarations/helpers `__netpoll_free`, `__netpoll_setup`, `do_netpoll_cleanup`, `irqs_disabled`, `netpoll_cleanup`, `netpoll_poll_dev`, `netpoll_poll_disable`, `netpoll_poll_enable`, `netpoll_poll_unlock`, `netpoll_send_skb`, `netpoll_send_udp`, `netpoll_setup`, `netpoll_tx_running`, `smp_store_release`.

Control flow: A configured netpoll endpoint stores local/remote addresses, ports, MAC address, and device; send paths bypass normal process context where possible and poll device/NAPI state under netpoll locks.

State and persistence behavior: Per-netpoll endpoint state persists for the configured device and target. Per-device `netpoll_info` tracks refcount, cleanup work, rx/tx state, and napi ownership.

Dependencies and integration points: Depends on netdevice, interrupts, RCU, lists, and refcounts. Integrated by netconsole and emergency logging paths.

Risks and test signals: Risks are deadlocks with NAPI/device locks, use-after-free during device teardown, and packet loss under panic constraints. Test setup/cleanup, device unregister, high-rate console output, and lockdep under netpoll transmission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netpoll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs.h -->
# sources/distributed-fs/ceph-client/include/linux/nfs.h

Purpose: Defines common NFS client constants and file-handle helpers shared by NFS versions and localio support.

Important APIs, types, and functions: Exports NFS localio program/procedure IDs, `NFS_MAXFHSIZE`, `struct nfs_fh`, `nfs_compare_fh()`, `nfs_copy_fh()`, `enum nfs3_stable_how`, and `nfs_fhandle_hash()`. Detected source surface: 69 lines; includes `linux/crc32.h`, `linux/cred.h`, `linux/string.h`, `linux/sunrpc/auth.h`, `linux/sunrpc/msg_prot.h`, `uapi/linux/nfs.h`; macros `LOCALIOPROC_NULL`, `LOCALIOPROC_UUID_IS_LOCAL`, `NFS_LOCALIO_PROGRAM`, `NFS_MAXFHSIZE`, `_LINUX_NFS_H`; structs `nfs_fh`; enums `nfs3_stable_how`; typedefs none; function-like declarations/helpers `nfs_compare_fh`, `nfs_copy_fh`, `nfs_fhandle_hash`.

Control flow: Code compares/copies opaque file handles and hashes them for display or lookup; write paths use stable-how values to request unstable, data-sync, or file-sync semantics.

State and persistence behavior: File handles are persistent opaque server identifiers carried in inode and RPC state. The header owns no global storage.

Dependencies and integration points: Depends on credentials, SUNRPC auth/protocol, string helpers, crc32, and UAPI NFS constants.

Risks and test signals: Risks are file-handle length overflow, bad equality comparisons, and incorrect stable-write semantics. Test max-sized handles, copy/compare/hash helpers, and NFSv3 write commit paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs3.h -->
# sources/distributed-fs/ceph-client/include/linux/nfs3.h

Purpose: Adds kernel-side NFSv3 constants over the UAPI NFSv3 definitions.

Important APIs, types, and functions: Exports `NFS3_POST_OP_ATTR_WORDS` and includes `uapi/linux/nfs3.h`. Detected source surface: 14 lines; includes `uapi/linux/nfs3.h`; macros `NFS3_POST_OP_ATTR_WORDS`, `_LINUX_NFS3_H`; structs none; enums none; typedefs none; function-like declarations/helpers none.

Control flow: There is no runtime flow; XDR code uses the constant for sizing post-op attribute buffers.

State and persistence behavior: No runtime state is stored.

Dependencies and integration points: Depends on UAPI NFSv3 procedure/status/type definitions and NFS XDR code.

Risks and test signals: Risk is XDR buffer sizing drift if protocol attr encoding changes. Test NFSv3 getattr/write/rename replies and XDR decode bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs4.h -->
# sources/distributed-fs/ceph-client/include/linux/nfs4.h

Purpose: Defines the NFSv4 protocol constants, operation numbers, status values, stateids, attribute bitmaps, pNFS layout enums, session identifiers, callback opnums, and feature masks used by client and server XDR paths.

Important APIs, types, and functions: Important exports include NFSv4 operation/status enums, `nfs4_stateid`, verifier and session-id types, file attribute bit definitions across words 0-2, pNFS layout/device enums, net location structures, xattr options, and callback op numbers. Detected source surface: 918 lines; includes `linux/list.h`, `linux/sunrpc/msg_prot.h`, `linux/sunrpc/xdrgen/nfs4_1.h`, `linux/uidgid.h`, `uapi/linux/nfs4.h`; macros `FATTR4_WORD0_ACL`, `FATTR4_WORD0_ACLSUPPORT`, `FATTR4_WORD0_ARCHIVE`, `FATTR4_WORD0_CANSETTIME`, `FATTR4_WORD0_CASE_INSENSITIVE`, `FATTR4_WORD0_CASE_PRESERVING`, `FATTR4_WORD0_CHANGE`, `FATTR4_WORD0_CHOWN_RESTRICTED`, `FATTR4_WORD0_FH_EXPIRE_TYPE`, `FATTR4_WORD0_FILEHANDLE`, `FATTR4_WORD0_FILEID`, `FATTR4_WORD0_FILES_AVAIL`, `FATTR4_WORD0_FILES_FREE`, `FATTR4_WORD0_FILES_TOTAL`, `FATTR4_WORD0_FSID`, `FATTR4_WORD0_FS_LOCATIONS`, `FATTR4_WORD0_HIDDEN`, `FATTR4_WORD0_HOMOGENEOUS`, and 89 more; structs `nfs42_netaddr`, `nfs4_ace`, `nfs4_acl`, `nfs4_deviceid`, `nfs4_label`, `nfs4_op_map`, `nfs4_sessionid`, `nfs4_stateid_struct`, `nl4_server`; enums `createmode4`, `data_content4`, `filelayout_hint_care4`, `gddrnf4_status`, `limit_by4`, `lock_type4`, `netloc_type4`, `nfs4_acl_whotype`, `nfs4_change_attr_type`, `nfs4_open_delegation_type4`, `nfs4_setxattr_options`, `nfs_cb_opnum4`, `nfs_ftype4`, `nfs_opnum4`, and 14 more; typedefs `nfs4_stateid`, `nfs4_verifier`; function-like declarations/helpers `seqid_mutating_err`.

Control flow: No functions execute here. XDR encoders/decoders and state-management code use these constants to build COMPOUND calls, interpret server replies, select supported attributes, and negotiate sessions/layouts.

State and persistence behavior: The header defines protocol ABI values that persist on the wire and in saved client state. `stateid`, `deviceid`, and session ids are carried through runtime structs but storage is elsewhere.

Dependencies and integration points: Depends on base types, NFS UAPI/protocol definitions, and XDR users in `nfs_xdr.h`, NFSv4 client state code, pNFS layout drivers, and callback handling.

Risks and test signals: Risks are wrong bitmap word shifts, status-code mapping mistakes, and pNFS enum drift. Test NFSv4.0/4.1/4.2 mount, open/close/lock, delegations, session creation, pNFS layoutget/return, xattrs, and callback dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs_common.h -->
# sources/distributed-fs/ceph-client/include/linux/nfs_common.h

Purpose: Declares common conversion helpers from NFS protocol status codes to Linux errno values.

Important APIs, types, and functions: Exports `nfs_stat_to_errno()` and `nfs4_stat_to_errno()`. Detected source surface: 18 lines; includes `linux/errno.h`, `uapi/linux/nfs.h`; macros `_LINUX_NFS_COMMON_H`; structs none; enums none; typedefs none; function-like declarations/helpers `nfs4_stat_to_errno`, `nfs_localio_errno_to_nfs4_stat`, `nfs_stat_to_errno`.

Control flow: RPC completion paths call these helpers when translating server status fields into VFS-visible errors.

State and persistence behavior: No state is stored; mappings are deterministic conversion tables in implementation files.

Dependencies and integration points: Depends on errno and UAPI NFS status enums. Used throughout NFSv2/v3/v4 RPC decode paths.

Risks and test signals: Risks are incorrect errno mapping and retry policy changes. Test representative NFS status codes such as stale handle, jukebox/delay, permission, exist, and xattr errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs_fs.h -->
# sources/distributed-fs/ceph-client/include/linux/nfs_fs.h

Purpose: Declares the main in-memory NFS client filesystem structures and VFS integration APIs for inode state, open contexts, access caches, localio handles, cache invalidation, direct I/O, directory operations, writeback, and read paths.

Important APIs, types, and functions: Key types are `struct nfs_access_entry`, `struct nfs_lock_context`, `struct nfs_file_localio`, `struct nfs_open_context`, `struct nfs_open_dir_context`, `struct nfs_inode`, and `struct nfs4_copy_state`. Inline accessors include `NFS_I()`, `NFS_SB()`, `NFS_FH()`, `NFS_SERVER()`, `NFS_CLIENT()`, and `NFS_PROTO()`. Extern APIs cover inode refresh, permission/open contexts, fattr/fhandle allocation, file/dir ops, direct I/O, lookup, sysctl, automount, unlink, writeback, commit, readahead, and cache helpers. Detected source surface: 714 lines; includes `linux/in.h`, `linux/mempool.h`, `linux/mm.h`, `linux/netfs.h`, `linux/nfs.h`, `linux/nfs2.h`, `linux/nfs3.h`, `linux/nfs4.h`, `linux/nfs_fs_sb.h`, `linux/nfs_xdr.h`, and 9 more; macros `NFS_ACCESS_DELETE`, `NFS_ACCESS_EXECUTE`, `NFS_ACCESS_EXTEND`, `NFS_ACCESS_LOOKUP`, `NFS_ACCESS_MODIFY`, `NFS_ACCESS_READ`, `NFS_ACCESS_XALIST`, `NFS_ACCESS_XAREAD`, `NFS_ACCESS_XAWRITE`, `NFS_CONTEXT_BAD`, `NFS_CONTEXT_FILE_OPEN`, `NFS_CONTEXT_UNLOCK`, `NFS_CONTEXT_WRITE_SYNC`, `NFS_DEBUG`, `NFS_DIR_VERIFIER_SIZE`, `NFS_FSDATA_BLOCKED`, `NFS_IFDEBUG`, `NFS_INO_ACL_LRU_SET`, and 33 more; structs `completion`, `dentry`, `file`, `group_info`, `inode`, `iov_iter`, `kstat`, `list_head`, `mutex`, `netfs_inode`, `nfs4_cached_acl`, `nfs4_copy_state`, `nfs4_state`, `nfs4_threshold`, `nfs4_xattr_cache`, `nfs_access_entry`, `nfs_delegation`, `nfs_fattr`, and 18 more; enums none; typedefs none; function-like declarations/helpers `NFS_FILEID`, `NFS_MAXATTRTIMEO`, `NFS_MINATTRTIMEO`, `NFS_SB`, `NFS_STALE`, `__nfs_revalidate_inode`, `_nfs_display_fhandle`, `_nfs_display_fhandle_hash`, `container_of`, `min_t`, `nfs4_label_free`, `nfs_access_add_cache`, `nfs_access_get_cached`, `nfs_access_set_mask`, `nfs_access_zap_cache`, `nfs_atomic_open_v23`, `nfs_attribute_cache_expired`, `nfs_clear_invalid_mapping`, and 71 more.

Control flow: VFS calls enter NFS file/dir/inode operations, which consult open contexts and credentials, validate cached inode attributes, issue SUNRPC operations through `nfs_rpc_ops`, update inode/fattr state, and schedule read/write/commit work.

State and persistence behavior: NFS inode state persists in memory across VFS operations: fileid, file handle, validity flags, attr timeout windows, access cache rbtrees/LRUs, directory verifiers, writeback counters, open files, out-of-order change tracking, NFSv4 delegations/layouts, byte counters, xattr cache, and optional netfs context.

Dependencies and integration points: Depends on VFS, mm/pagecache, rbtrees, refcounts, SUNRPC, netfs when fscache is enabled, NFS protocol headers, and superblock state. It is the primary integration point between NFS client code and the kernel VFS.

Risks and test signals: Risks are cache invalidation bugs, open-context credential lifetime, out-of-order change handling, delegation/layout races, and writeback/commit accounting leaks. Test attribute revalidation, mmap writes, silly rename, direct I/O, pNFS layouts, delegations, localio, fscache, and server-side changes from another client.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs_fs_i.h -->
# sources/distributed-fs/ceph-client/include/linux/nfs_fs_i.h

Purpose: Defines lock-owner metadata embedded in NFS file/inode state for NFS lock manager and NFSv4 locks.

Important APIs, types, and functions: Exports `struct nfs_lock_info` and `struct nfs4_lock_info`. Detected source surface: 21 lines; includes none; macros `_NFS_FS_I`; structs `list_head`, `nfs4_lock_info`, `nfs4_lock_state`, `nfs_lock_info`, `nlm_lockowner`; enums none; typedefs none; function-like declarations/helpers none.

Control flow: Locking code associates VFS file locks with NLM lock owners or NFSv4 lock state so lock/unlock RPCs can be matched to owner identity.

State and persistence behavior: The fields persist with the relevant file/inode lock context while locks are active.

Dependencies and integration points: Integrates with NLM lock owners and NFSv4 lock state definitions.

Risks and test signals: Risks are lock-owner aliasing and stale lock state after recovery. Test POSIX byte-range locks, reclaim, unlock, and mixed local/remote owners.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs_fs_i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs_fs_sb.h -->
# sources/distributed-fs/ceph-client/include/linux/nfs_fs_sb.h

Purpose: Declares NFS client and server superblock state: transport clients, mount flags, timeouts, capabilities, NFSv4 session/state metadata, pNFS/localio data, migration state, and per-server counters.

Important APIs, types, and functions: Key types are `struct nfs_client` and `struct nfs_server`, with many mount option flags, client state bits, SP4 machine-credential levels, automount inheritance flags, file-handle volatility flags, migration flags, and `NFS_CAP_*` capability bits. Detected source surface: 334 lines; includes `linux/atomic.h`, `linux/backing-dev.h`, `linux/idr.h`, `linux/list.h`, `linux/nfs_xdr.h`, `linux/nfslocalio.h`, `linux/refcount.h`, `linux/sunrpc/xprt.h`, `linux/wait.h`; macros `NFS4SERV_DELEGATION_EXPIRED`, `NFS_AUTOMOUNT_INHERIT_BSIZE`, `NFS_AUTOMOUNT_INHERIT_RSIZE`, `NFS_AUTOMOUNT_INHERIT_WSIZE`, `NFS_CAP_ACLS`, `NFS_CAP_ALLOCATE`, `NFS_CAP_ATOMIC_OPEN`, `NFS_CAP_ATOMIC_OPEN_V1`, `NFS_CAP_CASE_INSENSITIVE`, `NFS_CAP_CASE_PRESERVING`, `NFS_CAP_CLONE`, `NFS_CAP_COPY`, `NFS_CAP_COPY_NOTIFY`, `NFS_CAP_DEALLOCATE`, `NFS_CAP_DELEGTIME`, `NFS_CAP_DIR_DELEG`, `NFS_CAP_FS_LOCATIONS`, `NFS_CAP_HARDLINKS`, and 70 more; structs `delayed_work`, `fscache_volume`, `hlist_head`, `idmap`, `kobject`, `list_head`, `net`, `nfs41_impl_id`, `nfs41_server_owner`, `nfs41_server_scope`, `nfs4_minor_version_ops`, `nfs4_sequence_args`, `nfs4_sequence_res`, `nfs4_session`, `nfs4_slot_table`, `nfs_auth_info`, `nfs_client`, `nfs_fsid`, and 14 more; enums `nfs4_change_attr_type`; typedefs none; function-like declarations/helpers none.

Control flow: Mount and clone paths allocate or reuse `nfs_client`, create `nfs_server`, negotiate fsinfo/capabilities, attach RPC clients and security, and later VFS operations consult these fields for protocol behavior and limits.

State and persistence behavior: This is long-lived per-client/per-superblock state: RPC clients, owner/client IDs, lease time, session pointers, flags, mount options, read/write sizes, attr cache bounds, caps, delegations, layout types, localio UUID/client, migration status, and IO stats.

Dependencies and integration points: Depends on lists, backing-dev, idr, wait queues, NFS XDR types, SUNRPC transports, localio, atomics, and refcounts. Used by NFS mount, namespace, client, pNFS, and state recovery code.

Risks and test signals: Risks are mount option misinterpretation, refcount/lifetime bugs across cloned servers, capability mismatch after migration, and state recovery races. Test mount variants, trunking, failover/migration, pNFS, lease renewal, and unmount while RPCs are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs_fs_sb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs_iostat.h -->
# sources/distributed-fs/ceph-client/include/linux/nfs_iostat.h

Purpose: Defines NFS per-mount IO statistics versioning and counter indexes exposed through client instrumentation.

Important APIs, types, and functions: Exports `NFS_IOSTAT_VERS`, byte counter enum values, and event counter enum values. Detected source surface: 122 lines; includes none; macros `NFS_IOSTAT_VERS`, `_LINUX_NFS_IOSTAT`; structs none; enums `nfs_stat_bytecounters`, `nfs_stat_eventcounters`; typedefs none; function-like declarations/helpers none.

Control flow: NFS read/write/metadata paths increment counters by enum index; proc/debug presentation code formats them according to the version.

State and persistence behavior: The header defines indexes only; per-mount counter storage is elsewhere. Counter names are persistent user-visible diagnostic ABI.

Dependencies and integration points: Consumed by NFS superblock/client stats and procfs reporting.

Risks and test signals: Risks are enum reordering breaking tooling and missing increments in new paths. Test read/write/direct/commit/readdir/workload stats and proc output compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs_iostat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs_page.h -->
# sources/distributed-fs/ceph-client/include/linux/nfs_page.h

Purpose: Declares NFS page request and pageio batching infrastructure for read/write aggregation, mirrors, commit grouping, and async request lifecycle.

Important APIs, types, and functions: Important types are `struct nfs_page`, `struct nfs_pageio_ops`, `struct nfs_rw_ops`, `struct nfs_pgio_mirror`, and `struct nfs_pageio_descriptor`. APIs create requests from pages/folios, initialize descriptors, add/complete/resend requests, test aggregation, join/lock/unlock page groups, wait on async counters, and access request folios/pages/inodes/offsets. Detected source surface: 286 lines; includes `linux/kref.h`, `linux/list.h`, `linux/nfs_xdr.h`, `linux/pagemap.h`, `linux/sunrpc/auth.h`, `linux/wait.h`; macros `NFS_PAGEIO_DESCRIPTOR_MIRROR_MAX`, `_LINUX_NFS_PAGE_H`; structs `folio`, `inode`, `kref`, `list_head`, `nfs_commit_info`, `nfs_direct_req`, `nfs_inode`, `nfs_io_completion`, `nfs_lock_context`, `nfs_page`, `nfs_pageio_descriptor`, `nfs_pageio_ops`, `nfs_pgio_header`, `nfs_pgio_mirror`, `nfs_rw_ops`, `nfs_write_verifier`, `page`, `pnfs_layout_segment`, and 1 more; enums none; typedefs none; function-like declarations/helpers `folio_page`, `folio_size`, `int`, `list_entry`, `nfs_async_iocounter_wait`, `nfs_generic_pg_test`, `nfs_join_page_group`, `nfs_list_add_request`, `nfs_list_entry`, `nfs_list_move_request`, `nfs_list_remove_request`, `nfs_lock_request`, `nfs_page_clear_headlock`, `nfs_page_group_lock`, `nfs_page_group_sync_on_bit`, `nfs_page_group_sync_on_bit_locked`, `nfs_page_group_unlock`, `nfs_page_max_length`, and 11 more.

Control flow: Buffered read/write paths create `nfs_page` requests, group compatible ranges, aggregate them into pageio descriptors and mirrors, issue RPC headers through rw ops, and complete or resend failed groups.

State and persistence behavior: Request state includes list membership, page/folio reference, open and lock contexts, offsets/counts, wb flags, refcount, and group head relationships. Descriptor state persists during batching and mirrors pNFS layouts.

Dependencies and integration points: Depends on lists, pagemap, waits, SUNRPC auth, NFS XDR, krefs, open contexts, and pNFS/RPC completion paths.

Risks and test signals: Risks are request refcount leaks, page group lock deadlocks, incorrect coalescing across credentials/locks/layouts, and resend loops. Test writeback batching, pNFS mirrors, O_DIRECT interaction, folio sizes, and error cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs_page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs_ssc.h -->
# sources/distributed-fs/ceph-client/include/linux/nfs_ssc.h

Purpose: Declares NFS server-side copy client operation registration used for NFSv4.2 inter-server/server-side copy coordination.

Important APIs, types, and functions: Exports global `nfs_ssc_client_tbl`, `struct nfs4_ssc_client_ops`, `struct nfs_ssc_client_ops`, `struct nfs_ssc_client_ops_tbl`, register/unregister helpers for NFSv4.2 SSC, inline open/close wrappers, `struct nfsd4_ssc_umount_item`, and generic SSC registration APIs. Detected source surface: 81 lines; includes `linux/nfs_fs.h`, `linux/sunrpc/svc.h`; macros none; structs `file`, `list_head`, `nfs4_ssc_client_ops`, `nfs_fh`, `nfs_ssc_client_ops`, `nfs_ssc_client_ops_tbl`, `nfsd4_ssc_umount_item`, `vfsmount`; enums none; typedefs none; function-like declarations/helpers `ERR_PTR`, `nfs42_ssc_close`, `nfs42_ssc_register`, `nfs42_ssc_register_ops`, `nfs42_ssc_unregister`, `nfs42_ssc_unregister_ops`, `nfs_do_sb_deactive`, `nfs_ssc_register`, `nfs_ssc_unregister`.

Control flow: The NFS server copy path registers client ops, opens a source file on a mounted source server, performs copy work, closes it, and defers superblock deactivation through umount list items when needed.

State and persistence behavior: Global ops tables persist while modules are registered. Umount items and opened files persist for copy operation lifetime.

Dependencies and integration points: Depends on NFS client fs headers, SUNRPC server types, vfsmount/superblock state, and NFSv4.2 copy implementation.

Risks and test signals: Risks are ops-table races, leaked mounts/files, and cleanup ordering during module unload. Test copy registration/unregistration, inter-server copy success/failure, and umount while copy state exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs_ssc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs_xdr.h -->
# sources/distributed-fs/ceph-client/include/linux/nfs_xdr.h

Purpose: Defines the central NFS XDR data model: protocol attribute containers, fsinfo/fsstat/pathconf, NFSv4 sequence/session and pNFS structures, operation argument/result packets for NFSv2/v3/v4/v4.2, pageio/commit headers, unlink/rename async data, and the `nfs_rpc_ops` operation vector.

Important APIs, types, and functions: Key exports include `struct nfs_fattr`, `struct nfs_fsinfo`, `struct nfs4_sequence_args/res`, layoutget/commit/return/stat/error/clone data, open/close/lock/read/write/commit/remove/rename args and results, ACL/xattr args, NFSv3 operation structs, pNFS commit data, `struct nfs_pgio_header`, `struct nfs_commit_data`, completion op vectors, `struct nfs_rpc_ops`, `encode_opaque_fixed()`, and `decode_opaque_fixed()`. Detected source surface: 1896 lines; includes `linux/nfsacl.h`, `linux/sunrpc/gss_api.h`; macros `MAX_BIND_CONN_TO_SESSION_RETRIES`, `NFS42_LAYOUTERROR_MAX`, `NFS4_ACL_TRUNC`, `NFS4_FS_LOCATIONS_MAXENTRIES`, `NFS4_FS_LOCATION_MAXSERVERS`, `NFS4_PATHNAME_MAXCOMPONENTS`, `NFS_ATTR_FATTR`, `NFS_ATTR_FATTR_ATIME`, `NFS_ATTR_FATTR_BLOCKS_USED`, `NFS_ATTR_FATTR_BTIME`, `NFS_ATTR_FATTR_CHANGE`, `NFS_ATTR_FATTR_CTIME`, `NFS_ATTR_FATTR_FILEID`, `NFS_ATTR_FATTR_FSID`, `NFS_ATTR_FATTR_GROUP`, `NFS_ATTR_FATTR_GROUP_NAME`, `NFS_ATTR_FATTR_MODE`, `NFS_ATTR_FATTR_MOUNTED_ON_FILEID`, and 31 more; structs `dentry`, `file_lock`, `folio`, `fs_context`, `iattr`, `inode`, `list_head`, `nfs2_fsstat`, `nfs3_accessargs`, `nfs3_accessres`, `nfs3_createargs`, `nfs3_diropargs`, `nfs3_diropres`, `nfs3_getaclargs`, `nfs3_getaclres`, `nfs3_linkargs`, `nfs3_linkres`, `nfs3_mkdirargs`, and 219 more; enums `createmode4`, `nfs3_createmode`, `nfs3_ftype`, `nfs3_stable_how`, `nfs4_acl_type`, `nfs4_change_attr_type`, `nfs_opnum4`, `open_claim_type4`; typedefs `clientid4`, `void`; function-like declarations/helpers `decode_opaque_fixed`, `encode_opaque_fixed`, `nfs_fsid_equal`, `void`.

Control flow: NFS client code fills an args struct, XDR encoders serialize it into SUNRPC calls, decoders populate result/fattr structures, RPC completion code updates inode/pageio/commit state, and version-specific `nfs_rpc_ops` route VFS operations to the correct protocol implementation.

State and persistence behavior: Most structs are transient RPC state, but they carry persistent protocol identities: file handles, stateids, client IDs, sequence slots, write verifiers, layout state, change attributes, and commit lists. Pageio and commit headers persist while asynchronous RPC tasks are outstanding.

Dependencies and integration points: Depends on NFS ACL, GSS/SUNRPC, NFSv4 constants, pages/folios, credentials, file locks, pNFS layout drivers, and VFS state. It is the protocol glue between NFS filesystem logic and SUNRPC.

Risks and test signals: Risks are XDR size mismatches, missing bitmask fields, stateid/sequence misuse, page vector lifetime, pNFS error propagation, and version-specific operation divergence. Test NFSv2/v3/v4 mounts, open/close/lock, read/write/commit, readdirplus, ACLs, pNFS layouts, NFSv4.2 copy/seek/xattrs, and fault-injected RPC errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfs_xdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfsacl.h -->
# sources/distributed-fs/ceph-client/include/linux/nfsacl.h

Purpose: Declares NFS ACL buffer sizing and XDR encode/decode helpers for POSIX ACL transport.

Important APIs, types, and functions: Exports ACL entry/page sizing constants, `nfsacl_size()`, `nfsacl_encode()`, `nfsacl_decode()`, and ACL validity helpers. Detected source surface: 48 lines; includes `linux/posix_acl.h`, `linux/sunrpc/xdr.h`, `uapi/linux/nfsacl.h`; macros `NFSACL_MAXPAGES`, `NFSACL_MAXWORDS`, `NFS_ACL_INLINE_BUFSIZE`, `NFS_ACL_MAX_ENTRIES`, `NFS_ACL_MAX_ENTRIES_INLINE`, `__LINUX_NFSACL_H`; structs `posix_acl`; enums none; typedefs none; function-like declarations/helpers `nfs_stream_decode_acl`, `nfs_stream_encode_acl`, `nfsacl_decode`, `nfsacl_encode`, `nfsacl_size`.

Control flow: NFS ACL RPC paths size buffers, encode POSIX ACL entries into XDR words, decode replies back to kernel ACLs, and validate ACL masks.

State and persistence behavior: No global state is owned; ACL objects and pages are caller-owned transient RPC data.

Dependencies and integration points: Depends on POSIX ACL, SUNRPC XDR, and UAPI NFS ACL constants.

Risks and test signals: Risks are entry-count overflow, inline buffer under-sizing, and invalid ACL acceptance. Test max-entry ACLs, default/access ACL pairs, malformed XDR, and permission enforcement after set/get ACL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfsacl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfslocalio.h -->
# sources/distributed-fs/ceph-client/include/linux/nfslocalio.h

Purpose: Declares NFS localio support that lets an NFS client use local nfsd file access when the server is on the same host and UUID/auth checks permit it.

Important APIs, types, and functions: Exports localio UUID/list/client helpers, registration structures, enable/disable paths, and wrappers linking NFS client state to nfsd file handles and local credentials. Detected source surface: 123 lines; includes `linux/list.h`, `linux/module.h`, `linux/nfs.h`, `linux/sunrpc/clnt.h`, `linux/sunrpc/svcauth.h`, `linux/uuid.h`, `net/net_namespace.h`; macros `__LINUX_NFSLOCALIO_H`; structs `auth_domain`, `file`, `list_head`, `net`, `nfs_client`, `nfs_file_localio`, `nfsd_file`, `nfsd_localio_operations`, `rpc_clnt`; enums none; typedefs none; function-like declarations/helpers `nfs_close_local_fh`, `nfs_localio_disable_client`, `nfs_localio_enable_client`, `nfs_localio_invalidate_clients`, `nfs_to_nfsd_file_put_local`, `nfs_to_nfsd_net_put`, `nfs_uuid_begin`, `nfs_uuid_end`, `nfs_uuid_init`, `nfs_uuid_is_local`, `nfsd_localio_ops_init`.

Control flow: Client/server localio code exchanges or checks a UUID, determines whether a mount is local, opens local nfsd files for read/write shortcuts, and falls back to normal RPC when local access is unavailable.

State and persistence behavior: State includes per-client UUID pointers, registered localio clients, nfsd file references in `struct nfs_file_localio`, and net namespace scoped lookup data.

Dependencies and integration points: Depends on module/list/uuid, SUNRPC client and server auth, NFS base types, net namespaces, and NFS fs/sb integration.

Risks and test signals: Risks are auth bypass, stale nfsd file references, namespace confusion, and fallback inconsistency. Test local and remote mounts, UUID mismatch, permission changes, server restart, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nfslocalio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nitro_enclaves.h -->
# sources/distributed-fs/ceph-client/include/linux/nitro_enclaves.h

Purpose: Kernel wrapper for AWS Nitro Enclaves UAPI definitions.

Important APIs, types, and functions: Includes `uapi/linux/nitro_enclaves.h` and provides the kernel include guard. Detected source surface: 11 lines; includes `uapi/linux/nitro_enclaves.h`; macros `_LINUX_NITRO_ENCLAVES_H_`; structs none; enums none; typedefs none; function-like declarations/helpers none.

Control flow: There is no executable flow in this header; driver and userspace ABI code consume the UAPI definitions.

State and persistence behavior: No state is defined here.

Dependencies and integration points: Depends entirely on Nitro Enclaves UAPI ioctl and structure definitions.

Risks and test signals: Risks are ABI drift between kernel wrapper and UAPI. Test by building enclave driver users and exercising ioctl compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nitro_enclaves.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nl802154.h -->
# sources/distributed-fs/ceph-client/include/linux/nl802154.h

Purpose: Defines legacy IEEE 802.15.4 netlink names, multicast groups, attributes, commands, and policy declaration.

Important APIs, types, and functions: Exports family/group names, attribute enum with `IEEE802154_ATTR_MAX`, `ieee802154_policy[]`, command enum with `IEEE802154_CMD_MAX`, and event/group constants. Detected source surface: 173 lines; includes `net/netlink.h`; macros `IEEE802154_ATTR_MAX`, `IEEE802154_CMD_MAX`, `IEEE802154_MCAST_BEACON_NAME`, `IEEE802154_MCAST_COORD_NAME`, `IEEE802154_NL_NAME`, `NL802154_H`; structs none; enums none; typedefs none; function-like declarations/helpers none.

Control flow: IEEE 802.15.4 MAC netlink handlers validate attributes against the policy, dispatch commands such as association, scan, beacon, and device operations, and multicast coordinator/beacon events.

State and persistence behavior: The header defines numeric netlink ABI only; runtime state is in MAC device and netlink family implementations.

Dependencies and integration points: Depends on netlink attribute policy types and integrates with IEEE 802.15.4 subsystem control paths.

Risks and test signals: Risks are ABI renumbering, missing policy validation, and multicast group mismatch. Test netlink command parsing, invalid attributes, scan/associate flows, and event listeners.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nl802154.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nls.h -->
# sources/distributed-fs/ceph-client/include/linux/nls.h

Purpose: Declares the kernel native language support charset table interface and Unicode conversion helpers.

Important APIs, types, and functions: Key types are `wchar_t`, `unicode_t`, `struct nls_table`, and `enum utf16_endian`. APIs register/unregister/load/unload NLS tables, load default charset, convert UTF-8/UTF-16/UTF-32, and case-fold or compare strings through table callbacks. Detected source surface: 109 lines; includes `linux/init.h`; macros `MAX_WCHAR_T`, `MODULE_ALIAS_NLS`, `NLS_MAX_CHARSET_SIZE`, `_LINUX_NLS_H`, `register_nls`; structs `module`, `nls_table`; enums `utf16_endian`; typedefs `unicode_t`, `wchar_t`; function-like declarations/helpers `__register_nls`, `nls_nullsize`, `nls_strnicmp`, `nls_tolower`, `nls_toupper`, `unload_nls`, `unregister_nls`, `utf16s_to_utf8s`, `utf32_to_utf8`, `utf8_to_utf32`, `utf8s_to_utf16s`.

Control flow: Filesystems load an NLS table by charset name, call character conversion and case maps while parsing names, and unload the table when no longer needed.

State and persistence behavior: Registered charset tables are module-backed global state; loaded table references persist for filesystem mount lifetime.

Dependencies and integration points: Depends on init/module support and character conversion implementations. Used by FAT, ISO9660, CIFS, and other filename-encoding consumers.

Risks and test signals: Risks are module reference leaks, invalid multibyte handling, and case-fold mismatches. Test charset load/unload, invalid UTF sequences, UTF-16 endian variants, and case-insensitive lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nmi.h -->
# sources/distributed-fs/ceph-client/include/linux/nmi.h

Purpose: Declares lockup detector, hardlockup/NMI watchdog, softlockup touch, CPU backtrace, perf NMI, and stall-check interfaces with configuration-dependent stubs.

Important APIs, types, and functions: Exports watchdog globals, lockup detector init/reconfigure/cpu hotplug APIs, softlockup touch/reset helpers, hardlockup perf controls, NMI watchdog touch/check/start/stop/probe/enable/disable, backtrace trigger helpers, `nmi_trigger_cpumask_backtrace()`, `nmi_cpu_backtrace()`, sample-period helpers, and stall snapshot/check APIs. Detected source surface: 233 lines; includes `asm/irq.h`, `asm/nmi.h`, `linux/sched.h`; macros `LINUX_NMI_H`, `WATCHDOG_HARDLOCKUP_ENABLED`, `WATCHDOG_HARDLOCKUP_ENABLED_BIT`, `WATCHDOG_SOFTOCKUP_ENABLED`, `WATCHDOG_SOFTOCKUP_ENABLED_BIT`, `lockup_detector_offline_cpu`, `lockup_detector_online_cpu`, `sysctl_hardlockup_all_cpu_backtrace`, `sysctl_softlockup_all_cpu_backtrace`; structs none; enums none; typedefs none; function-like declarations/helpers `arch_perf_nmi_is_available`, `arch_touch_nmi_watchdog`, `hardlockup_config_perf_event`, `hardlockup_detector_disable`, `hardlockup_detector_perf_adjust_period`, `hardlockup_detector_perf_restart`, `hardlockup_detector_perf_stop`, `hw_nmi_get_sample_period`, `lockup_detector_init`, `lockup_detector_offline_cpu`, `lockup_detector_online_cpu`, `lockup_detector_reconfigure`, `lockup_detector_retry_init`, `lockup_detector_soft_poweroff`, `nmi_backtrace_stall_check`, `nmi_backtrace_stall_snap`, `nmi_cpu_backtrace`, `nmi_trigger_cpumask_backtrace`, and 19 more.

Control flow: Scheduler/timer/perf/NMI paths periodically touch watchdog state; lockup detectors compare progress and trigger warnings, panics, or CPU backtraces when thresholds are exceeded.

State and persistence behavior: Global watchdog enable bits, thresholds, panic flags, CPU masks, perf event configuration, and per-CPU watchdog state live in implementation files. This header exposes controls and stubs.

Dependencies and integration points: Depends on scheduler, IRQ/NMI architecture hooks, cpumasks, perf, and CPU hotplug. Used by kernel watchdog, panic diagnostics, and architecture NMI code.

Risks and test signals: Risks are false positives during long IRQ/NMI-off regions, missing watchdog touches, backtrace deadlocks, and config stub divergence. Test CPU hotplug, watchdog sysctls, induced soft/hard lockups, all-CPU backtrace, and perf NMI availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/node.h -->
# sources/distributed-fs/ceph-client/include/linux/node.h

Purpose: Declares NUMA node device model integration, node cache/performance attributes, memory hotplug registration, node notifiers, and CPU/memory node registration APIs.

Important APIs, types, and functions: Key types are `struct access_coordinate`, coordinate/cache enums, `struct node_cache_attrs`, `struct node`, and `struct node_notify`. APIs add cache/perf attributes, register memory blocks under nodes, register node notifiers, initialize node devices, register/unregister nodes, attach CPUs/memory, and map `device` to `node`. Detected source surface: 213 lines; includes `linux/device.h`, `linux/list.h`; macros `NODE_ADDED_FIRST_MEMORY`, `NODE_ADDING_FIRST_MEMORY`, `NODE_CANCEL_ADDING_FIRST_MEMORY`, `NODE_CANCEL_REMOVING_LAST_MEMORY`, `NODE_REMOVED_LAST_MEMORY`, `NODE_REMOVING_LAST_MEMORY`, `_LINUX_NODE_H_`, `hotplug_node_notifier`, `to_node`; structs `access_coordinate`, `device`, `list_head`, `memory_block`, `node`, `node_cache_attrs`, `node_notify`; enums `access_coordinate_class`, `cache_indexing`, `cache_mode`, `cache_write_policy`; typedefs none; function-like declarations/helpers `hotplug_node_notifier`, `node_add_cache`, `node_dev_init`, `node_notify`, `node_set_perf_attrs`, `node_update_perf_attrs`, `register_cpu_under_node`, `register_memory_blocks_under_node_hotplug`, `register_memory_blocks_under_nodes`, `register_memory_node_under_compute_node`, `register_node`, `register_node_notifier`, `unregister_cpu_under_node`, `unregister_memory_block_under_nodes`, `unregister_node`, `unregister_node_notifier`.

Control flow: Boot and hotplug code register node devices, attach CPUs and memory blocks, publish cache/performance attributes, and notify listeners when first/last memory is added or removed.

State and persistence behavior: Global `node_devices[]` and sysfs device state persist for each NUMA node. Cache/perf attributes and hotplug notifier state are runtime system topology state.

Dependencies and integration points: Depends on device model, lists, memory block hotplug, notifier blocks, and NUMA configuration. Used by memory, CPU, sysfs, and topology code.

Risks and test signals: Risks are stale sysfs topology after hotplug, missing notifier rollback, and invalid node IDs. Test node registration, memory add/remove, CPU online/offline, cache attribute publishing, and non-NUMA stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/node.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nodemask.h -->
# sources/distributed-fs/ceph-client/include/linux/nodemask.h

Purpose: Provides the core NUMA nodemask API: bit operations, parsing/printing, remapping/folding, node-state masks, iteration macros, online/possible/memory node helpers, and scratch allocation.

Important APIs, types, and functions: Important exports are `node_set/clear/isset`, `nodes_and/or/xor/andnot/copy/complement`, equality/subset/intersection/empty/full/weight, first/next node helpers, `nodemask_of_node()`, parse helpers, remap/onto/fold helpers, `enum node_states`, `node_states[]`, online/possible macros, and `NODEMASK_ALLOC`/scratch helpers. Detected source surface: 540 lines; includes `linux/bitmap.h`, `linux/minmax.h`, `linux/nodemask_types.h`, `linux/random.h`, `linux/threads.h`; macros `NODEMASK_ALLOC`, `NODEMASK_FREE`, `NODEMASK_SCRATCH`, `NODEMASK_SCRATCH_FREE`, `NODE_MASK_ALL`, `NODE_MASK_LAST_WORD`, `NODE_MASK_NONE`, `__LINUX_NODEMASK_H`, `first_memory_node`, `first_node`, `first_online_node`, `first_unset_node`, `for_each_node`, `for_each_node_mask`, `for_each_node_state`, `for_each_node_with_cpus`, `for_each_online_node`, `next_memory_node`, and 40 more; structs `nodemask_scratch`; enums `node_states`; typedefs none; function-like declarations/helpers `__first_node`, `__first_unset_node`, `__next_node`, `__next_node_in`, `__node_clear`, `__node_remap`, `__node_set`, `__node_test_and_set`, `__nodelist_parse`, `__nodemask_parse_user`, `__nodemask_pr_numnodes`, `__nodes_and`, `__nodes_andnot`, `__nodes_clear`, `__nodes_complement`, `__nodes_copy`, `__nodes_empty`, `__nodes_equal`, and 36 more.

Control flow: Callers manipulate `nodemask_t` bitmaps at compile-time inline speed, iterate possible/online nodes, parse user masks, and update node state masks during topology changes.

State and persistence behavior: For NUMA builds, `node_states[]`, `nr_node_ids`, and `nr_online_nodes` are global topology state. Non-NUMA builds collapse helpers to single-node constants.

Dependencies and integration points: Depends on threads, bitmap, minmax, nodemask types, and random helpers. Used by scheduler, memory policy, cpusets, NUMA balancing, and hotplug code.

Risks and test signals: Risks are out-of-range node indexes, non-NUMA stub assumptions, parser accepting invalid masks, and node state races. Test mask operations, user parsers, memoryless nodes, hotplug state transitions, and large `MAX_NUMNODES` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nodemask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nodemask_types.h -->
# sources/distributed-fs/ceph-client/include/linux/nodemask_types.h

Purpose: Defines the fundamental NUMA nodemask storage type and node-count constants.

Important APIs, types, and functions: Exports `NODES_SHIFT`, `MAX_NUMNODES`, `NUMA_NO_NODE`, and `nodemask_t` as a bitmap of `MAX_NUMNODES` bits. Detected source surface: 19 lines; includes `linux/bitops.h`; macros `MAX_NUMNODES`, `NODES_SHIFT`, `NUMA_NO_NODE`, `__LINUX_NODEMASK_TYPES_H`; structs none; enums none; typedefs `DECLARE_BITMAP`; function-like declarations/helpers none.

Control flow: No runtime flow; other headers inline bitmap operations over this storage type.

State and persistence behavior: `nodemask_t` instances store caller-owned node sets. The header owns no global state.

Dependencies and integration points: Depends on bitops and `CONFIG_NODES_SHIFT` for NUMA sizing.

Risks and test signals: Risks are insufficient node bit width for platform topology and stack pressure from large nodemask allocations. Test NUMA and non-NUMA builds plus large-node configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nodemask_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nospec.h -->
# sources/distributed-fs/ceph-client/include/linux/nospec.h

Purpose: Declares speculation barrier helpers for array-index masking and task speculation-control plumbing.

Important APIs, types, and functions: Exports `array_index_mask_nospec()`, `array_index_nospec()`, `arch_prctl_spec_ctrl_get()`, `arch_prctl_spec_ctrl_set()`, and `arch_seccomp_spec_mitigate()`. Detected source surface: 74 lines; includes `asm/barrier.h`, `linux/compiler.h`; macros `_LINUX_NOSPEC_H`, `array_index_nospec`, `barrier_nospec`; structs `task_struct`; enums none; typedefs none; function-like declarations/helpers `arch_prctl_spec_ctrl_get`, `arch_prctl_spec_ctrl_set`, `arch_seccomp_spec_mitigate`, `array_index_mask_nospec`.

Control flow: Callers pass an index and size through `array_index_nospec()` after bounds checks; the helper masks out-of-range indexes under speculative execution and emits architecture barriers through included asm support.

State and persistence behavior: No local state is defined. Speculation control state is task/architecture state managed by implementation files.

Dependencies and integration points: Depends on compiler annotations and architecture barrier primitives. Used by syscall, BPF, array lookup, and seccomp/speculation mitigation code.

Risks and test signals: Risks are using the helper before a real bounds check, wrong integer types causing truncation, and arch stub weakness. Test with static analysis for Spectre-v1 patterns, bounds-check call sites, and architecture mitigation selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nospec.h -->
