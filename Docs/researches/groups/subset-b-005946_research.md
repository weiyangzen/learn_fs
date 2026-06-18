# Research: subset-b-005946

This grouped report covers the exact source files assigned to `subset-b-005946`.
Each section is wrapped with reconciliation markers for deterministic splitting
into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_flow_table.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_flow_table.h

Purpose: Defines the kernel-side flowtable offload model used by netfilter/nftables to accelerate established conntrack flows in software, hardware, XDP, TC, and route-direct transmit paths.

Important APIs/types/functions: `struct nf_flowtable`, `nf_flowtable_type`, `flow_offload`, `flow_offload_tuple`, `nf_flow_route`, and `nf_flow_rule` are the core data carriers. Exported operations include `flow_offload_alloc/free`, `flow_offload_add/refresh/lookup`, `nf_flow_table_init/free`, GC cleanup helpers, NAT port rewrite helpers, IPv4/IPv6 hook functions, offload add/del/stats/flush/setup, route rule builders, and optional BPF registration. Inline callback management uses `flow_block_cb_lookup/alloc/free` under `flow_block_lock`.

Control flow: conntrack creates a `flow_offload`; routing fills bidirectional `nf_flow_route`; the flow is added to the rhashtable; packet hooks look up tuples and transmit through neighbor, direct, XFRM, TC, or offload paths; GC tears down stale, closing, or device-removed flows. Hardware callbacks are registered per device and retain flowtable references through type `get/put`.

State and persistence: State is in rhashtable tuples, conntrack references, timeout jiffies, flow flags, per-net flow table stats, delayed GC work, flow block callbacks, and optional hardware state bits. It is runtime only and must be cleaned on device teardown and namespace exit.

Dependencies/integration: Depends on conntrack tuple directions, `flow_offload.h`, dst cache, PPPoE parsing, rhashtable, netdevice lifecycle, nftables flowtables, BPF/BTF, procfs stats, and flow block offload callbacks.

Risks/test signals: Validate tuple hash-key boundaries around `__hash`, bidirectional NAT flags, PPPoE `pskb_may_pull`, stale dst cookies, refcount symmetry in offload callbacks, device unregister cleanup, GC races, and hardware offload failure fallback. Tests should exercise IPv4/IPv6 flowtable rules, NAT offload, device removal, module unload, proc stats, and offload callback duplicate registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_flow_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_hooks_lwtunnel.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_hooks_lwtunnel.h

Purpose: Declares the sysctl handler that controls lightweight-tunnel netfilter hook behavior when `CONFIG_SYSCTL` is enabled.

Important APIs/types/functions: The only exported contract is `nf_hooks_lwtunnel_sysctl_handler(const struct ctl_table *table, int write, void *buffer, size_t *lenp, loff_t *ppos)`.

Control flow: The handler is called by sysctl read/write dispatch for the corresponding lwtunnel netfilter knob. This header does not implement policy; it exposes the hook point to sysctl table definitions.

State and persistence: Persistent state lives in the sysctl backing variable owned by implementation code, not in this header. The handler must interpret user buffers and update that state consistently.

Dependencies/integration: Depends on `linux/sysctl.h` and `linux/types.h`; integrates with sysctl registration and lwtunnel/netfilter code.

Risks/test signals: Main risks are missing declaration under configuration combinations and incorrect write validation in the implementation. Test with `CONFIG_SYSCTL=y` and disabled variants, sysctl read/write permissions, invalid lengths, and namespace or global scope expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_hooks_lwtunnel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_log.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_log.h

Purpose: Provides the internal netfilter logging backend registry and packet logging interface used by LOG, ULOG/NFLOG, nft trace, and protocol-family-specific logger modules.

Important APIs/types/functions: `nf_loginfo` describes LOG or ULOG parameters; `nf_logfn` is the backend callback signature; `nf_logger` names a logger, type, module owner, and callback. APIs include `nf_log_register/unregister`, `nf_log_is_registered`, `nf_log_set/unset`, `nf_log_bind_pf/unbind_pf`, `nf_logger_find_get/put`, `nf_log_packet`, `nf_log_trace`, and buffered formatting helpers `nf_log_buf_open/add/close`.

Control flow: Backend modules register loggers by protocol family and type. Rules or tracing code call `nf_log_packet`/`nf_log_trace`; the core chooses the per-net/per-family logger and invokes `logfn` with skb, hook, devices, loginfo, and prefix.

State and persistence: Logger bindings are runtime kernel/module state, partly per-net and partly global. `sysctl_nf_log_all_netns` controls LOG target allowance in all namespaces. Module refcounts protect active loggers.

Dependencies/integration: Depends on netfilter core, skbuff/device context, module ownership, sysctl, and uapi `nf_log.h`; integrates with iptables/nftables logging targets and trace notifications.

Risks/test signals: Check module ref leaks, missing logger fallback, format string paths, per-net binding isolation, and behavior when loggers unregister during packet processing. Test LOG/NFLOG for IPv4, IPv6, bridge, namespace isolation, trace output, and `NF_LOG_F_COPY_LEN` handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_nat.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_nat.h

Purpose: Defines NAT manipulation types, conntrack NAT extension state, NAT hook registration, packet translation, checksum repair, and common IPv4/IPv6/inet NAT entry points.

Important APIs/types/functions: `enum nf_nat_manip_type`, `HOOK2MANIP`, `union nf_conntrack_nat_help`, and `struct nf_conn_nat` define state. Public APIs include `nf_nat_setup_info`, `nf_nat_alloc_null_binding`, `nf_ct_nat_ext_add`, `nfct_nat`, `nf_nat_oif_changed`, `nf_nat_register_fn/unregister_fn`, `nf_nat_packet`, `nf_nat_manip_pkt`, checksum and ICMP reply translation helpers, family-specific register/unregister functions, `nf_nat_inet_fn`, `nf_ct_nat`, and `nf_nat_initialized`.

Control flow: NAT rules allocate or find the conntrack NAT extension, set up source or destination ranges, and then packet hooks call `nf_nat_packet`/`nf_nat_manip_pkt` according to hook direction. ICMP errors use reply translation helpers to rewrite embedded packets.

State and persistence: NAT state is stored per conntrack in `NF_CT_EXT_NAT`, with optional PPTP helper data and masquerade interface index. It persists for the conntrack lifetime, not beyond runtime.

Dependencies/integration: Depends on conntrack core/extensions/tuples, uapi NAT ranges, netfilter hook registration, IPv4/IPv6 hooks, masquerade, and helpers such as PPTP.

Risks/test signals: Watch hook-to-manip mapping, status-bit initialization, checksum recalculation after payload rewrite, masquerade egress interface changes, extension allocation failures, and ICMP embedded translation. Test SNAT, DNAT, redirect, masquerade, helper-assisted protocols, namespace teardown, and IPv4/IPv6 parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_nat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_nat_helper.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_nat_helper.h

Purpose: Exposes helper routines for NAT-aware application protocol helpers that must rewrite payloads and coordinate expected related connections.

Important APIs/types/functions: `__nf_nat_mangle_tcp_packet` is the base TCP payload mangle primitive with optional sequence adjustment; `nf_nat_mangle_tcp_packet` wraps it with adjustment enabled. UDP payload rewriting is provided by `nf_nat_mangle_udp_packet`. Related-connection setup is handled by `nf_nat_follow_master`, and port selection for expectations by `nf_nat_exp_find_port`.

Control flow: A conntrack helper identifies protocol control payload offsets, invokes the TCP or UDP mangle routine with replacement bytes, and sequence/length adjustments are applied when needed. Expected conntracks inherit NAT from the master via `nf_nat_follow_master`.

State and persistence: State lives in conntrack, expectations, and sequence-adjust extension data. This header stores no state itself.

Dependencies/integration: Depends on skbuff mutability, conntrack, expectations, NAT extension state, and helper-specific parsers such as FTP, SIP, or PPTP.

Risks/test signals: Payload rewrites can fail on non-linear skbs, invalid offsets, insufficient tailroom, or sequence adjustment mistakes. Test helpers with TCP segmentation, UDP checksum changes, expectation port conflicts, NAT follow-master behavior, and malformed control payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_nat_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_nat_masquerade.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_nat_masquerade.h

Purpose: Declares masquerade NAT entry points that derive source addresses from the outgoing interface and clean up flows when interface addressing changes.

Important APIs/types/functions: `nf_nat_masquerade_ipv4`, `nf_nat_masquerade_ipv6`, `nf_nat_masquerade_inet_register_notifiers`, and `nf_nat_masquerade_inet_unregister_notifiers`.

Control flow: NAT rules call the IPv4 or IPv6 masquerade helper with the skb, NAT range, and output device. Notifiers register to observe address/device events that invalidate masqueraded conntracks.

State and persistence: Per-conntrack masquerade state is held through `nf_conn_nat.masq_index` in `nf_nat.h`; notifier registration is process-global runtime state.

Dependencies/integration: Depends on NAT range definitions, netdevice lifetime, IPv4/IPv6 address selection, conntrack cleanup, and notifier chains.

Risks/test signals: Risks include stale conntracks after address changes, wrong output interface index, missing notifier registration, and IPv6 parity. Test interface down/up, address replacement, namespace teardown, multiple egress devices, and rule unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_nat_masquerade.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_nat_redirect.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_nat_redirect.h

Purpose: Declares redirect NAT helpers for translating traffic to local addresses in IPv4 and IPv6.

Important APIs/types/functions: `nf_nat_redirect_ipv4(struct sk_buff *skb, const struct nf_nat_range2 *range, unsigned int hooknum)` and `nf_nat_redirect_ipv6(struct sk_buff *skb, const struct nf_nat_range2 *range, unsigned int hooknum)`.

Control flow: REDIRECT rules pass packet context and the user range to these helpers; implementations choose the local target address based on hook and family and then delegate to NAT setup/manipulation.

State and persistence: Redirect state is per conntrack through the normal NAT extension. No independent persistent state is declared here.

Dependencies/integration: Depends on skbuffs, uapi NAT ranges, IPv4/IPv6 local address selection, and core NAT setup.

Risks/test signals: Test local output vs prerouting hook behavior, loopback/local address selection, port range handling, IPv6 enabled/disabled builds, and interaction with conntrack zones.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_nat_redirect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_queue.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_queue.h

Purpose: Defines the packet queueing interface used to hand netfilter packets to userspace queue handlers such as nfnetlink_queue and later reinject or drop them.

Important APIs/types/functions: `struct nf_queue_entry` stores skb, hook state, hook index, queue id, bridge physical devices, conntrack-unconfirmed flag, and reroute storage. `struct nf_queue_handler` exposes `outfn` and `nf_hook_drop`. APIs include `nf_register_queue_handler`, `nf_unregister_queue_handler`, `nf_queue_entry_get_refs`, `nf_queue_entry_free`, `nf_queue`, and hashing helpers `hash_v4`, `hash_v6`, `hash_bridge`, `nfqueue_hash`.

Control flow: A queue verdict creates an entry, saves hook/device/routing context, dispatches it to the registered handler, and later reinjection resumes at `hook_index`. Queue balancing uses symmetric hashes so both directions tend to select the same queue.

State and persistence: Queued entries hold skb and references until userspace verdict or drop. Hash init uses a random nonzero seed. State is transient but can hold resources if userspace stalls.

Dependencies/integration: Depends on netfilter hooks, skbuff, rhashtable node embedding, IPv4/IPv6/bridge headers, jhash, reciprocal scaling, and bridge netfilter optional fields.

Risks/test signals: Risks include reference leaks, stale route keys, malformed bridge headers, queue imbalance, reinject-after-device-destroy races, and unconfirmed conntrack handling. Test queue-balance, bypass/drop behavior, bridge IPv4/IPv6 packets, namespace exit with queued packets, and userspace timeout scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_reject.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_reject.h

Purpose: Provides a shared checksum eligibility helper used by reject implementations before generating reject responses.

Important APIs/types/functions: `nf_reject_verify_csum(struct sk_buff *skb, int dataoff, __u8 proto)` returns whether a packet protocol has a checksum model suitable for normal reject validation.

Control flow: Reject code calls this helper before responding. UDP is accepted only if the UDP header is readable and the checksum field is nonzero; GRE, AH, ESP, SCTP, and UDPLite are rejected because they have optional, partial, or separate integrity semantics.

State and persistence: Stateless inline helper. It reads skb header data through `skb_header_pointer`.

Dependencies/integration: Depends on skbuff header access, protocol constants, UDP header layout, and IPv4/IPv6 reject code using this common filter.

Risks/test signals: Key risk is sending rejects for packets whose integrity was not verified or silently dropping valid edge cases. Test UDP zero-checksum, truncated transport headers, GRE/AH/ESP/SCTP/UDPLite, non-linear skbs, and both nft/iptables reject paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_reject.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_socket.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_socket.h

Purpose: Declares slow socket lookup helpers used by netfilter socket matching and transparent proxy paths.

Important APIs/types/functions: `nf_sk_lookup_slow_v4(struct net *net, const struct sk_buff *skb, const struct net_device *indev)` and `nf_sk_lookup_slow_v6(...)` return matching sockets for IPv4 or IPv6 packets.

Control flow: Netfilter expressions or matches first try faster skb/socket hints when available, then call these slow lookup helpers to search protocol socket tables using packet tuple and ingress device.

State and persistence: No state is defined here; looked-up sockets are existing kernel socket objects whose references are managed by implementation callers.

Dependencies/integration: Depends on `net/sock.h`, skbuff tuple parsing, network namespace socket tables, ingress device context, nft socket expression, xt socket match, and tproxy.

Risks/test signals: Risks are socket reference leaks, incorrect namespace/device scoping, fragment handling, and transparent socket matching differences. Test IPv4/IPv6 established and listener sockets, wildcard binds, VRF/l3mdev, transparent sockets, and no-socket fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_synproxy.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_synproxy.h

Purpose: Defines shared SYN proxy per-net state, option parsing, cookie handling, and IPv4/IPv6 hook entry points for netfilter SYNPROXY.

Important APIs/types/functions: `synproxy_stats` tracks SYN/cookie/reopen counters; `synproxy_net` stores the template conntrack, per-cpu stats, and IPv4/IPv6 hook refcounts; `synproxy_options` stores MSS, window scale, timestamps, and option flags. APIs include `synproxy_pernet`, `synproxy_parse_options`, `synproxy_init_timestamp_cookie`, client SYNACK send/ACK receive helpers, IPv4/IPv6 hook functions, and family init/fini functions.

Control flow: Hook code intercepts SYNs, parses TCP options, encodes state into SYN cookies/timestamps, sends SYNACKs, validates client ACKs, and then opens/adjusts conntrack state using sequence adjustment.

State and persistence: Runtime per-net state includes a template conntrack, per-cpu stats, and hook refcounts. No on-disk persistence.

Dependencies/integration: Depends on TCP, IPv6 checksum/route helpers, conntrack synproxy extension, sequence adjustment, pernet generic storage, and optional IPv6.

Risks/test signals: Test malformed TCP options, timestamp cookie validation, retransmitted cookies, reopened connections, per-net hook refcounting, IPv6-disabled builds, and stats accuracy under concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_synproxy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_tables.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_tables.h

Purpose: This is the central internal nftables contract. It defines packet metadata, the register VM, expression/set/object/chain/table/flowtable types, generation-mask transaction rules, tracing, garbage collection, and per-net nftables state.

Important APIs/types/functions: Core data types include `nft_pktinfo`, `nft_data`, `nft_regs`, `nft_ctx`, `nft_set`, `nft_set_ops`, `nft_expr_type`, `nft_expr_ops`, `nft_rule`, `nft_rule_blob`, `nft_chain`, `nft_chain_type`, `nft_base_chain`, `nft_table`, `nft_object`, `nft_object_type`, `nft_flowtable`, `nft_traceinfo`, transaction structs, `nft_trans_gc`, and `nftables_pernet`. Important helpers parse/dump data and registers, allocate/destroy expressions and elements, bind/deactivate sets and chains, validate chains and set elements, register expression/object/chain/flowtable types, run `nft_do_chain`, manage generation masks, and queue GC transactions.

Control flow: Netlink control operations build `nft_ctx`, parse attributes, create transaction objects, stage updates in the next generation, validate dependencies/loops, commit by switching generation state and RCU rule blobs, notify userspace, and asynchronously destroy old objects. Datapath hooks fill `nft_pktinfo`, execute compact rule blobs expression by expression, update registers/verdicts, jump/goto chains with bounded stack depth, evaluate sets/objects, and optionally trace.

State and persistence: Rulesets are runtime per-net state in `nftables_pernet`: table lists, commit/destroy/set/binding/module/notify lists, commit mutex, handles, timestamp, GC sequence, validation state, and destroy work. Tables own chains, sets, objects, and flowtables. Objects use two-bit generation masks for atomic readers. Rule blobs and set elements are RCU-managed; sets track refs, pending updates, element counts, timeouts, and GC intervals.

Dependencies/integration: Depends on netfilter hooks, nfnetlink/uapi nftables, netlink policy parsing, rhashtable, generic pernet IDs, flow offload, conntrack-facing expressions, modules, RCU, per-cpu stats, and all nft expression backends.

Risks/test signals: High-risk areas are transaction abort/commit symmetry, generation mask correctness, RCU lifetime of blobs/elements, set extension offsets, loop/dependency validation, bound anonymous sets/chains, per-net module references, flowtable hook cleanup, and trace notification reentrancy. Test atomic ruleset replacement, failed batch rollback, concurrent packet evaluation, set timeouts/GC, anonymous set binding, object updates, chain jumps/gotos, netdev ingress hooks, flowtable offload, module unload, and nft monitor trace output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_tables_core.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_tables_core.h

Purpose: Declares built-in nftables core expression and set implementations plus fast-path expression layouts and evaluator entry points.

Important APIs/types/functions: Extern expression types include immediate, cmp, counter, lookup, bitwise, byteorder, payload, dynset, range, meta, rt, exthdr, last, objref, inner, and optional secmark object. Fast private layouts include `nft_bitwise_fast_expr`, `nft_cmp_fast_expr`, `nft_cmp16_fast_expr`, `nft_immediate_expr`, `nft_ct`, and `nft_payload`. It declares built-in set types, lookup dispatchers, core module init/exit, evaluator functions, inner tunnel context, payload inner helpers, object reference evaluation, and `nft_dynset_new`.

Control flow: Core module registration installs common expressions and sets. Datapath evaluation calls the declared `*_eval` functions from expression ops, with optional retpoline mitigation wrappers selecting set lookup implementations.

State and persistence: State is expression-private data embedded in rules and set-private data owned by set implementations. Static keys gate counters and tracing.

Dependencies/integration: Depends on `nf_tables.h`, indirect-call wrappers, conntrack keys, payload/meta uapi keys, and set backend modules.

Risks/test signals: Test fast expression register sizes, payload offsets, retpoline lookup parity, static key enablement, inner tunnel offsets, and module init/exit registration symmetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_tables_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_tables_ipv4.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_tables_ipv4.h

Purpose: Provides IPv4 packet metadata setup and validation helpers for nftables packet evaluation.

Important APIs/types/functions: `nft_set_pktinfo_ipv4`, `__nft_set_pktinfo_ipv4_validate`, `nft_set_pktinfo_ipv4_validate`, and `nft_set_pktinfo_ipv4_ingress`.

Control flow: Base hooks initialize `nft_pktinfo` from `ip_hdr`. Validation paths safely fetch headers, verify IHL/version/total length/header length, set L4 protocol, ethertype, network/transport offsets, and fragment offset. Ingress validation increments IPv4 truncated/header-error stats on malformed packets.

State and persistence: Stateless helper; it mutates only the stack/current packet `nft_pktinfo` and IPv4 stats counters.

Dependencies/integration: Depends on `nf_tables.h`, `net/ip.h`, skbuff header access, `iph_totlen`, `pskb_may_pull`, and IP MIB stats.

Risks/test signals: Test short skbs, invalid IHL/version, total length shorter than header, fragments, ingress stats, non-zero network offsets for inner validation, and behavior falling back to `nft_set_pktinfo_unspec`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_tables_ipv4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_tables_ipv6.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_tables_ipv6.h

Purpose: Provides IPv6 packet metadata setup and validation helpers for nftables, including extension-header traversal.

Important APIs/types/functions: `nft_set_pktinfo_ipv6`, `__nft_set_pktinfo_ipv6_validate`, `nft_set_pktinfo_ipv6_validate`, and `nft_set_pktinfo_ipv6_ingress`.

Control flow: Helpers verify IPv6 version and payload length, then use `ipv6_find_hdr` with auth-header handling to find the transport protocol and offset. Invalid packets reset packet info to unspecified or increment IPv6 truncated/header-error stats in ingress path.

State and persistence: Stateless except for updating `nft_pktinfo` and IPv6 per-interface/per-net stats.

Dependencies/integration: Depends on IPv6 support, `ipv6_payload_len`, `ipv6_find_hdr`, `inet6_dev`, netfilter packet info, and IPv6 MIB counters. Disabled IPv6 builds return failure from validation helpers.

Risks/test signals: Exercise extension header chains, fragments, auth headers, jumbo/truncated payloads, `thoff > U16_MAX`, disabled IPv6 config, ingress stats, and fallback to unspecified packet info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_tables_ipv6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_tables_offload.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_tables_offload.h

Purpose: Defines nftables-to-flow-offload translation structures and helpers for offloading rule matches/actions to flow rules.

Important APIs/types/functions: `nft_offload_reg`, `nft_offload_ctx`, `nft_flow_key`, `nft_flow_match`, and `nft_flow_rule` model dependency tracking, register extraction, dissector keys, masks, and flow actions. APIs include dependency setters, `nft_flow_action_entry_next`, `nft_flow_rule_set_addr_type`, `nft_flow_rule_create/destroy/stats`, `nft_flow_rule_offload_commit`, `nft_chain_offload_support`, and offload init/exit. Macros map nft registers to flow dissector fields and exact masks.

Control flow: Rule translation walks expressions, fills match keys/masks and actions, tracks network/transport dependencies, and commits supported flow rules to devices. Datapath stats can be synchronized back to nft expressions.

State and persistence: Offload context is per-translation; generated `flow_rule` objects live until destroyed or chain updates commit.

Dependencies/integration: Depends on `flow_offload.h`, `nf_tables.h`, flow dissector key layouts, base-chain offload support, and device flow block operations.

Risks/test signals: Validate register-to-field offsets, action count bounds, dependency updates before payload matches, mask initialization, unsupported expression rejection, and stats sync. Test IPv4/IPv6/VLAN/Ethernet matches and rule replacement rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_tables_offload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_tproxy.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_tproxy.h

Purpose: Declares transparent proxy socket selection, assignment, and TIME_WAIT handling helpers for IPv4 and IPv6 interception.

Important APIs/types/functions: `enum nf_tproxy_lookup_t`, `nf_tproxy_sk_is_transparent`, `nf_tproxy_twsk_deschedule_put`, `nf_tproxy_assign_sock`, `nf_tproxy_laddr4`, `nf_tproxy_handle_time_wait4`, `nf_tproxy_get_sock_v4`, `nf_tproxy_laddr6`, `nf_tproxy_handle_time_wait6`, and `nf_tproxy_get_sock_v6`.

Control flow: TPROXY rules search for established or listener sockets using packet and redirect tuples. Transparent sockets are retained; non-transparent sockets are dropped with `sock_gen_put`. TIME_WAIT sockets may be replaced by listener sockets for new SYNs. Once selected, `nf_tproxy_assign_sock` orphans the skb and installs the socket with `sock_edemux`.

State and persistence: Uses existing socket/timewait state and consumes socket references. No independent persistent state.

Dependencies/integration: Depends on TCP/UDP sockets, inet transparency flags, skbuff ownership, bottom-half safe timewait descheduling, IPv4/IPv6 address handling, and nft/xt tproxy rules.

Risks/test signals: Reference ownership is the main risk. Test established vs listener preference, TIME_WAIT SYN reopen, non-transparent listeners, wildcard binds, IPv6, local-address override, skb destructor behavior, and l3mdev/namespace scoping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_tproxy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nft_fib.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nft_fib.h

Purpose: Defines common nftables FIB expression state and helpers for route/interface lookup based matching.

Important APIs/types/functions: `struct nft_fib` stores destination register, result selector, and flags. APIs include `nft_fib_dump`, `nft_fib_init`, `nft_fib_validate`, IPv4/IPv6 type/eval functions, `nft_fib_store_result`, and helpers `nft_fib_is_loopback`, `nft_fib_can_skip`, and `nft_fib_l3mdev_master_ifindex_rcu`.

Control flow: Init validates netlink attributes; eval functions perform family-specific FIB lookups and store requested result into nft registers. `nft_fib_can_skip` short-circuits lookup in inbound hooks when socket cached route/loopback proves the input device.

State and persistence: Expression-private state is embedded in nft rules. Runtime lookup reads route/device/socket state but stores no persistent data.

Dependencies/integration: Depends on `nf_tables.h`, l3mdev master lookup, netdevice flags, socket fullsock state, and IPv4/IPv6 route lookup implementations.

Risks/test signals: Test loopback skips, socket route cache correctness, VRF/l3mdev master indexes, result register length, invalid hook use, IPv4/IPv6 parity, and route changes during evaluation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nft_fib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nft_meta.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nft_meta.h

Purpose: Declares nftables meta expression state and operations for reading and setting packet, socket, interface, cgroup, mark, priority, and related metadata.

Important APIs/types/functions: `struct nft_meta` stores key, data length, and source/destination register. APIs include get/set init, dump, eval, destroy, validate, and `nft_meta_inner_eval` for inner tunnel context.

Control flow: Netlink init validates the selected meta key and register direction. Datapath eval reads metadata into registers or writes from registers to mutable skb fields. Set validation prevents illegal writes in unsupported hooks or contexts.

State and persistence: Expression-private state is in rules. Writes modify per-packet skb metadata or referenced packet context; no independent persistence.

Dependencies/integration: Depends on `nf_tables.h`, uapi meta keys, skb fields, socket/device/cgroup metadata, and inner tunnel payload context from nft core.

Risks/test signals: Test register lengths, set-only vs get-only keys, mutable metadata in each hook, inner packet evaluation, namespace-sensitive device ids, cgroup/socket edge cases, and dump/init round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nft_meta.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nft_reject.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nft_reject.h

Purpose: Provides common nftables reject expression state, validation, init, dump, and ICMP code validation helpers.

Important APIs/types/functions: `struct nft_reject` stores reject type and ICMP code. APIs are `nft_reject_validate`, `nft_reject_init`, `nft_reject_dump`, `nft_reject_icmp_code`, and `nft_reject_icmpv6_code`; `nft_reject_policy` defines netlink attribute validation.

Control flow: Init parses reject type/code from netlink, validate enforces hook/family constraints, family-specific eval code later generates TCP reset or ICMP/ICMPv6 rejects using this state.

State and persistence: Expression-private immutable state embedded in nft rules.

Dependencies/integration: Depends on netlink policies, nftables expression lifecycle, uapi reject types, and family-specific reject implementations.

Risks/test signals: Test invalid ICMP/ICMPv6 codes, TCP reset in unsupported contexts, bridge/inet family interactions, dump round-trip, and malformed netlink attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nft_reject.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/xt_rateest.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/xt_rateest.h

Purpose: Defines shared state for xtables rate estimator targets/matches.

Important APIs/types/functions: `struct xt_rateest` contains synchronized basic stats, a spinlock, refcount, hlist node, estimator name, `gnet_estimator` parameters, RCU head, and RCU pointer to `net_rate_estimator`. APIs are `xt_rateest_lookup` and `xt_rateest_put`.

Control flow: The target updates `bstats` under the cache-local lock; matches read the estimator pointer positioned away from hot update data. Lookup returns a named estimator with a reference; put releases it.

State and persistence: Runtime per-net estimator objects are refcounted and RCU-freed. No durable persistence.

Dependencies/integration: Depends on generic net stats/estimators, xtables match/target modules, RCU, spinlocks, and net namespace lookup.

Risks/test signals: Test refcount under concurrent rule replacement, RCU estimator updates, name lookup isolation by namespace, stats update/read races, and module unload with active matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/xt_rateest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netkit.h -->
# sources/distributed-fs/ceph-client/include/net/netkit.h

Purpose: Declares BPF attach/detach/query interfaces for Netkit devices and a peer-device helper.

Important APIs/types/functions: With `CONFIG_NETKIT`, APIs are `netkit_prog_attach`, `netkit_link_attach`, `netkit_prog_detach`, `netkit_prog_query`, and indirect-callable `netkit_peer_dev`. Without Netkit, stubs return `-EINVAL` or `NULL`.

Control flow: BPF syscall paths call attach/link/detach/query functions using `union bpf_attr` and `bpf_prog`. Device-facing code can resolve a peer device through the indirect-callable helper.

State and persistence: Actual attachment and link state lives in Netkit implementation and BPF link/prog objects. Header stubs hold no state.

Dependencies/integration: Depends on Linux BPF types, netdevice internals, indirect-call declarations, and `CONFIG_NETKIT`.

Risks/test signals: Test disabled-config stubs, BPF program/link lifecycle, query correctness, peer-device lifetime, and indirect call target registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netkit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netlabel.h -->
# sources/distributed-fs/ceph-client/include/net/netlabel.h

Purpose: Defines the NetLabel kernel API used by LSMs and protocol engines to manage network security labels, domain mappings, CIPSO/CALIPSO DOI configuration, packet/socket label attributes, and caches.

Important APIs/types/functions: Key types are `netlbl_audit`, `netlbl_lsm_cache`, `netlbl_lsm_catmap`, `netlbl_lsm_secattr`, and `netlbl_calipso_ops`. Inline helpers allocate/free/init/destroy secattr caches and sparse category maps. Under `CONFIG_NETLABEL`, APIs configure domain/static/CIPSO/CALIPSO maps, manipulate category maps and bitmaps, set/get/delete labels on sockets, request sockets, connections, and skbs, report skb label errors, check socket locking, invalidate/add caches, start audits, and register CALIPSO operations. Disabled stubs return `-ENOSYS`, neutral values, or no-ops.

Control flow: LSMs build `netlbl_lsm_secattr`, configure mappings through NetLabel generic netlink management, then set labels on sockets or packets. Incoming packets are decoded by protocol engines into secattrs and optionally cached. CALIPSO operations are indirect so IPv6 labeling can be modular.

State and persistence: Mapping tables, DOI definitions, caches, and LSM secattr cache references are runtime kernel state. Secattr structures carry ownership flags for domain/cache/category memory.

Dependencies/integration: Depends on generic netlink, skbuff/socket/request_sock, audit, LSM properties, CIPSO/CALIPSO engines, refcounting, and network namespaces.

Risks/test signals: Watch ownership flags (`FREE_DOMAIN`, `CACHE`, `MLS_CAT`), sparse category map range handling, disabled stub signatures, cache refcount/free callbacks, and socket lock expectations. Test SELinux/Smack labeling, CIPSO/CALIPSO add/remove/map, IPv4/IPv6 skb set/get, cache invalidation, malformed netlink management messages, and module registration/unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netlabel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netlink.h -->
# sources/distributed-fs/ceph-client/include/net/netlink.h

Purpose: Provides the core in-kernel netlink message and attribute construction, parsing, validation, iteration, typed access, nesting, multicast/unicast, and policy-dump interfaces.

Important APIs/types/functions: It defines `nla_policy`, range validation structs, `nl_info`, validation modes, and many policy macros (`NLA_POLICY_*`). Message helpers cover size/alignment, data/payload/attr access, `nlmsg_ok/next`, strict/deprecated parsing and validation, find/report/seq, construction (`nlmsg_put`, `nlmsg_append`, `nlmsg_new`, `nlmsg_new_large`, `nlmsg_end/cancel/free/consume`), multicast/unicast, dump consistency, and message iteration. Attribute helpers cover size/alignment, `nla_type/data/len/ok/next`, strict/deprecated nested parsing/validation, typed put/get for integer/endian/string/flag/msecs/IP/bitfield attributes, memdup, nesting start/end/cancel, 64-bit alignment, iteration macros, range extraction, and policy dumping.

Control flow: Kernel families build replies by allocating skbs, placing netlink headers, appending attributes, ending or canceling on error, and sending unicast/multicast. Receive paths validate messages with a selected strictness level, parse attributes into type-indexed arrays, and use typed getters. Dump paths track sequence consistency and can expose policies to userspace.

State and persistence: Mostly stateless inline helpers; mutable state is in skbs, netlink callbacks, extack reporting, and optional policy dump state allocated by implementation functions.

Dependencies/integration: Used by rtnetlink, generic netlink, nfnetlink/nftables, NetLabel, XFRM, and many networking subsystems. Depends on skbuff, netlink sockets, jiffies, extended ACK, alignment rules, and uapi netlink flags.

Risks/test signals: High-risk areas are strict vs deprecated validation compatibility, `strict_start_type`, nested `NLA_F_NESTED` enforcement, 64-bit alignment padding, U16 nested length overflow, variable-sized signed/unsigned attributes, and malformed/trailing data. Test attribute fuzzing, policy round trips, old userspace compatibility, extack messages, dump interruption flagging, multicast error normalization, and architectures without efficient unaligned access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netmem.h -->
# sources/distributed-fs/ceph-client/include/net/netmem.h

Purpose: Introduces `netmem_ref`, an abstract networking memory reference that can represent either a normal `struct page` or a non-page `struct net_iov` memory-provider chunk, while exposing common page-pool fields.

Important APIs/types/functions: `netmem_desc` mirrors page-pool fields in `struct page`; `net_iov` and `net_iov_area` represent slab-allocated network I/O chunks from providers such as dmabuf or io_uring. Helpers include owner/index/init, page/iov/netmem conversions, refcount/PFN/address/PFMemalloc queries, page-pool descriptor access, DMA address access, devmem type check, `get_netmem`, `put_netmem`, DMA unmap address macro, and `netmem_dma_unmap_page_attrs`.

Control flow: Page-pool and networking code carry `netmem_ref`; the low bit distinguishes net_iov from page pointers. Helpers branch to page or provider-specific logic for references, DMA, NUMA, addressability, and page-pool fields. Unsafe helpers are available for page-only hot paths.

State and persistence: Runtime memory descriptors track page-pool pointer, DMA address, and page-pool refcount. Static assertions enforce layout aliasing with `struct page`.

Dependencies/integration: Depends on page_pool field layout, DMA mapping, mm page APIs, static keys for memory providers, debug warnings, and provider implementations for `__get_netmem/__put_netmem`.

Risks/test signals: Layout drift is critical. Test static assertions, low-bit pointer tagging assumptions, unsafe helper misuse on net_iovs, refcount symmetry, DMA unmap suppression for provider memory, address queries returning NULL for iovs, and provider-enabled/disabled configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/bpf.h -->
# sources/distributed-fs/ceph-client/include/net/netns/bpf.h

Purpose: Defines per-network-namespace BPF attachment storage for namespace-scoped networking programs.

Important APIs/types/functions: `enum netns_bpf_attach_type` currently covers flow dissector and socket lookup attachment types. `struct netns_bpf` stores RCU `run_array` pointers, direct `progs`, and link lists per attach type.

Control flow: BPF attach/link operations update program arrays and link lists for a net namespace. Packet or socket lookup paths read `run_array` under RCU to execute programs.

State and persistence: Per-net runtime state only; program arrays and links must be RCU-safe and cleaned during namespace teardown.

Dependencies/integration: Depends on BPF program arrays, BPF links, RCU, flow dissector, and SK_LOOKUP hooks.

Risks/test signals: Test attach/detach/query, RCU replacement, namespace destruction with links, invalid attach type rejection, flow dissector behavior, and socket lookup program ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/can.h -->
# sources/distributed-fs/ceph-client/include/net/netns/can.h

Purpose: Defines per-network-namespace Controller Area Network state.

Important APIs/types/functions: `struct netns_can` holds procfs entries, all-device receive filter lists, receive-list lock, statistics timer, package/list stats, and CAN gateway job list.

Control flow: CAN core initializes per-net receive lists and stats, receive paths consult `rx_alldev_list` under `rcvlists_lock`, stats timer updates counters, and gateway code tracks jobs in `cgw_list`.

State and persistence: Runtime per-net state with timers, locks, hlist/list nodes, and optional procfs dentries. It must be torn down before namespace release.

Dependencies/integration: Depends on CAN core receive lists, procfs, timers, spinlocks, CAN BCM proc entries, and CAN gateway.

Risks/test signals: Test namespace create/destroy, procfs entry cleanup, concurrent filter updates, stats timer shutdown, gateway job cleanup, and all-device receive filter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/can.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/conntrack.h -->
# sources/distributed-fs/ceph-client/include/net/netns/conntrack.h

Purpose: Defines per-network-namespace conntrack protocol timeout/configuration state and conntrack subsystem controls.

Important APIs/types/functions: Protocol structs include `nf_generic_net`, `nf_tcp_net`, `nf_udp_net`, `nf_icmp_net`, optional `nf_sctp_net`, and optional `nf_gre_net`. `nf_ip_net` groups per-protocol settings. `struct netns_ct` stores event/work flags, sysctl booleans, per-cpu stats, event notifier RCU pointer, protocol config, and optional label usage count.

Control flow: Conntrack initialization fills timeouts and sysctls per namespace; packet tracking consults protocol-specific arrays; sysctl writes update behavior; event delivery reads `nf_conntrack_event_cb`; flowtable uses offload timeouts when enabled.

State and persistence: Runtime per-net state, including per-cpu stats and RCU notifier pointer. No durable persistence.

Dependencies/integration: Depends on nf_conntrack protocol definitions, TCP/SCTP/GRE config options, seqlocks/list_nulls/workqueues, labels, events, sysctl, and flowtable.

Risks/test signals: Test timeout sysctls per namespace, notifier RCU teardown, label counter, event work pending flag, flowtable offload timeout config, and protocol config option combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/conntrack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/core.h -->
# sources/distributed-fs/ceph-client/include/net/netns/core.h

Purpose: Defines core networking sysctl and accounting fields stored per network namespace.

Important APIs/types/functions: `struct netns_core` stores sysctl header, socket/backlog/memory/tx hash knobs, procfs protocol in-use counters, and optional RPS default CPU mask.

Control flow: Namespace init registers sysctls and allocates optional proc/RPS fields. Core socket and networking code reads these knobs on hot paths.

State and persistence: Runtime per-net sysctl state and optional per-cpu/proc data.

Dependencies/integration: Depends on sysctl, procfs, protocol in-use accounting, cpumasks, RPS, and socket core.

Risks/test signals: Test sysctl defaults/isolation, procfs cleanup, RPS mask lifetime, hot-path cache effects, and namespace teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/flow_table.h -->
# sources/distributed-fs/ceph-client/include/net/netns/flow_table.h

Purpose: Defines per-net flowtable statistics storage.

Important APIs/types/functions: `struct nf_flow_table_stat` has counters for workqueue add, delete, and stats operations. `struct netns_ft` points to a per-cpu stat block.

Control flow: Flowtable offload code increments these counters through macros in `nf_flow_table.h`; procfs/stat readers aggregate them.

State and persistence: Runtime per-cpu counters scoped to a network namespace.

Dependencies/integration: Depends on nf flowtable, per-cpu allocation, optional procfs stats, and namespace lifecycle.

Risks/test signals: Test allocation failure paths, stat increments under concurrency, procfs output, and cleanup on netns exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/flow_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/generic.h -->
# sources/distributed-fs/ceph-client/include/net/netns/generic.h

Purpose: Defines the generic per-net pointer array used by modules to attach private per-namespace data without modifying `struct net`.

Important APIs/types/functions: `struct net_generic` stores a length/RCU header or flexible pointer array. `net_generic(const struct net *net, unsigned int id)` RCU-dereferences `net->gen` and returns `ptr[id]`.

Control flow: Per-net operations with `id` and `size` cause the core to allocate private data and store it in the generic array. Subsystems call `net_generic` to retrieve it.

State and persistence: Runtime per-net pointer array protected by RCU. The header documents that pointers must not be changed while the net namespace is alive and callers must not take private references to the net_generic object itself.

Dependencies/integration: Depends on net namespace core, pernet operations, RCU, and modules needing private netns state such as nftables and synproxy.

Risks/test signals: Test id allocation, array growth under RCU, namespace teardown, invalid id access, and modules obeying lifetime rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/hash.h -->
# sources/distributed-fs/ceph-client/include/net/netns/hash.h

Purpose: Stores per-network-namespace hash seeds for networking hash functions.

Important APIs/types/functions: `struct netns_hash` contains a single `u32 mix` value.

Control flow: Namespace setup initializes `mix`; hashing code combines it with tuple or object data to avoid shared global hash behavior across namespaces.

State and persistence: Runtime per-net randomization state.

Dependencies/integration: Depends on net namespace initialization and consumers that need per-net hash salt.

Risks/test signals: Test seed initialization, namespace isolation, deterministic behavior only where expected, and no zero/uninitialized use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/ieee802154_6lowpan.h -->
# sources/distributed-fs/ceph-client/include/net/netns/ieee802154_6lowpan.h

Purpose: Defines per-net namespace state for IEEE 802.15.4 6LoWPAN fragmentation/reassembly.

Important APIs/types/functions: `struct netns_ieee802154_lowpan` stores a fragment queue directory pointer `fqdir`.

Control flow: 6LoWPAN receive paths use `fqdir` for fragment queueing and reassembly within a namespace.

State and persistence: Runtime fragment queue directory state, cleaned during namespace teardown.

Dependencies/integration: Depends on inet fragment infrastructure and IEEE 802.15.4 6LoWPAN code.

Risks/test signals: Test reassembly under namespace isolation, queue timeout cleanup, memory pressure behavior, and teardown with outstanding fragments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/ieee802154_6lowpan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/ipv4.h -->
# sources/distributed-fs/ceph-client/include/net/netns/ipv4.h

Purpose: Defines the large per-network-namespace IPv4 state block, including hot-path TCP/IP sysctls, routing/FIB data, fragment/peer state, multicast routing, ICMP/IGMP controls, local port ranges, and address generation state.

Important APIs/types/functions: Supporting structs include `local_ports`, `ping_group_range`, `inet_timewait_death_row`, optional multipath hash seed, and `udp_tunnel_gro`. `struct netns_ipv4` stores cacheline-grouped TCP/IP sysctls, ICMP limiter state, TCP death row, UDP table, GRO tunnel sockets, sysctl headers, device configs, router-alert chain, FIB rules/tables/hash/info state, multicast routing state, notifier ops, route generation ids, siphash key, address lists, and delayed address checking work.

Control flow: IPv4/TCP/UDP routing and protocol paths read these per-net fields. Sysctl writes update behavior. FIB and multicast routing code mutate tables under their locks. Address and route changes bump generation counters and schedule delayed work.

State and persistence: Runtime per-net state only, but it is long-lived for the namespace. Several fields are hot-path cacheline organized and protected by atomic, mutex, spinlock, RCU, or seqlock mechanisms.

Dependencies/integration: Depends on TCP/UDP, FIB/routing, inet fragments, peers, sysctl/proc, multicast routing, l3mdev, multipath, notifier, address configuration, and siphash.

Risks/test signals: Test cacheline-sensitive field changes, sysctl isolation, route generation invalidation, FIB notifier sequencing, multicast table cleanup, local port range reserved-port behavior, timewait limits, UDP tunnel GRO availability, and namespace teardown with delayed work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/ipv4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/ipv6.h -->
# sources/distributed-fs/ceph-client/include/net/netns/ipv6.h

Purpose: Defines per-network-namespace IPv6 sysctl, routing, neighbor/control socket, address label, multicast routing, Segment Routing, IOAM, and optional defrag state.

Important APIs/types/functions: `struct netns_sysctl_ipv6` stores route/ICMP/fragment/xfrm sysctl headers and IPv6 behavior knobs. `struct netns_ipv6` stores `ip6_dst_ops`, device configs, peer/fqdir pointers, null entries, route stats/timers/tables/walkers/locks, fib rule state, control sockets, address hash/list state, multicast route tables, generation counters, Segment Routing and IOAM pernet data, notifier ops, address label table, and flowlabel counters. `struct netns_nf_frag` stores IPv6 netfilter defrag fqdir when enabled.

Control flow: IPv6 protocol and route paths consult sysctls and route tables, timers drive fib GC, address config uses delayed work, and control sockets serve NDISC/TCP/IGMP-like functionality.

State and persistence: Runtime per-net state protected by spinlocks, rwlocks, atomics, timers, and delayed work. No durable storage.

Dependencies/integration: Depends on IPv6 route/dst ops, sysctl, fragments, fib rules, multicast routing, addrconf, Segment Routing, IOAM, notifiers, and optional netfilter defrag.

Risks/test signals: Test route GC timers, sysctl isolation, address hash locking, fib6 generation counters, multicast route cleanup, flowlabel controls, defrag fqdir cleanup, IPv6 disabled/optional configs, and namespace teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/ipv6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/mctp.h -->
# sources/distributed-fs/ceph-client/include/net/netns/mctp.h

Purpose: Defines per-network-namespace state for MCTP routing, addressing, keys, and sockets.

Important APIs/types/functions: `MCTP_BINDS_BITS` sizes the bound-socket hash. `struct netns_mctp` contains an RCU-freed route list updated under RTNL, `bind_lock`, a `(type, src_eid, dest_eid)` socket bind hash table, `keys_lock` and key hlist for tag allocations, `default_net`, `neigh_lock`, and a neighbours list. `mctp_bind_hash` hashes bind triples with `hash_32`.

Control flow: MCTP route management updates the route list under RTNL while receive paths read routes through RCU. Socket bind/unbind updates the bind hash under `bind_lock`; packet receive can read bind entries under RCU. Tag keys are manipulated in atomic contexts under `keys_lock` and freed after an RCU grace period. Neighbour updates use `neigh_lock`.

State and persistence: Runtime per-net routes, bind hash buckets, tag keys, default network id, and neighbour list. No durable persistence; RCU protects readers and delayed frees.

Dependencies/integration: Depends on MCTP core routing, address management, socket layer, and namespace lifecycle.

Risks/test signals: Test bind hash collisions and wildcard `MCTP_ADDR_ANY` entries, route removal while packets are received, atomic-context key allocation/free, neighbour cleanup, namespace isolation, and default-net behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/mctp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/mib.h -->
# sources/distributed-fs/ceph-client/include/net/netns/mib.h

Purpose: Defines per-network-namespace SNMP/MIB statistics pointers for core IP, ICMP, TCP, UDP, and Linux-specific networking counters.

Important APIs/types/functions: `struct netns_mib` contains per-cpu stat pointers such as IP, IPv6, ICMP, ICMPv6, TCP, UDP, UDPLite, Linux MIB, and IPv6 fragment stats depending on config.

Control flow: Protocol paths increment per-cpu counters through MIB macros; procfs/netlink stats readers aggregate them.

State and persistence: Runtime per-net per-cpu counters, allocated during namespace initialization and freed on teardown.

Dependencies/integration: Depends on SNMP stat definitions, protocol config options, procfs/stat readers, and per-cpu allocation.

Risks/test signals: Test allocation/cleanup for config matrices, counter increments under concurrency, namespace isolation in `/proc/net/snmp*`, and disabled protocol configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/mib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/mpls.h -->
# sources/distributed-fs/ceph-client/include/net/netns/mpls.h

Purpose: Defines per-network-namespace MPLS routing and platform-label state.

Important APIs/types/functions: `struct netns_mpls` stores `ip_ttl_propagate`, `default_ttl`, `platform_labels`, an RCU pointer array of RCU `mpls_route` pointers, `platform_mutex`, `platform_label_seq`, and sysctl header `ctl`.

Control flow: MPLS route lookup uses the per-net platform-label table indexed by label under RCU/sequence protection. Configuration changes take `platform_mutex`, update the table and sequence counter, and sysctls adjust TTL propagation/default TTL.

State and persistence: Runtime per-net MPLS route tables and sysctl state.

Dependencies/integration: Depends on MPLS routing, sysctl, net namespace lifecycle, and route table allocation.

Risks/test signals: Test platform label resize with concurrent lookup, sequence counter retry behavior, route table cleanup, TTL sysctl changes, namespace isolation, and disabled MPLS builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/mpls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/netfilter.h -->
# sources/distributed-fs/ceph-client/include/net/netns/netfilter.h

Purpose: Defines per-network-namespace core netfilter state, including logger bindings, hook entry arrays by protocol family, sysctl/proc entries, and defragmentation users.

Important APIs/types/functions: `struct netns_nf` stores optional `proc_netfilter`, RCU `nf_loggers[NFPROTO_NUMPROTO]`, sysctl headers for logging and lwtunnel hooks, RCU hook arrays for IPv4/IPv6 and optional ARP/bridge families, plus IPv4/IPv6 defrag user counters when enabled.

Control flow: Netfilter hook registration updates the relevant family/hook RCU array; packet traversal reads hook entries under RCU. Logging paths pick per-net protocol-family loggers. Sysctl/proc expose logging and lwtunnel hook controls. Defrag modules increment/decrement per-net users.

State and persistence: Runtime per-net hook arrays, logger pointers, proc/sysctl headers, and defrag counters. No durable persistence; RCU and namespace teardown ordering are central.

Dependencies/integration: Depends on netfilter core, nfnetlink, logging, queueing, bridge netfilter, procfs/sysctl, and namespace teardown ordering.

Risks/test signals: Test hook registration/unregistration races, namespace-specific logger binding, ARP/bridge config matrices, lwtunnel sysctl registration, defrag user reference counts, proc/sysctl cleanup, and packet traversal during hook-array replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/netfilter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/nexthop.h -->
# sources/distributed-fs/ceph-client/include/net/netns/nexthop.h

Purpose: Defines per-network-namespace nexthop object table state.

Important APIs/types/functions: `struct netns_nexthop` stores an RB tree of nexthops by id, a device hash for nexthops by device, RTNL-protected sequence number `seq`, `last_id_allocated`, and a blocking notifier chain.

Control flow: Nexthop create/lookup/replace/delete operations update the RB tree and device hash under routing locks. Route code observes sequence changes and notifier events when nexthop objects change.

State and persistence: Runtime per-net nexthop index, device hash, last allocated id, sequence counter, and notifier subscribers.

Dependencies/integration: Depends on fib/nexthop core, notifier chains, route lookup, and namespace lifecycle.

Risks/test signals: Test id allocation wrap/duplicates, RB tree and devhash consistency, object replacement under route references, notifier ordering, sequence increments under RTNL, and namespace cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/nexthop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/nftables.h -->
# sources/distributed-fs/ceph-client/include/net/netns/nftables.h

Purpose: Defines the compact nftables fields embedded directly in `struct net`.

Important APIs/types/functions: `struct netns_nftables` stores `base_seq`, used to sequence base-chain hook updates, and `gencursor`, the two-generation cursor used by nftables generation masks.

Control flow: nftables control-plane commits flip or consult `gencursor` to stage current/next generation activity; hook update code uses `base_seq` to coordinate base-chain changes.

State and persistence: Runtime per-net scalar state. Full ruleset lists and transactions live in generic pernet data described in `nf_tables.h`.

Dependencies/integration: Depends on nftables core, generic pernet handling, netfilter hooks, and netlink control paths.

Risks/test signals: Test generation cursor flipping during atomic commit/abort, base sequence updates during base-chain replacement, per-net initialization defaults, and namespace isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/nftables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/packet.h -->
# sources/distributed-fs/ceph-client/include/net/netns/packet.h

Purpose: Defines per-network-namespace AF_PACKET state.

Important APIs/types/functions: `struct netns_packet` stores the packet socket list and associated synchronization state.

Control flow: AF_PACKET socket create/destroy updates the namespace list; packet delivery enumerates matching packet sockets.

State and persistence: Runtime per-net socket list, protected by packet socket locking/RCU in implementation code.

Dependencies/integration: Depends on AF_PACKET, netdevice receive path, socket lifecycle, and namespace teardown.

Risks/test signals: Test packet socket creation/destruction under traffic, namespace isolation, device unregister cleanup, fanout interactions, and teardown with open sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/packet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/sctp.h -->
# sources/distributed-fs/ceph-client/include/net/netns/sctp.h

Purpose: Defines per-network-namespace SCTP state, statistics, sockets, address lists, timers, and extensive protocol sysctl defaults.

Important APIs/types/functions: `struct netns_sctp` includes SNMP stats, proc/sysctl headers, control socket, UDP tunnel sockets/ports, local address lists and wait queues, address timers/locks, auto-ASCONF list, and many protocol parameters: RTO, burst, cookies, SACK, heartbeat, PLPMTUD, retransmission limits, failover, accounting policies, addip/auth/reconfig/interleave/ECN flags, scope policy, receive-window update threshold, autoclose, and optional l3mdev accept.

Control flow: SCTP init creates control/tunnel sockets and fills defaults. Address notifier paths update lists under locks and timers. Protocol operations read namespace parameters for association behavior, retransmission, auth, encapsulation, and accounting.

State and persistence: Runtime per-net state with timers, sockets, locks, lists, and stats. Sysctls change values during namespace lifetime.

Dependencies/integration: Depends on SCTP core, SNMP stats, procfs/sysctl, UDP tunneling, timers, socket layer, address notification, and l3mdev.

Risks/test signals: Test namespace teardown with timers/sockets, UDP encapsulation ports, address add/delete races, sysctl validation, failover policies, auth/addip/reconfig flags, and stats accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/sctp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/smc.h -->
# sources/distributed-fs/ceph-client/include/net/netns/smc.h

Purpose: Defines per-network-namespace SMC protocol state.

Important APIs/types/functions: `struct netns_smc` stores per-cpu SMC stats, `mutex_fback_rsn`, fallback reason stats, `limit_smc_hs`, optional sysctl header, optional BPF handshake-control pointer, and sysctls for autocorking, buffer type, testlink time, send/receive memory, max links/connections per link group, and SMCR send/receive work requests.

Control flow: SMC init allocates stats and sysctls. Protocol paths update per-cpu stats, protect fallback reason updates with the mutex, consult handshake limits/BPF control, and read namespace sysctls for link group and buffer behavior.

State and persistence: Runtime per-net stats, fallback reason state, handshake-control pointer, and sysctl values.

Dependencies/integration: Depends on SMC core, sysctl/proc integration, socket lifecycle, and namespace teardown.

Risks/test signals: Test per-net sysctls, fallback reason locking, BPF handshake control RCU lifetime, stats cleanup, handshake limit enforcement, disabled config behavior, and namespace isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/smc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/unix.h -->
# sources/distributed-fs/ceph-client/include/net/netns/unix.h

Purpose: Defines per-network-namespace AF_UNIX state.

Important APIs/types/functions: `struct unix_table` stores spinlock and bucket arrays. `struct netns_unix` embeds the table, `sysctl_max_dgram_qlen`, and sysctl header `ctl`.

Control flow: AF_UNIX bind/connect/listen paths hash sockets into namespace-local buckets protected by bucket locks. Sysctl controls datagram queue length, and cleanup/proc paths consult the same table.

State and persistence: Runtime per-net UNIX socket hash table and datagram queue sysctl.

Dependencies/integration: Depends on AF_UNIX socket core, procfs, namespace lifecycle, and socket garbage collection.

Risks/test signals: Test abstract namespace isolation, hash bucket lock allocation/cleanup, datagram queue sysctl, garbage collection across namespaces, and bind collisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/unix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/vsock.h -->
# sources/distributed-fs/ceph-client/include/net/netns/vsock.h

Purpose: Defines per-network-namespace VSOCK state.

Important APIs/types/functions: `enum vsock_net_mode` distinguishes global and local modes. `struct netns_vsock` stores sysctl header, protected local port, current mode, child namespace mode, child-mode lock state, and guest-to-host fallback flag.

Control flow: VSOCK sysctls and namespace creation choose global/local mode behavior. Port allocation reads/updates `port` under the global vsock table lock. Child namespace mode and fallback controls affect transport selection.

State and persistence: Runtime per-net mode and port allocation controls.

Dependencies/integration: Depends on VSOCK core, transport modules, socket lifecycle, and namespace cleanup.

Risks/test signals: Test global vs local mode transitions, child namespace mode locking, port allocation under concurrent sockets, guest-to-host fallback behavior, sysctl cleanup, and namespace isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/vsock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/xdp.h -->
# sources/distributed-fs/ceph-client/include/net/netns/xdp.h

Purpose: Defines per-network-namespace XDP state.

Important APIs/types/functions: `struct netns_xdp` stores a mutex and hlist of namespace-scoped XDP resources.

Control flow: XDP resource creation/removal takes the namespace mutex and updates the hlist; lookup/enumeration consults the list for namespace-scoped XDP objects.

State and persistence: Runtime per-net mutex-protected hlist state only.

Dependencies/integration: Depends on XDP sockets/core, netdevice receive path, namespace lifecycle, and optional memory accounting.

Risks/test signals: Test concurrent list updates, XSK bind/unbind across namespaces, teardown with active sockets, device unregister, and cleanup of all hlist entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/xdp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/xfrm.h -->
# sources/distributed-fs/ceph-client/include/net/netns/xfrm.h

Purpose: Defines per-network-namespace IPsec/XFRM state and policy databases.

Important APIs/types/functions: `xfrm_policy_hash` and `xfrm_policy_hthresh` describe policy hash tables and threshold updates. `struct netns_xfrm` stores all state lists, state hash tables by destination/source/SPI/sequence, per-cpu input cache, hash masks/counts/work, policy lists/index hashes/destination hashes/counts/work, inexact bins, netlink socket pointers, sysctls, default policies, dst ops, locks, generation seqcounts, config mutex, and NAT keepalive work.

Control flow: XFRM state/policy add/delete/lookup paths mutate protected tables and generation counters. Netlink operations use namespace netlink sockets and config mutex. Hash resize work updates state/policy tables. Packet paths consult state caches and policy hashes.

State and persistence: Runtime per-net security association and policy state. Protected by spinlocks, mutex, seqcount, RCU, workqueues, and delayed work.

Dependencies/integration: Depends on XFRM core/uapi, dst ops, netlink, workqueues, rhashtable/list infrastructure, IPv6 optional dst ops, sysctl, and NAT keepalive.

Risks/test signals: Test concurrent SA/policy add/delete/lookup, hash resize, generation seqcount readers, netlink socket teardown, namespace cleanup with delayed work, default policy sysctls, IPv6 config, and NAT keepalive cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netns/xfrm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netprio_cgroup.h -->
# sources/distributed-fs/ceph-client/include/net/netprio_cgroup.h

Purpose: Provides cgroup net priority helpers for mapping tasks to socket priority indexes.

Important APIs/types/functions: With `CONFIG_CGROUP_NET_PRIO`, `struct netprio_map` stores RCU-freeable priority maps. `task_netprioidx` reads the task's net_prio css id under RCU, and `sock_update_netprioidx` copies the current task priority index into socket cgroup data unless in interrupt context. Without the feature, helpers return zero or no-op.

Control flow: Socket creation/update paths call `sock_update_netprioidx`; it reads the current task cgroup and updates socket cgroup metadata. Packet scheduling/classification can later use the priority index.

State and persistence: Runtime cgroup ids and RCU priority maps; no state is stored in this header.

Dependencies/integration: Depends on cgroup subsystem state, socket cgroup data, RCU, hardirq context checks, and net_prio cgroup config.

Risks/test signals: Test disabled stubs, RCU correctness, interrupt-context no-op, socket priority inheritance after task migration, cgroup deletion, and classifier/qdisc behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netprio_cgroup.h -->
